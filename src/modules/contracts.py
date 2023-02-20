import requests
from jsonrpcclient import request, parse, Ok

base_endpoint = "https://alpha-sleek-general.solana-devnet.discover.quiknode.pro/b511198243861757412f978f597d03eb715ce6a5/"
chain = "solana"


class SmartContracts:
    def __init__(self, log):
        self.log = log

    async def create_collection(self, name: str, description: str, img_url: str):
        """creates a collection via the Quiknode API"""
        metadata = {"name": name, "description": description, "imageUrl": img_url}

        response = requests.post(
            base_endpoint, json=request("cm_createCollection", [chain, metadata])
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            return parsed.result  # Returns the collection id and other data
        else:
            return {"error": parsed}


    async def mint_nft(
        self,
        collection_id: str,
        name: str,
        description: str,
        img_url: str,
        wallet_addr: str,
        attributes: dict,
    ):
        """Mints an NFT via the Quiknode API"""
        atrs = []
        for key in attributes:
            atrs.append({"trait_type": key, "value": attributes[key]})

        nft_config = {
            "name": name,
            "description": description,
            "image": img_url,
            "attributes": atrs,
        }
        addr = f"solana:{wallet_addr}"
        response = requests.post(
            base_endpoint,
            json=request("cm_mintNFT", [collection_id, addr, nft_config]),
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            return parsed.result  # returns the nft id and other data
        else:
            return {"error": parsed}


    def check_minting_status(self, nft_id: str, collection_id: str) -> dict:
        """Checks the minting status of an NFT via the Quiknode API"""
        response = requests.post(
            base_endpoint, json=request("cm_getNFTMintStatus", [collection_id, nft_id])
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            return parsed.result
        else:
            return {"error": parsed}


    async def get_all_nfts(self, wallet_addr: str):
        """Gets all NFTs owned by a wallet via the Quiknode API"""
        response = requests.post(base_endpoint, json=request("qn_fetchNFTs", [wallet_addr]))
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            return parsed.result
        else:
            return {"error": parsed}
