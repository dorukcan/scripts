#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import json
import os
import sys
import time
import winreg
from random import randint

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


class BackgroundArt:
    IMAGE_FOLDER = "C:\\BackgroundArchive\\"
    IMAGE_EXTENSION = "png"
    WIKIART_URL = "https://www.wikiart.org/en/App/Search/popular-paintings?searchterm=alltime&json=2&page="

    BLACKLIST_ARTIST = ["Pablo Picasso", "Jean-Michel Basquiat"]

    SUBTEXT = True
    FROMFOLDER = False

    def __init__(self, args):
        for arg in args[1:]:
            if arg is "-folder":
                self.FROMFOLDER = True
            elif arg is "-nosubtext":
                self.SUBTEXT = False

        self.check_if_image_folder_exists()

        if self.FROMFOLDER is False:
            self.start_for_url()
        else:
            self.start_for_folder()

    def check_if_image_folder_exists(self):
        """Checks if the image folder is exists and if not creates"""

        if not os.path.exists(self.IMAGE_FOLDER):
            os.makedirs(self.IMAGE_FOLDER)

    def start_for_url(self):
        """Starts the program to get image data from the given url"""

        painting = self.get_random_image_from_url()
        self.pretty_print_image_data(painting)

        self.download_image(painting)
        self.modify_image(painting)
        self.set_background(painting)

        # self.pause()

    def start_for_folder(self):
        """Starts the program to get image data from IMAGE_FOLDER"""

        painting = self.get_random_image_from_folder()
        self.set_background(painting)

    def get_random_image_from_url(self):
        """Gets a random image from wikiart json api"""

        # get random page full of artworks
        randomPage = str(randint(1, 60))
        response = requests.post(self.WIKIART_URL + randomPage)
        jsonObj = json.loads(response.text)

        # get random image which is not in BLACKLIST_ARTIST and not in downloaded images folder
        files = self.get_images_from_folder()
        while True:
            randomIndex = randint(0, jsonObj["PageSize"] - 1)
            painting = jsonObj["Paintings"][randomIndex]

            fileName = self.get_image_file_name(painting)

            isInFolder = True if (fileName in files) else False
            isInBlacklist = True if (painting["artistName"] in self.BLACKLIST_ARTIST) else False

            if not (isInFolder or isInBlacklist):
                break

        return painting

    def get_random_image_from_folder(self):
        """Gets a random image from downloaded images folder"""

        files = self.get_images_from_folder()
        randomIndex = randint(0, len(files))

        return self.IMAGE_FOLDER + files[randomIndex]

    def get_images_from_folder(self):
        """Returns a list of files in downloaded images folder"""

        return [f for f in os.listdir(self.IMAGE_FOLDER) if os.path.isfile(os.path.join(self.IMAGE_FOLDER, f))]

    def pretty_print_image_data(self, painting):
        """Prints image information to console as user friendly"""

        print("### image information ###")
        print("id: " + painting["id"])
        print("artistName: " + painting["artistName"])
        print("title: " + painting["title"])
        print("year: " + painting["year"])
        print("height: " + str(painting["height"]))
        print("width: " + str(painting["width"]))
        print("image: " + painting["image"])

    def download_image(self, painting):
        """Downloads and saves the image file data"""

        with open(self.get_image_path(painting), "wb") as f:
            startTime = time.clock()
            r = requests.get(painting["image"], stream=True)
            totalLength = r.headers.get("content-length")

            averageSpeed = 0
            if totalLength is None:  # no content length header
                f.write(r.content)
            else:
                downloaded = 0
                speedIterationCount = 0

                for chunk in r.iter_content(1024):
                    downloaded += len(chunk)
                    f.write(chunk)

                    done = int(100 * downloaded / int(totalLength))

                    kilobytePerSecond = downloaded // (time.clock() - startTime) / 1024

                    speedIterationCount += 1
                    averageSpeed += kilobytePerSecond

                    sys.stdout.write("\r%%%s %s kbps" % (done, kilobytePerSecond))
                    sys.stdout.flush()

                averageSpeed /= speedIterationCount

        print("\r\relapsed: " + str(time.clock() - startTime) + " seconds")
        print("average speed: " + str(averageSpeed) + " kbps")

    def modify_image(self, painting):
        """Writes the information of the painting to the canvas"""

        if self.SUBTEXT is False:
            return

        # get the image
        base = Image.open(self.get_image_path(painting)).convert("RGBA")

        # get the drawing context
        draw = ImageDraw.Draw(base)

        # set text properties
        fontSize = painting["height"] // 40
        try:
            font = ImageFont.truetype("MyriadPro-Regular.otf", fontSize)
        except ImportError as e:
            font = ImageFont.truetype("Helvetica.otf", fontSize)
        imageText = painting["title"] + " - " + painting["artistName"] + " - " + painting["year"]
        colorStroke = (0, 0, 0)  # stroke color
        colorText = (255, 255, 255)  # text color
        xPos = painting["width"] / 50
        yPos = painting["height"] - font.getsize(imageText)[1] * 1.5

        # set text background properties
        xPos1Background = painting["width"] / 75
        xPos2Background = xPos + font.getsize(imageText)[0] + xPos - xPos1Background
        yPos1Background = yPos - font.getsize(imageText)[1] / 5
        yPos2Background = yPos + font.getsize(imageText)[1] + font.getsize(imageText)[1] / 5

        # draw text background
        rectangle = Image.new("RGBA", base.size, (0, 0, 0, 0))
        rectangleDraw = ImageDraw.Draw(rectangle)
        rectangleDraw.rectangle([xPos1Background, yPos1Background, xPos2Background, yPos2Background], fill=(0, 0, 0))
        alpha = rectangle.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
        rectangle.putalpha(alpha)
        base = Image.composite(rectangle, base, rectangle)
        draw = ImageDraw.Draw(base)

        # draw text to the canvas
        xPosIncerement = 0  # for letter spacing
        for i, letter in enumerate(imageText):
            # draw stroke letter
            draw.text((xPos + xPosIncerement, yPos), letter, fill=colorStroke, font=font)

            # draw actual letter
            draw.text((xPos + xPosIncerement - 1, yPos), letter, fill=colorText, font=font)

            # calculate the position of next letter with current letter width
            xPosIncerement += font.getsize(letter)[0]

        # save the image
        base.save(self.get_image_path(painting))

    def set_background(self, painting):
        """Sets the background of device (windows only)"""

        desktopKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(desktopKey, "WallpaperStyle", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(desktopKey, "TileWallpaper", 0, winreg.REG_SZ, "0")

        path = self.get_image_path(painting) if self.FROMFOLDER is False else painting
        imageBuffer = ctypes.create_string_buffer(str.encode(path))
        ctypes.windll.user32.SystemParametersInfoA(20, 0, imageBuffer, 1)

    def get_image_path(self, painting):
        """Returns the absolute file path"""

        return self.IMAGE_FOLDER + self.get_image_file_name(painting)

    def get_image_file_name(self, painting):
        """Returns the name of painting with file extension"""

        localFilename = painting["image"].split("/")[-1]
        localFilename = localFilename.split(".")[0]

        return localFilename + "-" + painting["id"] + "." + self.IMAGE_EXTENSION

    def pause(self):
        """Pauses the program to read outputs on console"""

        os.system("pause")


def main():
    BackgroundArt(sys.argv)


if __name__ == "__main__":
    main()
