#!/usr/bin/python3

import os
import sys
import getopt
import random
import time

from PIL import Image as image
from PIL import ImageStat

class imGenExp(Exception):
	def __init__(self, message="", code=0):
		self.message = message
		self.code = code
		super().__init__(self.message, self.code)


def print_help():
	print("	-h - print this message\n"
	      "	--source-dir=<source dir> - specify source images directory\n"
	      "	--target=<target path> - specify target image name\n"
	      "	-s, --size-multiplier=<float(0.1-1)> - sticker size modification\n"
	      "	-r, --resolution=<(1080x1024)> - target image resolution. default - 3840x2160\n")

class imageGenerator():
	def __init__(this, size=(3840, 2160), source_dir="./source-images"):
		this.imageSize = size
		this.source_dir = source_dir
		this.target_path = ""
		this.imageList = []
		this.avImageSize = (0, 0) #average image size. calculated in readImages() method
		this.sizeCooficient = 0.4 #sticker size cooficient


	def checkParams(this):
		if not (this.source_dir):
			raise imGenExp("source-dir not spcified", -1)
		if not (os.path.exists(this.source_dir)):
			raise imGenExp(("source-dir", this.source_dir, "not exists"), -2)
		if not (os.path.isdir(this.source_dir)):
			raise imGenExp(("source-dir", this.source_dir, "is not directory"), -1)
		if not (os.listdir(this.source_dir)):
			raise imGenExp(("source-dir", this.source_dir, "is empty"), -1)
		if (this.sizeCooficient > 1) or (this.sizeCooficient <= 0):
			raise imGenExp("size-multiplier invalid. must be in range of 0.1-1", -1)


	def readImages(this):
		print("Reading images")
		for file in os.scandir(this.source_dir):
			tmpImage = image.open(this.source_dir + "/" + file.name, formats=["png"])
			xSize = int(tmpImage.size[0]*this.sizeCooficient)
			ySize = int(tmpImage.size[1]*this.sizeCooficient)
			tmpImage = tmpImage.resize((xSize, ySize))
			this.avImageSize = ((tmpImage.size[0] + this.avImageSize[0])//2, (tmpImage.size[1] + this.avImageSize[1])//2)
			this.imageList.append(tmpImage)
		if not this.imageList:
			raise imGenExp("failed to read images from source-dir", -1)
		if (this.avImageSize[0] > this.imageSize[0]) or (this.avImageSize[1] > this.imageSize[1]):
			raise imGenExp("average sticker size exceeds target resolution", -1)
		print("Average image size", this.avImageSize)


	def buildGrid(this):
		grid = []
		x = 0
		y = 0

		print("Generating grid")

		while (x < this.imageSize[0]) and (y < this.imageSize[1]):
			grid.append((x, y))
			x += this.avImageSize[0]//2 #each cell in grid 2 times less than average image to create overlap
			if x > this.imageSize[0]:
				x = 0
				y += this.avImageSize[1]//2
		if not (grid):
			raise imGenExp("failed to generate pivot grid", -1)
		return grid;


	def placeImages(this, grid):
		print("Placing images")
		target = image.new("RGBA", this.imageSize)
		while (len(grid)):
			place = grid.pop(grid.index(random.choice(grid)))
			stickerOffsetCompensation = ((this.avImageSize[0]//2)*-1, (this.avImageSize[1]//2)*-1)
			placeWithOffset = (place[0] + stickerOffsetCompensation[0], place[1] + stickerOffsetCompensation[1])
			sticker = random.choice(this.imageList)
			sticker = sticker.convert("RGBA")
			sticker = sticker.rotate(random.randrange(-45, 45))
			target.paste(sticker, placeWithOffset, sticker)
		return target


	def generateBackground(this, source):
		color = ImageStat.Stat(source).median
		bckImage = image.new("RGBA", this.imageSize, (color[0], color[1], color[2]))
		return bckImage


	def create(this):
		try:
			this.readImages()
		except imGenExp as exp:
			print("ERROR:", exp.message)
			os._exit(exp.code)

		try:
			grid = this.buildGrid()
		except imGenExp as exp:
			print("ERROR:", exp.message)
			os._exit(exp.code)

		this.stkImage = this.placeImages(grid)
		this.bckImage = this.generateBackground(this.stkImage)


	def print(this):
		targetImage = image.new("RGBA", this.imageSize)
		targetImage.paste(this.bckImage, (0,0), this.bckImage.convert("RGBA"))
		targetImage.paste(this.stkImage, (0,0), this.stkImage.convert("RGBA"))
		if not (this.target_path):
			this.target_path = str(int(time.time())) + ".png"
		try:
			targetImage.save(this.target_path)
		except ValueError:
			print("ERROR: Failed to save image. Check target file extension")
			os._exit(-1)

		print("Image loaded to", this.target_path)


def main(argv):
	generator = imageGenerator()

	try:
		opts, args = getopt.getopt(argv,
		                    "hs:r:",
		                    ["source-dir=",
		                     "target=",
		                     "size-multiplier=",
		                     "resolution="])
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
		elif (opt == "--resolution") or (opt == "-r"):
			width, height = arg.split("x", 2)
			generator.imageSize = (int(width), int(height))

	try:
		generator.checkParams()
	except imGenExp as exp:
		print("ERROR:", exp.message)
		os._exit(exp.code)

	generator.create()
	generator.print()

if __name__ == "__main__":
	main(sys.argv[1:])