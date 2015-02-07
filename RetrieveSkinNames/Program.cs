using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;
using Newtonsoft.Json;

namespace RetrieveSkinNames
{
    class Program
    {
        static void Main(string[] args)
        {
            // get weapon names from text file
            Console.WriteLine("Getting weapon names from file...");
            WeaponCollection weapons = new WeaponCollection();
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
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();

            sw.Start();
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
            sw.Stop();
            Console.Write("\r{0} of {1}   ", count, count);
            Console.WriteLine(sw.ElapsedMilliseconds + "\n");

            // serialize to json
            Console.WriteLine("Serializing to JSON...");
            using (System.IO.StreamWriter file = new System.IO.StreamWriter("WeaponsAndSkins.json"))
            {
                JsonSerializer jsonSerializer = new JsonSerializer();
                jsonSerializer.Serialize(file, weapons);
            }
            Console.WriteLine("Done.\n");

            // upload to database
            using (System.Net.WebClient client = new System.Net.WebClient())
            {
                client.UploadData("", "PUT");
            }

            Console.WriteLine("Complete, press ENTER to exit.");
            Console.ReadLine();
        }
    }
}
