import requests
from jsonrpcclient import request, parse, Ok
base_endpoint = "https://alpha-sleek-general.solana-devnet.discover.quiknode.pro/b511198243861757412f978f597d03eb715ce6a5/"
chain = "solana"
async def create_collection(name: str, description: str, img_url: str):
    metadata = {
        "name": name,
        "description": description,
        "imageUrl": img_url
    }
    response = requests.post(base_endpoint,json=request("cm_createCollection", [chain, metadata]))
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        return parsed.result # returns the collection id and other data
    else:
        print(parsed.message)
        return None

async def mint_nft(collection_id: str, name: str, description: str, img_url: str, wallet_addr: str, attributes: dict):
    atrs = []
    for key in attributes:
        atrs.append({"trait_type": key, "value": attributes[key]})
    
    nft_config = {
        "name": name,
        "description": description,
        "image": img_url,
        "attributes": atrs
    }
    response = requests.post(base_endpoint,json=request("cm_mintNFT", [collection_id, wallet_addr,  nft_config]))
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        return parsed.result # returns the nft id and other data
    else:
        print(parsed.message)
        return None

async def check_minting_status(nft_id: str, collection_id:str):
    response = requests.post(base_endpoint, json=request("cm_getNFTMintStatus", [collection_id, nft_id]))
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        return parsed.result
    else:
        print(parsed.message)
        return None

async def get_all_nfts(wallet_addr: str):
    response = requests.post(base_endpoint, json=request("qn_fetchNFTs", [wallet_addr]))
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        return parsed.result
    else:
        print(parsed.message)
        return None
