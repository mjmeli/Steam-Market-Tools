# Steam Market Tools
A collection of tools used to analyze the Steam market.

Please excuse the fragmented repos for now, I am working on getting everything combined.

### Retrieve Skin Names

This project will create a json file representing every weapon skin available on the Steam CSGO market. It will contain every weapon, it's associated skins, and the available conditions for that skin.

NOTE: Does not include StatTrak™ weapons at the moment.

Example:

    {
        "name": "AK-47",
        "skins": [
            {
                "name": "Vulcan",
                "conditions": [
                    "Battle-Scarred",
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
                    "Field-Tested"
                ]
            },
            ...
        ]
        ...
    }

### Credits

Lead Software Developer - Michael Meli (mjmeli)
Lead Project Manager - Derek Whatley (djwhatle)
