#!/usr/bin/env python

import epd2in13b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
import random
import os
import buttonshim
import csv

COLORED = 1
UNCOLORED = 0
FONT_PATH = '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'

class EBadge(object):

    def __init__(self, image_path, slogan_path):
        super(EBadge, self).__init__()
        self.epd = epd2in13b.EPD()
        self.epd.init()
        self.pause = False
        self.interval = 5

        # store color
        self.red = 0
        self.green = 0
        self.blue = 0

        # paths
        self.image_path = image_path
        self.slogan_path = slogan_path

    def hit_pause(self):
        if self.pause:
            self.pause = False
            self.red = 0
            self.green = 0
            self.blue = 0
        else:
            self.pause = True
            self.red = 255
            self.green = 0
            self.blue = 0

        buttonshim.set_pixel(self.red, self.green, self.blue)

    def increase_interval(self):
        # set pixel to blue
        buttonshim.set_pixel(0, 0, 255)
        self.interval += 5
        if self.interval > 30:
            self.interval = 30

    def decrease_interval(self):
        # set pixel to blue
        buttonshim.set_pixel(0, 0, 255)

        self.interval -= 5
        if self.interval < 5:
            self.interval = 5

    def get_buffer(self):
        # clear the frame buffer
        frame_black = [0xFF] * (self.epd.width * self.epd.height // 8)
        frame_red = [0xFF] * (self.epd.width * self.epd.height // 8)

        return frame_black, frame_red

    def get_x_pos(self, font, text):
        text_length = sum(font.getsize(x)[0] for x in text)
        return self.epd.width // 2 - text_length // 2

    def get_scaled_font(self, text, width, text_max=32, text_min=8):
        for x in range(text_max, text_min, -1):
            text_length = sum(ImageFont.truetype(FONT_PATH, x).getsize(x) for x in text)
            if text_length < width:
                return ImageFont.truetype(FONT_PATH, x)

        return ImageFont.truetype(FONT_PATH, text_min)

    def border(self, text, scale=True, centered=True):
        frame_black, frame_red = self.get_buffer()
        self.epd.draw_filled_rectangle(frame_black, 0, 0, self.epd.width, self.epd.height, COLORED)
        for x in range(4, 9):
            self.epd.draw_rectangle(frame_red, x, x, self.epd.width - x, self.epd.height - x, COLORED)

        # get font
        font = self.get_scaled_font(text, self.epd.width) if scale else ImageFont.truetype(FONT_PATH, 32)

        # write text
        start_x = 12 if centered else self.get_x_pos(font, text) + 4
        start_y = self.epd.height // 2 - font.getsize("a")[1] // 2
        self.epd.draw_string_at(frame_red, start_x, start_y, text, font, COLORED)
        self.epd.display_frame(frame_black, frame_red)

    def hello(self, text, scale=True, centered=True):
        frame_black, frame_red = self.get_buffer()
        font = ImageFont.truetype(FONT_PATH, 24)
        self.epd.draw_filled_rectangle(frame_red, 0, 0, self.epd.width, self.epd.height // 2, COLORED)
        self.epd.draw_string_at(frame_red, 12, 12, "Hello My Name Is", font, UNCOLORED)

        # get font
        font = self.get_scaled_font(text, self.epd.width) if scale else ImageFont.truetype(FONT_PATH, 32)

        # write actual text
        start_x = 8 if centered else self.get_x_pos(font, text)
        start_y = self.epd.height * 0.66
        self.epd.draw_string_at(frame_black, start_x, start_y, text, font, COLORED)

        # draw frames
        self.epd.display_frame(frame_black, frame_red)

    def image(self, image, color="black", background="white"):
        frame_black, frame_red = self.get_buffer()
        self.epd.draw_filled_rectangle(frame_black, 0, 0, self.epd.width, self.epd.height, COLORED)
        frame_black = self.epd.get_frame_buffer(Image.open(image))
        self.epd.display_frame(frame_black, frame_red)

    def choose_style(self):
        choices = ["border", "hello"]
        return random.choice(choices)

    def choose_text(self):
        choices = []
        with open(self.slogan_path) as fh:
            for line in fh:
                # treat lines that start with # as comments
                if line[0] == "#":
                    continue

                data = [x.strip() for x in line.strip().split("\t")]
                choices.append(data)
        return random.choice(choices)

    def choose_image(self):
        choices = os.listdir(self.image_path)
        return os.path.join(self.image_path, random.choice(choices))

    def random_image(self):
        image = self.choose_image()
        self.image(image)

    def get_scaled(self, text):
        if text == "scale":
            return True
        elif text == "any":
            return random.choice((True, False))
        else:
            return False

    def get_centered(self, text):
        if text == "center":
            return True
        elif text == "any":
            return random.choice((True, False))
        else:
            return False

    def hit_random_image(self):
        buttonshim.set_pixel(0, 255, 0)
        self.random_image()

    def random_text(self):
        style = self.choose_style()
        text = self.choose_text()
        if style == "border":
            if len(text) >= 3:
                self.border(text[0], self.get_scaled(text[1]), self.get_centered(text[2]))
        elif style == "hello":
            if len(text) >= 3:
                self.hello(text[0], self.get_scaled(text[1]), self.get_centered(text[2]))

    def hit_random_text(self):
        buttonshim.set_pixel(0, 255, 0)
        self.random_text()

    def smile_or_text(self):
        if random.choice(("image", "text", "text", "text", "image", "text")) == "image":
            self.random_image()
        else:
            self.random_text()

    def loop(self):
        buttonshim.set_pixel(self.red, self.green, self.blue)
        if not self.pause:
            self.random_text()
            time.sleep(self.interval)
        else:
            time.sleep(0.01)


def main():
    badge = EBadge("/var/badge/images/", "/var/badge/slogans.txt")

    @buttonshim.on_press(buttonshim.BUTTON_A)
    def button_a(button, pressed):
        badge.hit_pause()

    @buttonshim.on_press(buttonshim.BUTTON_B)
    def button_b(button, pressed):
        badge.hit_random_text()

    @buttonshim.on_press(buttonshim.BUTTON_C)
    def button_c(button, pressed):
        badge.hit_random_image()

    @buttonshim.on_press(buttonshim.BUTTON_D)
    def button_d(button, pressed):
        badge.increase_interval()

    @buttonshim.on_press(buttonshim.BUTTON_E)
    def button_e(button, pressed):
        badge.decrease_interval()

    while True:
        badge.loop()


if __name__ == '__main__':
    main()
