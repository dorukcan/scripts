import inspect
import logging
import math
import os
import time
import urllib.request
from math import atan2, ceil, cos, sin, sqrt
from random import randint

import cv2
import numpy as np


class ImageProcess():
    START_TIME = 0
    FINISH_TIME = 0

    INPUT_IMAGE = {}
    INPUT_IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "\\test_images\\"

    OUTPUT_IMAGE = {}
    OUTPUT_IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "\\output_images\\"
    OUTPUT_IMAGE_PREFIX = "output_"

    SECOND_IMAGE_NAME = "baboon.jpg"

    def __init__(self, imageName):
        self.__handleTime(mode="init")

        self.INPUT_IMAGE = self.__loadImage(imageName)

    def __loadImage(self, imageName):
        logging.info("Input: {0}".format(self.INPUT_IMAGE_FOLDER + imageName))

        image = cv2.imread(self.INPUT_IMAGE_FOLDER + imageName)
        height, width = image.shape[:2]
        imageName = imageName.split(".")[0].replace(self.OUTPUT_IMAGE_PREFIX, "")

        # cv2.imshow(imageName, image)

        return {"image": image,
                "name": imageName,
                "width": width,
                "height": height}

    def __saveImage(self, output, filterName="", mode=0):
        filterName = filterName + "_" if filterName != "" else filterName

        self.OUTPUT_IMAGE["image"] = output
        self.OUTPUT_IMAGE["name"] = self.OUTPUT_IMAGE_PREFIX + filterName + self.INPUT_IMAGE["name"] + ".png"
        self.OUTPUT_IMAGE["path"] = self.OUTPUT_IMAGE_FOLDER + self.OUTPUT_IMAGE["name"]

        self.__saveImageFile(output, self.OUTPUT_IMAGE["path"])

        logging.info("Output: {0}".format(self.OUTPUT_IMAGE["path"]))

        self.__handleTime(mode="finish")

        self.__showImage(output, self.OUTPUT_IMAGE["name"])

        self.INPUT_IMAGE["image"] = output
        self.INPUT_IMAGE["height"], self.INPUT_IMAGE["width"] = output.shape[:2]
        self.INPUT_IMAGE["name"] = filterName + self.INPUT_IMAGE["name"] if mode is 0 else self.INPUT_IMAGE["name"]

        self.__handleTime(mode="init")

    def __showImage(self, im, name):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"])

        cv2.imshow(name, im)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def __saveImageFile(self, im, path):
        cv2.imwrite(path, im)

    def __createBlankImage(self, width, height, backgroundColor=(255, 255, 255)):
        blankImage = np.full((height, width, 3), backgroundColor, dtype=np.uint8)
        return blankImage

    def __getPixel(self, im, x, y):
        try:
            return im.item(y, x, 2), im.item(y, x, 1), im.item(y, x, 0)
        except Exception as e:
            logging.error("getPixel error: {0}".format(e))
            logging.error(
                "x:{0} y:{1} width:{2} height:{3}".format(x, y, self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]))
            return 0, 0, 0

    def __setPixel(self, im, x, y, r, g, b):
        try:
            im.itemset((y, x, 2), r)
            im.itemset((y, x, 1), g)
            im.itemset((y, x, 0), b)
        except Exception as e:
            logging.error("setPixel error: {0}".format(e))
            logging.error(
                "x:{0} y:{1} r:{2} g:{3} b:{4} width:{5} height:{6}".format(x, y, r, g, b, self.INPUT_IMAGE["width"],
                                                                            self.INPUT_IMAGE["height"]))

    def __loadSecondImage(self, imageName):
        if imageName != None:
            return cv2.imread(self.INPUT_IMAGE_FOLDER + imageName)
        else:
            return cv2.imread(self.INPUT_IMAGE_FOLDER + self.SECOND_IMAGE_NAME)

    def __handleTime(self, mode):
        if mode is "finish":
            self.FINISH_TIME = cv2.getTickCount()
            elapsed = (self.FINISH_TIME - self.START_TIME) / cv2.getTickFrequency()
            logging.info("Execution time: {0} seconds\n".format(elapsed))
        elif mode is "init":
            self.FINISH_TIME = 0
            self.START_TIME = cv2.getTickCount()

    def border(self):
        im = self.INPUT_IMAGE["image"]
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        borderSize = 50

        new = self.__createBlankImage(width + borderSize * 2, height + borderSize * 2)
        new[borderSize:height + borderSize, borderSize:width + borderSize] = im

        red = im[:, :, 2].sum() // width // height
        green = im[:, :, 1].sum() // width // height
        blue = im[:, :, 0].sum() // width // height

        new[0:borderSize, :] = (blue, green, red)
        new[-borderSize:, :] = (blue, green, red)
        new[:, 0:borderSize] = (blue, green, red)
        new[:, -borderSize:] = (blue, green, red)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def brightness(self):
        new = 100 + self.INPUT_IMAGE["image"]

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def cartoon(self):
        im = self.INPUT_IMAGE["image"]
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        redAverage = im[:, :, 2].sum() // width // height
        greenAverage = im[:, :, 1].sum() // width // height
        blueAverage = im[:, :, 0].sum() // width // height

        numberOfShades = 5
        conversionFactor = 255 // (numberOfShades - 1)

        red = redAverage // conversionFactor * conversionFactor
        green = greenAverage // conversionFactor * conversionFactor
        blue = blueAverage // conversionFactor * conversionFactor

        new[:, :] = (blue, green, red)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def changeBlocks(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        inc = width // 50

        for i in range(0, height - inc * 2, inc * 2):
            for j in range(0, width - inc * 2, inc * 2):
                new[i:i + inc, j:j + inc] = self.INPUT_IMAGE["image"][i + inc:i + inc * 2, j + inc:j + inc * 2]
                new[i + inc:i + inc * 2, j + inc:j + inc * 2] = self.INPUT_IMAGE["image"][i:i + inc, j:j + inc]
                new[i:i + inc, j + inc:j + inc * 2] = self.INPUT_IMAGE["image"][i + inc:i + inc * 2, j:j + inc]
                new[i + inc:i + inc * 2, j:j + inc] = self.INPUT_IMAGE["image"][i:i + inc, j + inc:j + inc * 2]

        functionName = inspect.stack()[0][3]
        self.__saveImage(new[0:height - inc * 2, 0:width - inc * 2], functionName)
        return self

    def columnFilter(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.INPUT_IMAGE["image"]

        interval = width // 5

        for i in range(0, width, interval):
            redTotal = new[0:height, i:i + interval, 2].sum() // interval // width // 2
            greenTotal = new[0:height, i:i + interval, 1].sum() // interval // width // 2
            blueTotal = new[0:height, i:i + interval, 0].sum() // interval // width // 2

            new[0:height, i:i + interval, 2] //= 2
            new[0:height, i:i + interval, 1] //= 2
            new[0:height, i:i + interval, 0] //= 2

            new[0:height, i:i + interval, 2] += redTotal
            new[0:height, i:i + interval, 1] += greenTotal
            new[0:height, i:i + interval, 0] += blueTotal

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def combine(self, secondImageName=None):
        firstImage = self.INPUT_IMAGE["image"]
        width1, height1 = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        secondImage = self.__loadSecondImage(secondImageName)
        width2, height2 = secondImage.shape[1], secondImage.shape[0]

        width = min(width1, width2)
        height = min(height1, height2)

        new = cv2.multiply(firstImage[0:height, 0:width] / 255, secondImage[0:height, 0:width] / 255)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def crossFade(self, secondImageName=None):
        firstImage = self.INPUT_IMAGE["image"]
        width1, height1 = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        secondImage = self.__loadSecondImage(secondImageName)
        width2, height2 = secondImage.shape[1], secondImage.shape[0]

        width = min(width1, width2)
        height = min(height1, height2)

        alpha = 0.5
        new = firstImage[0:height, 0:width] * alpha - secondImage[0:height, 0:width] * (1 - alpha)

        new.astype(int)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def dither(self):
        def saturated_add(val1, val2):
            temp = val1 + val2
            return max(min(temp, 255), 0)

        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        im = self.INPUT_IMAGE["image"]
        new = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        for i in range(height - 1):
            for j in range(width - 1):
                if new[i, j] > 127:
                    err = new[i, j] - 255
                    new[i, j] = 255
                else:
                    err = new[i, j] - 0
                    new[i, j] = 0

                a = (err * 7) / 16
                b = (err * 1) / 16
                c = (err * 5) / 16
                d = (err * 3) / 16

                if j != 0:
                    new[i + 0, j + 1] = saturated_add(new[i + 0, j + 1], a);
                    new[i + 1, j + 1] = saturated_add(new[i + 1, j + 1], b);
                    new[i + 1, j + 0] = saturated_add(new[i + 1, j + 0], c);
                    new[i + 1, j - 1] = saturated_add(new[i + 1, j - 1], d);

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def edgeFind(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        for i in range(width - 1):
            for j in range(height - 1):
                red1, green1, blue1 = self.__getPixel(x=i, y=j, im=self.INPUT_IMAGE["image"])
                red2, green2, blue2 = self.__getPixel(x=i + 1, y=j + 1, im=self.INPUT_IMAGE["image"])

                d = int(sqrt(abs(red1 * red1 - red2 * red2) + abs(green1 * green1 - green2 * green2) + abs(
                    blue1 * blue1 - blue2 * blue2)))

                if d > 120:
                    self.__setPixel(im=new,
                                    x=i,
                                    y=j,
                                    r=255,
                                    g=255,
                                    b=255)
                else:
                    self.__setPixel(im=new,
                                    x=i,
                                    y=j,
                                    r=0,
                                    g=0,
                                    b=0)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def face(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        im = self.INPUT_IMAGE["image"]
        new = self.__createBlankImage(width, height)

        for j in range(height):
            for i in range(width):
                new[j, i] = (im[j, i] + 128 * sin(
                    sqrt((i - width / 2) * (i - width / 2) + (j - height / 2) * (j - height / 2)))) % 255

        face_cascade = cv2.CascadeClassifier(self.INPUT_IMAGE_FOLDER + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(im, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = im[y:y + h, x:x + w]

            randX, randY = randint(0, height - w), randint(0, width - h)

            new[randX:randX + w, randY:randY + h] = (roi + im[randX:randX + w, randY:randY + h]) / 2

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def filter(self, filterName=None):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        im = self.INPUT_IMAGE["image"]

        filters = {
            "blur": np.array([[0, 0, 0, 0, 0],
                              [0, 1, 1, 1, 0],
                              [0, 1, 1, 1, 0],
                              [0, 1, 1, 1, 0],
                              [0, 0, 0, 0, 0]]),
            "sharpen": np.array([[0, 0, 0, 0, 0],
                                 [0, 0, -1, 0, 0],
                                 [0, -1, 5, -1, 0],
                                 [0, 0, -1, 0, 0],
                                 [0, 0, 0, 0, 0]]),
            "edges": np.array([[0, 1, 0],
                               [1, -4, 1],
                               [0, 1, 0]]),
            "emboss": np.array([[-2, -1, 0],
                                [-1, 1, 1],
                                [0, 1, 2]]),
            "gaussian": np.array([[1, 4, 7, 4, 1],
                                  [4, 16, 26, 16, 4],
                                  [7, 26, 41, 26, 7],
                                  [4, 16, 26, 16, 4],
                                  [1, 4, 7, 4, 1]]),
            "laplacian_derivative": np.array([[0, 1, 0],
                                              [1, -4, 1],
                                              [0, 1, 0]])
        }

        filterName = "emboss" if filterName is None else filterName
        filter = filters[filterName]

        factor = max(filter.sum(), 1)

        padding = (len(filter) - 1) // 2
        output = self.__createBlankImage(width, height)

        for i in range(padding, width - padding - 1):
            for j in range(padding, height - padding - 1):
                roi1 = im[j - padding:j + padding + 1, i - padding:i + padding + 1, 0]
                roi2 = im[j - padding:j + padding + 1, i - padding:i + padding + 1, 1]
                roi3 = im[j - padding:j + padding + 1, i - padding:i + padding + 1, 2]

                k1 = (roi1 * filter).sum()
                k2 = (roi2 * filter).sum()
                k3 = (roi3 * filter).sum()

                output[j, i, 0] = min(max(k1 // factor, 0), 255)
                output[j, i, 1] = min(max(k2 // factor, 0), 255)
                output[j, i, 2] = min(max(k3 // factor, 0), 255)

        functionName = inspect.stack()[0][3]
        self.__saveImage(output, functionName + "-" + filterName)
        return self

    def gradientBlend(self, secondImageName=None):
        firstImage = self.INPUT_IMAGE["image"]
        width1, height1 = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        secondImage = self.__loadSecondImage(secondImageName)
        width2, height2 = secondImage.shape[1], secondImage.shape[0]

        width = min(width1, width2)
        height = min(height1, height2)

        firstImage = firstImage[0:height, 0:width]
        secondImage = secondImage[0:height, 0:width]

        new = self.__createBlankImage(width, height)

        for i in range(height):
            ratio = i / height
            new[i, :] = firstImage[i, :] * ratio + secondImage[i, :] * (1 - ratio)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def greyscale1(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]
        im = self.INPUT_IMAGE["image"]
        new = self.INPUT_IMAGE["image"]

        for i in range(width):
            for j in range(height):
                red, green, blue = self.__getPixel(x=i, y=j, im=new)

                gray = int(red * 0.2126 + green * 0.7152 + blue * 0.0722)
                self.__setPixel(im=new,
                                x=i,
                                y=j,
                                r=gray,
                                g=gray,
                                b=gray)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def greyscale2(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        for i in range(width):
            for j in range(height):
                red, green, blue = self.__getPixel(x=i, y=j, im=self.INPUT_IMAGE["image"])

                numberOfShades = 5
                conversionFactor = 255 // (numberOfShades - 1)
                averageValue = (red + green + blue) / 3
                gray = averageValue // conversionFactor * conversionFactor

                self.__setPixel(im=new,
                                x=i,
                                y=j,
                                r=gray,
                                g=gray,
                                b=gray)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def minMax(self, secondImageName=None):
        functionName = inspect.stack()[0][3]

        firstImage = self.INPUT_IMAGE["image"]
        width1, height1 = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        secondImage = self.__loadSecondImage(secondImageName)
        width2, height2 = secondImage.shape[1], secondImage.shape[0]

        width = min(width1, width2)
        height = min(height1, height2)

        new = np.minimum(firstImage[0:height, 0:width], secondImage[0:height, 0:width])
        self.__saveImage(new, functionName + "-min")

        new = np.maximum(firstImage[0:height, 0:width], secondImage[0:height, 0:width])
        self.__saveImage(new, functionName + "max")
        return self

    def negative(self):
        new = 255 - self.INPUT_IMAGE["image"]

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def operator(self):
        im = self.INPUT_IMAGE["image"]
        functionName = inspect.stack()[0][3]

        slice1 = slice(None, None, -1), slice(None, None, None)
        slice2 = slice(None, None, None), slice(None, None, -1)
        slice3 = slice(None, None, -1), slice(None, None, -1)
        slices = [slice1, slice2, slice3]

        for i, s in enumerate(slices):
            new = im ^ im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-1", mode=1)

            new = im & im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-2", mode=1)

            new = im | im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-3", mode=1)

            new = im + im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-4", mode=1)

            new = im - im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-5", mode=1)

            new = im * im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-6", mode=1)

            new = im / im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-7", mode=1)

            new = im % im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-8", mode=1)

            new = im ** im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-9", mode=1)

            new = im << im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-10", mode=1)

            new = im >> im[s]
            self.__saveImage(new, functionName + "-" + str(i) + "-11", mode=1)

        return self

    def pixelSort(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        im = self.INPUT_IMAGE["image"]
        new = self.__createBlankImage(width, height)

        def lum(r, g, b):
            return math.sqrt(.241 * r + .691 * g + .068 * b)

        def getFirstNotBlackX(x, y):
            for i in range(x, width):
                luminosity = lum(im[y, i, 2], im[y, i, 1], im[y, i, 0])
                # print (i,y,luminosity, im[y, i, 2], im[y, i, 1], im[y, i, 0])
                if luminosity > 5:
                    return i

            return x

        def getNextBlackX(x, y):
            for i in range(x, width):
                luminosity = lum(im[y, i, 2], im[y, i, 1], im[y, i, 0])
                if luminosity < 5:
                    return i + 1

            return x + 1

        x, xEnd, y = 0, 0, 0
        while y < height:
            while x < width - 1:
                x = getFirstNotBlackX(x, y)
                xEnd = getNextBlackX(x, y)
                # print(x, xEnd)
                unsorted = im[y, x:xEnd]

                new[y, x:xEnd] = np.sort(unsorted, axis=1)

                x = xEnd + 1
            y += 1

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def pixelate(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.INPUT_IMAGE["image"]

        inc = int(width / 50)

        for i in range(0, width, inc):
            for j in range(0, height, inc):
                redTotal = new[j:j + inc, i:i + inc, 2].sum()
                greenTotal = new[j:j + inc, i:i + inc, 1].sum()
                blueTotal = new[j:j + inc, i:i + inc, 0].sum()

                new[j:j + inc, i:i + inc, 2] = redTotal // (inc * inc)
                new[j:j + inc, i:i + inc, 1] = greenTotal // (inc * inc)
                new[j:j + inc, i:i + inc, 0] = blueTotal // (inc * inc)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def plasma(self):
        functionName = inspect.stack()[0][3]

        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        im = self.INPUT_IMAGE["image"]
        valueFunc = {
            0: lambda i, j: 128 * sin(i / 8),
            1: lambda i, j: 128 * sin((i + j) / 8),
            2: lambda i, j: 255 - sqrt(i * j),
            2: lambda i, j: 128 * sin(sqrt(i * j)),
            3: lambda i, j: 128 * sin(sqrt((i - width / 2) * (i - width / 2) + (j - height / 2) * (j - height / 2))),
            4: lambda i, j: int((time.time() % 255) * sin(i / 16)) + int((time.time() % 255) * sin(j / 16)),
            5: lambda i, j: 64 + 32 * sin(i / 16) + 32 * sin(j / 8) + 32 * sin((i + j) / 8) + 32 * sin(
                sqrt(i * i + j * j) / 8),
            6: lambda i, j: 128 + 128 * sin(i * math.pi / 32),
            7: lambda i, j: 128 + 128 * sin(i * math.pi),
            8: lambda i, j: 128 + 128 * cos(i * math.pi),
            9: lambda i, j: i ** 2,
            10: lambda i, j: i ** 2 + j ** 2,
            11: lambda i, j: i * (1 - i),
            12: lambda i, j: cos(i * math.pi) + sin(j * math.pi),
            13: lambda i, j: i ** 3,
            14: lambda i, j: math.exp(sin(i)) - 2 * cos(4 * i) + (sin((2 * i - math.pi)) / 24) ** 5,
            15: lambda i, j: i ** 2 - i ** 4,
            16: lambda i, j: j ** 2 - j ** 4,
            17: lambda i, j: sqrt(i * 137.508),
            18: lambda i, j: 128 * sin(i ** 2 + j ** 2),
            19: lambda i, j: 128 * cos(i * j)
        }

        for funcInd in range(len(valueFunc)):
            valueMat = self.__createBlankImage(width, height)

            for i in range(width):
                for j in range(height):
                    valueMat[j, i] = valueFunc[funcInd](i, j)

            new = (im + valueMat) % 255
            self.__saveImage(new, functionName + "-" + str(funcInd), mode=1)

        return self

    def realColorFilter(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.INPUT_IMAGE["image"]

        sensitivity = 150

        new[new > sensitivity] = 255
        new[new < sensitivity] //= 2

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def removeBlackBorder(self):
        im = self.INPUT_IMAGE["image"]

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        x, y, w, h = cv2.boundingRect(contours)

        new = im[y:y + h, x:x + w]

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def resize(self, scale=None, width=None, height=None):
        try:
            if scale is not None:
                new = cv2.resize(self.INPUT_IMAGE["image"], None, fx=scale, fy=scale)
            else:
                new = cv2.resize(self.INPUT_IMAGE["image"], (width, height))

            functionName = inspect.stack()[0][3]
            self.__saveImage(new, functionName)
            return self
        except:
            pass

    def rotate(self):
        im = self.INPUT_IMAGE["image"]

        # new = im[:,::-1]
        # new = im[::-1,:]
        # new = im[::-1,::-1]
        new = np.swapaxes(im, 0, 1)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def sharp(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)
        im = self.INPUT_IMAGE["image"]
        for i in range(width - 1):
            for j in range(height - 1):
                red1, green1, blue1 = self.__getPixel(x=i, y=j, im=self.INPUT_IMAGE["image"])
                red2, green2, blue2 = self.__getPixel(x=i + 1, y=j + 1, im=self.INPUT_IMAGE["image"])

                self.__setPixel(im=new,
                                x=i,
                                y=j,
                                r=int(sqrt(abs(red1 * red1 - red2 * red2))),
                                g=int(sqrt(abs(green1 * green1 - green2 * green2))),
                                b=int(sqrt(abs(blue1 * blue1 - blue2 * blue2))))

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def tunnel(self, gif=None):
        self.removeBlackBorder()

        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        while (True):
            ratio = 32
            shiftX = width * 1 * time.time()
            shiftY = height * 0.25 * time.time()
            centerX = width / randint(1, 5)
            centerY = height / randint(1, 5)

            for i in range(width):
                for j in range(height):
                    try:
                        distance = (ratio * height / sqrt(
                            (i - centerX) * (i - centerX) + (j - centerY) * (j - centerY))) % height
                    except:
                        distance = 0

                    angle = 0.5 * width * atan2(j - height / 2, i - width / 2) / 3.1416
                    xPos = int((distance + shiftX) % width)
                    yPos = int((angle + shiftY) % height)

                    new[j, i] = self.INPUT_IMAGE["image"][yPos, xPos]

            if gif != None:
                cv2.imshow("tunnel", new)
                key = cv2.waitKey(20)
                if key == 27:  # exit on ESC
                    cv2.destroyAllWindows()
                    break
            else:
                break

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self

    def quantization(self):
        width, height = self.INPUT_IMAGE["width"], self.INPUT_IMAGE["height"]

        new = self.__createBlankImage(width, height)

        factor = 4
        ratio = 255 / factor

        for i in range(width):
            for j in range(height):
                red, green, blue = self.__getPixel(x=i, y=j, im=self.INPUT_IMAGE["image"])

                red = ratio * ceil(red / ratio)
                green = ratio * ceil(green / ratio)
                blue = ratio * ceil(blue / ratio)

                self.__setPixel(im=new,
                                x=i,
                                y=j,
                                r=red,
                                g=green,
                                b=blue)

        functionName = inspect.stack()[0][3]
        self.__saveImage(new, functionName)
        return self


class Helper():
    START_TIME = 0
    FINISH_TIME = 0

    def __init__(self):
        self.__handleTime(mode="init")

    def __handleTime(self, mode):
        if mode is "finish":
            self.FINISH_TIME = time.time()
            elapsed = self.FINISH_TIME - self.START_TIME
            logging.info("Execution time: {0} seconds\n".format(elapsed))
        elif mode is "init":
            self.FINISH_TIME = 0
            self.START_TIME = time.time()

    def createSampleInputData(self):
        folderPath = ImageProcess.INPUT_IMAGE_FOLDER
        outputFolderPath = ImageProcess.OUTPUT_IMAGE_FOLDER

        folders = [
            {"name": "test_images", "path": folderPath},
            {"name": "output_images", "path": outputFolderPath},
        ]

        for folder in folders:
            if not os.path.exists(folder["path"]):
                os.makedirs(folder["path"])
                logging.info("{0} folder has been created\n".format(folder["name"]))

        files = [
            {"name": "baboon.jpg", "url": "https://imagej.nih.gov/ij/images/baboon.jpg"},
            {"name": "lena.jpg", "url": "https://imagej.nih.gov/ij/images/lena.jpg"},
            {"name": "doruk.jpg",
             "url": "https://scontent-otp1-1.xx.fbcdn.net/v/t1.0-9/10659208_10206937386297344_8963969065168858442_n.jpg?oh=f8144159ce5c69d7cac669277447b8d6&oe=59E48539"},
            {"name": "haarcascade_frontalface_default.xml",
             "url": "https://raw.githubusercontent.com/Itseez/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"},
            {"name": "haarcascade_eye.xml",
             "url": "https://raw.githubusercontent.com/Itseez/opencv/master/data/haarcascades/haarcascade_eye.xml"},
        ]

        for file in files:
            if not os.path.exists(folderPath + file["name"]):
                logging.info("{0} is downloading".format(file["name"]))
                try:
                    data = urllib.request.urlopen(file["url"]).read()
                    with open(folderPath + file["name"], "wb") as f:
                        f.write(data)
                    logging.info("{0} has been downloaded\n".format(file["name"]))
                except Exception as e:
                    logging.error("{0} couldn't downloaded. Error: {1} \n".format(file["name"], str(e)))

        self.__handleTime(mode="finish")

    def getAppropriateFileName(self, imageName):
        folderPath = ImageProcess.INPUT_IMAGE_FOLDER

        if os.path.exists(folderPath + imageName):
            return imageName
        else:
            logging.warning("{0} does not exist.\n".format(imageName))
            if os.path.exists(folderPath + "lena.jpg"):
                return "lena.jpg"
            else:
                logging.error(
                    "No such file have been found. Please consider adding images to test folder or connecting to internet.")
                return None

    def initLogging(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %H:%M:%S',
                            level=logging.INFO)

    def processOneImage(self, imageName):
        public_method_names = [method for method in dir(ImageProcess) if callable(getattr(ImageProcess, method)) if
                               not method.startswith("_")]

        for method in public_method_names:
            im = ImageProcess(imageName)
            getattr(im, method)()


class Experimental():
    def __init__(self):
        pass

    def camTest(self):
        cap = cv2.VideoCapture(0)

        while (True):
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow("w1", gray)

            key = cv2.waitKey(20)
            if key == 27:  # exit on ESC
                break

        cv2.destroyAllWindows()


def main():
    imageName = "doruk.jpg"

    helper = Helper()
    helper.initLogging()
    helper.createSampleInputData()

    imageName = helper.getAppropriateFileName(imageName)
    if imageName is None:
        return

    ImageProcess(imageName).dither()


if __name__ == '__main__':
    main()
