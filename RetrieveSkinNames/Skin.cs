using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.Serialization;

namespace RetrieveSkinNames
{
    [Serializable]
    class Skin : ISerializable
    {
        private const string BASE_URL = "http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=730&market_hash_name=";
        private static string[] POSSIBLE_CONDITIONS = { "Battle-Scarred", "Well-Worn", "Field-Tested", "Minimal Wear", "Factory New" };
        private const int FAIL_LENGTH = 20;

        private String name;
        private List<String> conditions;

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
        public List<String> Conditions
        {
            get
            {
                return conditions;
            }
        }

        public Skin(String name)
        {
            this.name = name;
            this.conditions = new List<string>();
        }

        /// <summary>
        /// Check the possible conditions for this skin and see which ones actually exist in the market.
        /// </summary>
        /// <param name="w">Weapon for which this skin belongs</param>
        public void GetConditions(Weapon w)
        {
            // check each possible condition
            List<Task> tasks = new List<Task>(POSSIBLE_CONDITIONS.Length);
            foreach (String str in POSSIBLE_CONDITIONS)
            {
                String testURL = BASE_URL + w.Name.Replace(" ","%20") + "%20%7C%20" + this.name.Replace(" ","%20") + "%20%28" + str.Replace(" ","%20") + "%29";
                tasks.Add(new Task(() => CheckCondition(testURL, str)));
            }
            foreach (Task t in tasks)
            {
                t.Start();
            }
            Task.WaitAll(tasks.ToArray());
        }

        /// <summary>
        /// Private helper method used to check if a skin exists
        /// </summary>
        /// <param name="url">URL to test against</param>
        /// <param name="cond">Condition being tested</param>
        private void CheckCondition(string url, string cond)
        {
            if (cond == null)
            {
                throw new Exception("Condition string can not be null! URL: " + url);
            }

            using (System.Net.WebClient client = new System.Net.WebClient())
            {
                // check if this exists
                try
                {
                    string htmlCode = client.DownloadString(url);
                    if (htmlCode.Length > FAIL_LENGTH)
                    {
                        conditions.Add(cond);
                    }                
                }
                catch (Exception)
                {
                    // if the weapon condition does not exist, exception is thrown, so ignore
                }
            }
        }

        // Serialize data
        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("name", this.name, typeof(string));
            info.AddValue("conditions", conditions);
        }
    }
}
