Sticker wallpaper generator 
====================
python3 pillow based image generator (not neural network)

Requirements
---------------------
pillow: pip3 install pillow

Usage
---------------------
	python3 sticker_wp.py --source-dir=./source-dir --target ouput-image.png --size-multiplier 0.3 --resolution 1080x1024


* `--source-dir` - directory with source material. PNG images or "stickers". default: ./source-images
* `--target` - output image name with .png extension. default: timestamp based name
* `-s --size-multiplier` - stickers size modificator in range 0,1-1. default: 0.4
* `-r --resolution` - target image resolution. default: 3840x2160