from io import BytesIO
from PIL import Image


def generate_image_file() -> BytesIO:
    file = BytesIO()
    image = Image.new("RGBA", size=(1000, 1000), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test.png"
    file.seek(0)
    return file
