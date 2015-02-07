using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using HtmlAgilityPack;
using System.Runtime.Serialization;

namespace RetrieveSkinNames
{
    [Serializable]
    class Weapon : ISerializable
    {
        private String name;
        private HashSet<Skin> skins;

        /// <summary>
        /// Weapon name
        /// </summary>
        public String Name {
            get
            {
                return name;
            }
            set
            {
                name = value;
            }
        }
        
        /// <summary>
        /// List of the names of skins for this weapon
        /// </summary>
        public HashSet<Skin> Skins {
            get
            {
                return skins;
            }
            set
            {
                skins = value;
            }
        }

        /// <summary>
        /// Create a new weapon object.
        /// </summary>
        /// <param name="name">Name of the weapon</param>
        public Weapon(String name)
        {
            this.name = name;
            this.skins = new HashSet<Skin>();
        }

        /// <summary>
        /// Populates skin list with list of skins.
        /// </summary>
        public void GetSkinNames()
        {
            // compile URL
            string URL = "http://csgostash.com/weapon/" + this.name.Replace(" ", "+");

            // get HTML
            HtmlDocument html = new HtmlDocument();
            using (System.Net.WebClient client = new System.Net.WebClient())
            {
                string htmlCode = client.DownloadString(URL);
                if (htmlCode != null)
                {
                    html.LoadHtml(htmlCode);
                }
                else
                {
                    throw new Exception("Could not load HTML from URL: " + URL);
                }
            }

            // extract skin names
            foreach (HtmlNode node in html.DocumentNode.SelectNodes("//h3//a"))
            {
                if (!node.InnerText.Equals(""))
                {
                    skins.Add(new Skin(node.InnerText));
                }
            }
        }

        // Serialize data
        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("name", this.name, typeof(string));
            info.AddValue("skins", skins);
        }
    }
}
