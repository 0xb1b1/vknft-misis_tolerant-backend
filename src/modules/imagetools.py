class ImageTools:
    def __init__(self, url):
        self.url = url if url[-1] == "/" else url + "/"

    def upload(self, image: bytes) -> str:
        """Uploads image to self.url and returns a link"""
        pass  #! TODO: implement
        return "None"
