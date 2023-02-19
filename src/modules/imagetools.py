import requests as r
import json

class ImageTools:
    def __init__(self, url):
        self.url = url if url[-1] == "/" else url + "/"

    def upload(self, image: bytes) -> str:
        """Uploads image to self.url and returns a link"""
        endpoint = self.url + "api/upload.php"
        # POST file to endpoint
        response = r.post(endpoint, files={"file": image})
        return json.loads(response.text)["url"]
