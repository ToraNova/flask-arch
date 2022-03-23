import math
import random
import hashlib
import os
from flask import current_app
from PIL import Image, ImageDraw
from io import BytesIO

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

class Identicon(object):
    '''
    ported from https://github.com/greyli/flask-avatars/blob/master/flask_avatars/identicon.py
    removed reliance on the current_app object to allow instantiation before app runs
    '''

    def __init__(self, rows=7, cols=7, bg_color=(255, 255, 255)):

        """Generate identicon image.
        :param rows: The row of pixels in avatar.
        :param columns: The column of pixels in avatar.
        :param bg_color: Backgroud color, pass RGB tuple, for example: (125, 125, 125).
               Set it to ``None`` to use random color.
        """

        self.rows = rows
        self.cols = cols
        self.bg_colour = bg_color
        self._generate_colours()

        m = hashlib.md5()
        m.update(b"hello world")
        entropy = len(m.hexdigest()) / 2 * 8
        if self.rows > 15 or self.cols > 15:
            raise ValueError("Rows and columns must be valued 15 or under")

        self.digest = hashlib.md5
        self.digest_entropy = entropy

    def _generate_colours(self):
        colours_ok = False

        while colours_ok is False:
            self.fg_colour = self._get_pastel_colour()

            if self.bg_colour is None:
                self.bg_colour = self._get_pastel_colour(lighten=80)

                # Get the luminance for each colour
                fg_lum = self._luminance(self.fg_colour) + 0.05
                bg_lum = self._luminance(self.bg_colour) + 0.05

                # Check the difference in luminance
                # meets the 1.25 threshold
                result = (fg_lum / bg_lum) \
                    if (fg_lum / bg_lum) else (bg_lum / fg_lum)
                if result > 1.20:
                    colours_ok = True
            else:
                colours_ok = True

    def get_image(self, string, width, height, pad=0):
        """
          Byte representation of a PNG image
        """
        hex_digest_byte_list = self._string_to_byte_list(string)
        matrix = self._create_matrix(hex_digest_byte_list)
        return self._create_image(matrix, width, height, pad)

    def _get_pastel_colour(self, lighten=127):
        """
            Create a pastel colour hex colour string
        """
        def r():
            return random.randint(0, 128) + lighten
        return r(), r(), r()  # return rgb values as a tuple

    def _luminance(self, rgb):
        """
        Determine the liminanace of an RGB colour
        """
        a = []
        for v in rgb:
            v = v / float(255)
            if v < 0.03928:
                result = v / 12.92
            else:
                result = math.pow(((v + 0.055) / 1.055), 2.4)

            a.append(result)
        return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722

    def _string_to_byte_list(self, data):
        """
        Creates a hex digest of the input string given to create the image,
        if it's not already hexadecimal
        Returns:
            Length 16 list of rgb value range integers
            (each representing a byte of the hex digest)
        """
        bytes_length = 16

        m = self.digest()
        m.update(str.encode(data))
        hex_digest = m.hexdigest()

        return list(int(hex_digest[num * 2:num * 2 + 2], bytes_length)
                    for num in range(bytes_length))

    def _bit_is_one(self, n, hash_bytes):
        """
        Check if the n (index) of hash_bytes is 1 or 0.
        """

        scale = 16  # hexadecimal

        if not hash_bytes[int(n / (scale / 2))] >> int(
                (scale / 2) - ((n % (scale / 2)) + 1)) & 1 == 1:
            return False
        return True

    def _create_image(self, matrix, width, height, pad):
        """
        Generates a PNG byte list
        """

        image = Image.new("RGB", (width + (pad * 2),
                                  height + (pad * 2)), self.bg_colour)
        image_draw = ImageDraw.Draw(image)

        # Calculate the block width and height.
        block_width = float(width) / self.cols
        block_height = float(height) / self.rows

        # Loop through blocks in matrix, draw rectangles.
        for row, cols in enumerate(matrix):
            for col, cell in enumerate(cols):
                if cell:
                    image_draw.rectangle((
                        pad + col * block_width,  # x1
                        pad + row * block_height,  # y1
                        pad + (col + 1) * block_width - 1,  # x2
                        pad + (row + 1) * block_height - 1  # y2
                    ), fill=self.fg_colour)

        stream = BytesIO()
        image.save(stream, format="png", optimize=True)
        # return the image byte data
        return stream.getvalue()

    def _create_matrix(self, byte_list):
        """
        This matrix decides which blocks should be filled fg/bg colour
        True for fg_colour
        False for bg_colour
        hash_bytes - array of hash bytes values. RGB range values in each slot
        Returns:
            List representation of the matrix
            [[True, True, True, True],
            [False, True, True, False],
            [True, True, True, True],
            [False, False, False, False]]
        """

        # Number of rows * cols halfed and rounded
        # in order to fill opposite side
        cells = int(self.rows * self.cols / 2 + self.cols % 2)

        matrix = [[False] * self.cols for num in range(self.rows)]

        for cell_number in range(cells):

            # If the bit with index corresponding to this cell is 1
            # mark that cell as fg_colour
            # Skip byte 1, that's used in determining fg_colour
            if self._bit_is_one(cell_number, byte_list[1:]):
                # Find cell coordinates in matrix.
                x_row = cell_number % self.rows
                y_col = int(cell_number / self.cols)
                # Set coord True and its opposite side
                matrix[x_row][self.cols - y_col - 1] = True
                matrix[x_row][y_col] = True
        return matrix

identicon = Identicon(7, 7, (255, 255, 255))
