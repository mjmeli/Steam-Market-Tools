using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.Serialization;

namespace RetrieveSkinNames
{
    [Serializable]
    class WeaponCollection : List<Weapon>, ISerializable
    {
        // Custom serialization
        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("weapons", this);
        }
    }
}
