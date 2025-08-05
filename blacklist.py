# blacklist.py

def is_blacklisted(asset_input):
    blacklist = [
        "0x000000000000000000000000000000000000dead",
        "0x1111111111111111111111111111111111111111",
        "scamnft.eth",
        "rugtoken.xyz",
    ]
    return asset_input.lower() in [item.lower() for item in blacklist]
