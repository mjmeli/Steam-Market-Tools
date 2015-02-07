﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;
using Newtonsoft.Json;
using System.Net;

namespace RetrieveSkinNames
{
    class Program
    {
        static void Main(string[] args)
        {
            // get weapon names from text file
            Console.WriteLine("Getting weapon names from file...");
            WeaponCollection weaponCollection = new WeaponCollection();
            List<Weapon> weapons = weaponCollection.Weapons;
            String line;
            using (System.IO.StreamReader file = new System.IO.StreamReader("WeaponList.txt"))
            {
                while ((line = file.ReadLine()) != null)
                {
                    weapons.Add(new Weapon(line));
                }
            }
            Console.WriteLine("Done.\n");
                       
            // get skin names for each weapon
            Console.WriteLine("Getting skin names for each weapon...");
            int count = 0;
            foreach (Weapon w in weapons)
            {
                w.GetSkinNames();
                count += w.Skins.Count;
            }
            Console.WriteLine(count + " skins found.\n");

            // get conditions for each skin
            int i = 0;
            Console.WriteLine("Checking available conditions for each skin...");
            foreach (Weapon w in weapons)
            {
                foreach (Skin s in w.Skins)
                {
                    s.GetConditions(w);

                    // progress
                    i++;
                    Console.Write("\r{0} of {1}   ", i, count);
                }
            }
            Console.Write("\r{0} of {1}   ", count, count);

            // serialize to json
            Console.WriteLine("Serializing to JSON...");
            using (System.IO.StreamWriter file = new System.IO.StreamWriter("WeaponsAndSkins.json"))
            {
                JsonSerializer jsonSerializer = new JsonSerializer();
                jsonSerializer.Serialize(file, weaponCollection);
            }
            Console.WriteLine("Done.\n");

            // upload to database
            using (System.Net.WebClient client = new System.Net.WebClient())
            {
                String connString = "";
                XmlDocument xml = new XmlDocument();
                try
                {
                    String host, port, username, password;
                    xml.Load("config.xml");
                    XmlNode node = xml.DocumentElement.SelectSingleNode("/configuration/dbCredentials");
                    host = node.SelectSingleNode("host").InnerText;
                    port = node.SelectSingleNode("port").InnerText;
                    username = node.SelectSingleNode("username").InnerText;
                    password = node.SelectSingleNode("password").InnerText;

                    connString = "http://" + host + ":" + port + "/";
                    
                    using (System.IO.StreamReader file = new System.IO.StreamReader("WeaponsAndSkins.json"))
                    {
                        // compile credentials
                        String json = file.ReadToEnd();
                        string creds = Convert.ToBase64String(Encoding.ASCII.GetBytes(username + ":" + password));
                        client.Headers[HttpRequestHeader.Authorization] = string.Format("Basic {0}", creds);

                        // check database exists
                        try
                        {
                            byte[] response = client.UploadData(connString + "tracked_steam_item_names/", "PUT", System.Text.Encoding.UTF8.GetBytes(""));
                            Console.WriteLine(System.Text.Encoding.UTF8.GetString(response));
                        }
                        catch (Exception)
                        {
                            Console.WriteLine("Ignored exception");
                        }

                        // get uuid
                        String uuidJson = System.Text.Encoding.UTF8.GetString(client.DownloadData(connString + "_uuids"));
                        var dsJson = JsonConvert.DeserializeObject<dynamic>(uuidJson);
                        String uuid = dsJson.uuids[0];

                        // push json
                        try
                        {
                            byte[] response = client.UploadData(connString + "tracked_steam_item_names/" + uuid, "PUT", System.Text.Encoding.UTF8.GetBytes(json));
                            Console.WriteLine(System.Text.Encoding.UTF8.GetString(response));
                        }
                        catch (Exception ex)
                        {
                            throw ex;
                        }
                    }
                }
                catch (System.IO.FileNotFoundException)
                {
                    Console.WriteLine("No config.xml file found. Ignoring database integration.");
                }
            }

            Console.WriteLine("Complete, press ENTER to exit.");
            Console.ReadLine();
        }
    }
}
