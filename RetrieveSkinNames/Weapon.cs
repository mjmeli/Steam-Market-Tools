using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RetrieveSkinNames
{
    class Weapon
    {
        private String name;
        private List<String> skins;

        /// <summary>
        /// Weapon name
        /// </summary>
        public String Name { get; set; }
        
        /// <summary>
        /// List of the names of skins for this weapon
        /// </summary>
        private List<String> Skins { get; set; }

        /// <summary>
        /// Create a new weapon object.
        /// </summary>
        /// <param name="name">Name of the weapon</param>
        public Weapon(String name)
        {
            this.name = name;
            this.skins = new List<String>();
        }
    }
}
