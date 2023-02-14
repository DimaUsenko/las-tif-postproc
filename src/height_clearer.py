import numpy as np
# import seaborn as sns
from PIL import Image


def clear_image(tif_path: str):
    im = Image.open(tif_path)
    imarray = np.array(im)

    c1 = imarray.copy()
    real_min = np.unique(c1)[2]

    c2 = c1.copy()
    c2 = c2[c2 >= real_min]
    real_mean = np.mean(c2)

    c1[c1 < real_min] = real_mean
    ended = c1 - real_min
    return ended
