import requests
from jsonrpcclient.responses import parse, Ok
from jsonrpcclient.requests import request


class SmartContracts:
    def __init__(self, log, endpoint_secret: str, chain: str = "solana"):
        self.log = log
        self.base_endpoint = f"https://alpha-sleek-general.solana-devnet.discover.quiknode.pro/{endpoint_secret}/"
        self.chain = chain

    async def create_collection(self, name: str, description: str, img_url: str):
        """creates a collection via the Quiknode API"""
        metadata = {"name": name, "description": description, "imageUrl": img_url}

        response = requests.post(
            self.base_endpoint, json=request("cm_createCollection", [self.chain, metadata])
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            self.log.debug(f"SmartContracts create_collection result: {parsed.result}")
            return parsed.result  # Returns the collection id and other data
        else:
            self.log.debug(f"SmartContracts create_collection result (error): {parsed}")
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
        attrs = []
        for key in attributes:
            attrs.append({"trait_type": key, "value": attributes[key]})

        self.log.debug(f"SmartContracts mint_nft attrs: {attrs}")

        nft_config = {
            "name": name,
            "description": description,
            "image": img_url,
            "attributes": attrs,
        }
        self.log.debug(f"SmartContracts mint_nft nft_config: {nft_config}")
        addr = f"solana:{wallet_addr}"
        self.log.debug(f"SmartContracts mint_nft addr: {addr}")
        response = requests.post(
            self.base_endpoint,
            json=request("cm_mintNFT", [collection_id, addr, nft_config]),
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            self.log.debug(f"SmartContracts mint_nft result: {parsed.result}")
            return parsed.result  # returns the nft id and other data
        else:
            self.log.debug(f"SmartContracts mint_nft result (error): {parsed}")
            return {"error": parsed}


    def check_minting_status(self, nft_id: str, collection_id: str) -> dict:
        """Checks the minting status of an NFT via the Quiknode API"""
        response = requests.post(
            self.base_endpoint, json=request("cm_getNFTMintStatus", [collection_id, nft_id])
        )
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            self.log.debug(f"SmartContracts check_minting_status result: {parsed.result}")
            return parsed.result
        else:
            self.log.debug(f"SmartContracts check_minting_status result (error): {parsed}")
            return {"error": parsed}


    async def get_all_nfts(self, wallet_addr: str):
        """Gets all NFTs owned by a wallet via the Quiknode API"""
        response = requests.post(self.base_endpoint, json=request("qn_fetchNFTs", [wallet_addr]))
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            self.log.debug(f"SmartContracts get_all_nfts result: {parsed.result}")
            return parsed.result
        else:
            self.log.debug(f"SmartContracts get_all_nfts result (error): {parsed}")
            return {"error": parsed}
