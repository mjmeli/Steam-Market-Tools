using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.Serialization;

namespace RetrieveSkinNames
{
    [Serializable]
    class WeaponCollection : ISerializable
    {
        private List<Weapon> weapons;
        private DateTime dt;
        public String _rev = "";



        public DateTime DateTime
        {
          get { return dt; }
          set { dt = value; }
        }

        public List<Weapon> Weapons
        {
            get { return weapons; }
            set { weapons = value; }
        }

        public WeaponCollection()
        {
            this.weapons = new List<Weapon>();
            dt = DateTime.Now;
        }

        // Custom serialization
        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("datetime", dt, typeof(DateTime));
            info.AddValue("weapons", weapons);
            if (!String.IsNullOrWhiteSpace(_rev))
            {
                info.AddValue("_rev", _rev);
            }
        }
    }
}
