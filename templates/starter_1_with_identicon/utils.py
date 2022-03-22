import os
from flask import current_app
from PIL import Image

libpath, _conf_ = os.path.split(os.path.realpath(__file__))
#rootpath = os.path.join(libpath,'..') #up one dir
rootpath = libpath[:-libpath[::-1].find(os.path.sep)] #behold, magic! jk

def resize_image(img, base_width):
    '''resize an image'''
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
    return img

def crop_image(img_path, formd, base_width=500):
        x = int(float(formd.get('x')))
        y = int(float(formd.get('y')))
        w = int(float(formd.get('w')))
        h = int(float(formd.get('h')))

        raw_img = Image.open(img_path)
        if raw_img.size[0] >= base_width:
            raw_img = resize_image(raw_img, base_width=base_width)
        return raw_img.crop((x, y, x + w, y + h))
