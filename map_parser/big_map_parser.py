
from PIL import Image as PILImage
import numpy as np


def map_parse():
    with open('bigmap.png', 'rb') as img_handle:
        img = PILImage.open(img_handle)
        img = img.convert('RGB')
        img_data = np.array(img.getdata())
        print(img.getpixel((2,1)))
        print(np.all(np.equal(img_data,np.tile([153, 204, 255],)),axis=1))


map_parse()
