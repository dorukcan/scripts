import operator

from PIL import Image, ImageDraw


class ColorPalette():
    INPUT_IMAGE = {}
    INPUT_IMAGE_FOLDER = "C:\\Users\\dorukcan\\Desktop\\"
    INPUT_IMAGE_EXTENSION = "jpg"
    OUTPUT_IMAGE_FOLDER = "C:\\Users\\dorukcan\\Desktop\\"
    OUTPUT_IMAGE_PREFIX = "output_"
    OUTPUT_IMAGE_EXTENSION = "jpg"

    def __init__(self, imageName):
        self.INPUT_IMAGE = self.getImage(imageName)

        palette = self.generatePalette()

        output = self.modifyImage(palette)
        self.saveOutputImage(output, imageName)

    def getImage(self, imageName):
        image = Image.open(self.getInputImagePath(imageName)).convert("RGBA")
        draw = ImageDraw.Draw(image)

        return {"image": image, "draw": draw}

    def generatePalette(self):
        pixels = self.getPixels()
        commonColors = self.getColorsSorted(pixels)

        colorList = self.filterColorList(commonColors)
        palette = self.sortColorsByRGB(colorList)

        return palette

    def getPixels(self):
        pixels = self.INPUT_IMAGE["image"].getdata()
        width, height = self.INPUT_IMAGE["image"].size
        pixel_count = width * height

        validPixels = []
        for i in range(0, pixel_count):
            r, g, b, a = pixels[i]

            # If pixel is mostly opaque and not white
            if a >= 125:
                if not (r > 250 and g > 250 and b > 250):
                    validPixels.append((r, g, b))

        return validPixels

    def getColorsSorted(self, colorList):
        result = {}

        for item in colorList:
            if item in result:
                result[item] += 1
            else:
                result[item] = 1

        result = sorted(result.items(), reverse=True, key=operator.itemgetter(1))

        return result

    def filterColorList(self, colorList):
        """
        result = []

        for i in range(len(colorList)):
            found = 0
            color1 = colorList[i][0]

            for j in range(i + 1, len(colorList)):
                color2 = colorList[j][0]

                dist = sqrt( (color1[0]-color2[0])**2 + (color1[1]-color2[1])**2 + (color1[2]-color2[2])**2 )
                if dist < 5:
                    found = 1
                    break

            if found == 0:
                result.append(color1)

        return result[0:10]
        """

        result = []
        for i in range(len(colorList)):
            result.append(colorList[i][0])
        return result[0:10]

    def sortColorsByRGB(self, colorList):
        return colorList

    def modifyImage(self, palette):
        canvasSize = self.INPUT_IMAGE["image"].size
        lengthOfSquare = (canvasSize[0] / len(palette))

        newImage = Image.new("RGBA", (canvasSize[0], canvasSize[1] + lengthOfSquare))
        newImage.paste(self.INPUT_IMAGE["image"], (0, 0, canvasSize[0], canvasSize[1]))
        newImageDraw = ImageDraw.Draw(newImage)

        for i, color in enumerate(palette):
            xPos1 = lengthOfSquare * i
            xPos2 = lengthOfSquare * (i + 1)
            yPos1 = canvasSize[1]
            yPos2 = canvasSize[1] + lengthOfSquare

            print(i + 1, color)

            newImageDraw.rectangle([xPos1, yPos1, xPos2, yPos2], fill=color, outline=(255, 255, 255))

        return newImage

    def saveOutputImage(self, output, imageName):
        output.save(self.getOutputImagePath(imageName))
        output.show()

    def getInputImagePath(self, imageName):
        return self.INPUT_IMAGE_FOLDER + imageName + '.' + self.INPUT_IMAGE_EXTENSION

    def getOutputImagePath(self, imageName):
        return self.OUTPUT_IMAGE_FOLDER + self.OUTPUT_IMAGE_PREFIX + imageName + '.' + self.OUTPUT_IMAGE_EXTENSION


def main():
    from datetime import datetime
    startTime = datetime.now()

    ColorPalette("lena")

    print(datetime.now() - startTime)


if __name__ == '__main__':
    main()
