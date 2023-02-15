import os
import json
import re
import cv2
from image_downloading import download_image

from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
from PIL import Image

import rasterio
from rasterio.warp import transform_bounds
import yaml
import time

from glob import glob

start_time = time.time()

incorrect_total = 0


def get_corners(image_file: str, zoom=19):
    sat_data = rasterio.open(image_file)
    xmin, ymin, xmax, ymax = transform_bounds(sat_data.crs, 4326, *sat_data.bounds)
    return f'{ymax}, {xmin}', f'{ymin} {xmax}', str(zoom)


file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, 'preferences.json')
default_prefs = {
    'url': 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    'tile_size': 256,
    'tile_format': 'jpg',
    'dir': os.path.join(file_dir, 'images'),
    'headers': {
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    },
    'tl': '',
    'br': '',
    'zoom': ''
}


def take_input(messages):
    inputs = []
    print('Enter "r" to reset or "q" to exit.')
    for message in messages:
        inp = input(message)
        if inp == 'q' or inp == 'Q':
            return None
        if inp == 'r' or inp == 'R':
            return take_input(messages)
        inputs.append(inp)
    return inputs


def run(prefs_add: dict):
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    prefs['tl'], prefs['br'], prefs['zoom'] = prefs_add['tl'], prefs_add['br'], prefs_add['zoom']
    lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['tl'])
    lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['br'])

    zoom = int(prefs['zoom'])
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    if prefs['tile_format'].lower() == 'png':
        channels = 4
    else:
        channels = 3

    img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
                         prefs['headers'], prefs['tile_size'], channels)

    name = prefs_add['image_name']

    cv2.imwrite(name, cv2.resize(img, (prefs_add['width_to'], prefs_add['height_to']), interpolation=cv2.INTER_AREA))
    print(f'Saved as {name}')


def tif_to_arr(tif_path):
    im = Image.open(tif_path)
    imarray = np.array(im)
    return imarray


def plot_heatmap_array(tif):
    if type(tif) == str:
        array = tif_to_arr(tif)
    else:
        array = tif
    plt.figure(figsize=(15, 10))
    sns.heatmap(array)
    plt.show()


def clear_image(tif_path: str, write_path='', rewrite=False):
    imarray = tif_to_arr(tif_path)

    c1 = imarray.copy()
    real_min = np.unique(c1)[2]

    c2 = c1.copy()
    c2 = c2[c2 >= real_min]
    real_mean = np.mean(c2)

    c1[c1 < real_min] = real_mean
    ended = c1 - real_min

    if write_path:
        if not rewrite:
            write_path += '_fixed.tif'
        Image.fromarray(ended).save(write_path)
        print(f'Fixed image: {write_path}')

    return ended


with open('config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

if os.path.isfile(prefs_path):

    tif_dir = cfg['tif_dir']

    files = glob(tif_dir + '/*', recursive=True)

    for tif_dir in files:
        try:
            filename = tif_dir + '/' + tif_dir.split('/')[-1] + '.tif'

            prefs_add = {}
            prefs_add['cutsom_dir'] = tif_dir
            prefs_add['tl'], prefs_add['br'], prefs_add['zoom'] = get_corners(filename)
            clear_image(filename, write_path=filename, rewrite=True)
            prefs_add['image_name'] = filename + '.jpg'

            img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)

            prefs_add['height_to'] = img.shape[0]
            prefs_add['width_to'] = img.shape[1]

            run(prefs_add)
        except Exception as E:
            incorrect_total += 1
else:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(default_prefs, f, indent=2, ensure_ascii=False)

    print(f'Preferences file created in {prefs_path}')

print("--- %s seconds ---" % (time.time() - start_time))
print('Incorrect runs: ', incorrect_total)
