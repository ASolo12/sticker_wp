#!/usr/bin/python3

import os
import sys
import getopt
import random

from PIL import Image as image
from PIL import ImageStat

def print_help():
	print("	-h - print this message\n"
	      "	--source-dir=<source dir> - specify source images directory\n"
	      "	--target=<target path> - specify target image name\n"
	      "	--size-multiplier=<float(0.1-1)> - sticker size modification\n")

class imageGenerator():
	imageSize = (0, 0)
	target_path = ""
	source_dir = ""
	imageList = []
	avImageSize = (0, 0) #average image size. calculated in readImages() method
	sizeCooficient = 0.4 #sticker size cooficient


	def __init__(this, size=(3840, 2160), source_dir="./source-images", target_path="./output-image"):
		this.imageSize = size
		this.source_dir = source_dir
		this.target_path = target_path + ".png"


	def readImages(this):
		print("reading images")
		for file in os.scandir(this.source_dir):
			tmpImage = image.open(this.source_dir + "/" + file.name, formats=["png"])
			xSize = int(tmpImage.size[0]*this.sizeCooficient)
			ySize = int(tmpImage.size[1]*this.sizeCooficient)
			tmpImage = tmpImage.resize((xSize, ySize))
			this.avImageSize = ((tmpImage.size[0] + this.avImageSize[0])//2, (tmpImage.size[1] + this.avImageSize[1])//2)
			this.imageList.append(tmpImage)
		print("average image size", this.avImageSize)


	def buildGrid(this):
		grid = []
		x = 0
		y = 0

		print("generating grid")

		while (x < this.imageSize[0]) and (y < this.imageSize[1]):
			grid.append((x, y))
			x += this.avImageSize[0]//2 #each cell in grid 2 times less than average image to create overlap
			if x > this.imageSize[0]:
				x = 0
				y += this.avImageSize[1]//2
		return grid;


	def placeImages(this, grid):
		print("placing images")
		target = image.new("RGBA", this.imageSize)
		while (len(grid)):
			place = random.choice(grid)
			stickerOffsetCompensation = ((this.avImageSize[0]//2)*-1, (this.avImageSize[1]//2)*-1)
			placeWithOffset = (place[0] + stickerOffsetCompensation[0], place[1] + stickerOffsetCompensation[1])
			sticker = random.choice(this.imageList)
			sticker = sticker.rotate(random.randrange(-45, 45))
			target.paste(sticker, placeWithOffset, sticker.convert("RGBA"))
			grid.pop(grid.index(place))
		return target


	def generateBackground(this, source):
		color = ImageStat.Stat(source).median
		bckImage = image.new("RGBA", this.imageSize, (color[0], color[1], color[2]))
		return bckImage


	def create(this):
		this.readImages()
		grid = this.buildGrid()
		this.stkImage = this.placeImages(grid)
		this.bckImage = this.generateBackground(this.stkImage)


	def print(this):
		targetImage = image.new("RGBA", this.imageSize)
		targetImage.paste(this.bckImage, (0,0), this.bckImage.convert("RGBA"))
		targetImage.paste(this.stkImage, (0,0), this.stkImage.convert("RGBA"))
		targetImage.save(this.target_path)
		print("image loaded to", this.target_path)


def main(argv):
	generator = imageGenerator()

	try:
		opts, args = getopt.getopt(argv,
		                    "hs:",
		                    ["source-dir=",
		                     "target=",
		                     "size-multiplier="])
	except getopt.GetoptError:
		print_help()
		sys.exit(-1)
	for opt, arg in opts:
		if opt == "-h":
			print_help()
		elif opt == "--source-dir":
			generator.source_dir = arg
		elif opt == "--target":
			generator.target_path = arg
		elif (opt == "--size-multiplier") or (opt == "-s"):
			generator.sizeCooficient = float(arg)

	generator.create()
	generator.print()

if __name__ == "__main__":
	main(sys.argv[1:])