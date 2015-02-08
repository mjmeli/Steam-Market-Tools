# Steam Market Tools
A collection of tools used to analyze the Steam market.

Please excuse the fragmented repos for now, I am working on getting everything combined.

### Retrieve Skin Names

This project will create a json file representing every weapon skin available on the Steam CSGO market. It will contain every weapon, it's associated skins, and the available conditions for that skin.

The program is written with our application of putting the data into a CouchDB database. This is configured by an config.xml file that is not included in this repo. You can try to figure it out, or simply not include it and everything should still work.

NOTE: Does not include StatTrak™ weapons at the moment.

Example:

    {
        "weapons": [
            ...
            {
                "name": "AK-47",
                "skins": [
                    {
                        "name": "Vulcan",
                        "conditions": [
                            "Battle-Scarred",
                            "Well-Worn",
                            "Factory New",
                            "Minimal Wear",
                            "Field-Tested"
                        ]
                    },
                    {
                        "name": "Redline",
                        "conditions": [
                            "Battle-Scarred",
                            "Minimal Wear",
                            "Well-Worn",
                            "Field-Tested"
                        ]
                    },
                    ...
                ]
                ...
            }
            ...
        ]
    }

### Credits

Lead Software Developer - Michael Meli (mjmeli)

Lead Project Architect - Derek Whatley (djwhatle)

Subject Matter Consultant - Nick Kandl
