from PIL import Image
import os, random, math, imghdr, datetime, json, time

TARGET_WIDTH = random.randint(10, 300)
TARGET_HEIGHT = random.randint(10, 300)

curPath = os.path.realpath(__file__)
PROJECT_DIR = os.path.split(curPath)[0]
COSBY_DIR = os.path.join(PROJECT_DIR, "images")

# returns dimensions for a region that fills as much of the container as
# without overflowing or losing the aspect ratio
# returns a tuple of floats
def sizeToContain(oldWidth, oldHeight, containerWidth, containerHeight):
    widthScaleFactor = float(containerWidth) / oldWidth
    heightScaleFactor = float(containerHeight) / oldHeight
    # use minimum scale to ensure that the final dimensions fit
    minScale = min(widthScaleFactor, heightScaleFactor)
    return (min(oldWidth * minScale, containerWidth), 
            min(oldHeight * minScale, containerHeight))

# resizes the image to the given dimensions, cropping the largest area possible
# and focusing on as much of the central region as possible
def resizeImage(img, targWidth, targHeight, cxPercent, cyPercent):
    assert targWidth > 0
    assert targHeight > 0
    assert 0 <= cxPercent <= 1
    assert 0 <= cyPercent <= 1

    imgWidth, imgHeight = img.size
    assert imgWidth > 0
    assert imgHeight > 0

    cx = int(cxPercent * imgWidth)
    cy = int(cyPercent * imgHeight)

    # multiply width by this number to get a height of the proper ratio
    widthHeightRatio = float(targHeight) / targWidth

    # determine dimensions of a region to crop, and ensure that it can actually
    # be cropped from the image
    cropWidth, cropHeight = sizeToContain(imgWidth, imgWidth * widthHeightRatio, 
                                          imgWidth, imgHeight)
    left = int(max(cx - (cropWidth / 2.0), 0))
    top = int(max(cy - (cropHeight / 2.0), 0))

    cropWidth = int(round(cropWidth))
    cropHeight = int(round(cropHeight))

    right = left + cropWidth
    if right > imgWidth:
        left = imgWidth - cropWidth
        right = imgWidth

    bottom = top + cropHeight
    if bottom > imgHeight:
        top = imgHeight - cropHeight
        bottom = imgHeight

    croppedImg = img.crop((left, top, right, bottom))

    # optimize so that shrinking doesn't produce visual artifacts, while
    # expanding doesn't cause massive slowdown
    if targWidth > imgWidth or targHeight > imgHeight:
        imgFilter = Image.NEAREST
    else:
        imgFilter = Image.ANTIALIAS
    return croppedImg.resize((targWidth, targHeight), imgFilter)

def main():
    print "Target size: %d x %d" % (TARGET_WIDTH, TARGET_HEIGHT)

    # read image center information from json file
    with open(os.path.join(PROJECT_DIR, "image_centers.json"), "r") as file:
        centerPercents = json.load(file)

    imageFilenames = os.listdir(COSBY_DIR)

    for cosbyImgName in imageFilenames:
        # determine image center
        if cosbyImgName in centerPercents:
            [cxPercent, cyPercent] = centerPercents[cosbyImgName]
        else:
            cxPercent = cyPercent = 0.5

        cosbyPath = os.path.join(COSBY_DIR, cosbyImgName)
        if not (os.path.isfile(cosbyPath) and
                imghdr.what(cosbyPath) in {"png", "gif", "jpeg"}):
            continue

        try:
            cosbyImg = Image.open(cosbyPath)
        except IOError:
            print "unable to open %s" % cosbyPath
            continue
        startTime = time.time()
        croppedCosby = resizeImage(cosbyImg, TARGET_WIDTH, TARGET_HEIGHT,
                                   cxPercent, cyPercent)
        endTime = time.time()
        assert croppedCosby.size[0] == TARGET_WIDTH
        assert croppedCosby.size[1] == TARGET_HEIGHT
        print "showing %s... (%f s)" % (cosbyImgName, 
                                        (endTime - startTime) / 1000.0)
        croppedCosby.show()

if __name__ == "__main__":
    main()