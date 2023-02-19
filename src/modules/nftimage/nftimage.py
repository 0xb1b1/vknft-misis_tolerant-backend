import os
from io import BytesIO
from Crypto.Cipher import AES
from PIL import Image, ImageFilter, ImageFont, ImageDraw, ImageEnhance, ImageOps

class NFTImage:
    def __init__(self):
        self.fonts = {
            'regular': 'fonts/Roboto-Regular.ttf',
            'medium': 'fonts/Roboto-Medium.ttf',
            'bold': 'fonts/Roboto-Bold.ttf',
            'black': 'fonts/Roboto-Black.ttf'
        }
        self.lock_font = 'bold'
        self.lock_img = 'assets/lock.png'

    def resize(self, image, size: tuple = (1000, 1000)):
        # If the image is not a square, add padding
        # Do not crop or stretch/compress the image
        image = Image.open(BytesIO(image)).convert('RGBA')
        w, h = image.size
        # Get the biggest dimension
        max_dim = max(w, h)
        # Create a new image with the biggest dimension
        outimg = Image.new('RGBA', (max_dim, max_dim), (0, 119, 255, 255))
        # Paste the original image in the new image without stretching/compressing
        outimg.paste(image, ((max_dim - w) // 2, (max_dim - h) // 2))

        # Resize the image by x and y
        outimg = outimg.resize(size)

        img_bytes = BytesIO()
        outimg.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

    def watermark(self, image,
                  text: str = "Доступно только\nдля пользователей VK NFT",
                  font: ImageFont = None, font_size: int = 20):
        if not font:
            font = ImageFont.truetype(self.fonts[self.lock_font], size=font_size)
        image = Image.open(BytesIO(image))

        # Get lock image
        lock_img = Image.open(self.lock_img)
        # Resize lock image
        lock_resize_factor = 0.3
        lock_img = lock_img.resize((int(lock_img.width * lock_resize_factor),
                                    int(lock_img.height * lock_resize_factor)))
        # Get width and height of lock image
        lock_w, lock_h = lock_img.size
        lock_offset = lock_h // 3

        # Get width and height of image
        W, H = image.size
        # Get width and height of text
        draw = ImageDraw.Draw(image)
        _, _, w, h = draw.textbbox((0, 0), text, font=font)

        # Paste lock image in the middle of the image
        image.paste(lock_img,
                    ((W-lock_w)//2,
                     (H-lock_h)//2),
                    lock_img)

        # Write text on image
        draw.text(((W-w)/2, (H-h)/2 +
                   (lock_h + lock_offset)),
                  text,
                  font=font,
                  align='center',
                  spacing=12,
                  fill='white')

        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    def blur(self, image, radius: int = 20):
        image = Image.open(BytesIO(image))
        image = image.filter(ImageFilter.GaussianBlur(radius=radius))
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    def darken(self, image, factor: int = 2):
        '''Make image darker'''
        image = Image.open(BytesIO(image))
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.5)
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    def encrypt(self, file: bytes, key: str):
        file = BytesIO(file)
        # 16-byte random initialization vector
        iv = os.urandom(16)

        # Pad the password to a multiple of 16 bytes
        key = key.ljust(16, '\0')

        # Create the AES cipher object with 128-bit key
        cipher = AES.new(bytes(key, 'utf-8'), AES.MODE_CBC, iv)

        # Write the initialization vector to the output
        output = iv

        chunk_size = 16
        while True:
            # Use an alternative to read() that returns bytes
            chunk = file.read(chunk_size)
            if len(chunk) == 0:
                break
            elif len(chunk) % chunk_size != 0:
                chunk += b'\0' * (chunk_size - len(chunk) % chunk_size)
            encrypted_chunk = cipher.encrypt(chunk)
            output += (encrypted_chunk)
        return output

    def decrypt(self, file, key: str):
        file = BytesIO(file)
        # Read the initialization vector from the input
        iv = file.read(16)

        # Pad the password to a multiple of 16 bytes
        key = key.ljust(16, '\0')

        # Create the AES cipher object with 128-bit key
        cipher = AES.new(bytes(key, 'utf-8'), AES.MODE_CBC, iv)

        # Read the encrypted data
        chunk_size = 16
        output = b''
        while True:
            chunk = file.read(chunk_size)
            if len(chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(chunk)
            output += decrypted_chunk
        return output
