from inky.auto import auto
from PIL import Image


def push_to_display(image_path):
    inky = auto()
    img = Image.open(image_path).convert("RGB")
    img = img.resize((inky.width, inky.height))
    inky.set_image(img, saturation=0.5)
    inky.show()
