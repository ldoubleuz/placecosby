from PIL import Image

''' given the original dimensions of an image and the target container size,
  returns width/height dimensions for a region that fills as much of 
  the container as possible without overflowing or losing the aspect ratio
  
  @param oldWidth
    the original width of an image
  @param oldHeight
    the original height of an image
  @param containerWidth
    the width limit of the container
  @param containerHeight
    the height limit of the container
  @return
    returns a tuple of floats for the resulting (width,height) dimension
'''
def sizeToContain(oldWidth, oldHeight, containerWidth, containerHeight):
    widthScaleFactor = float(containerWidth) / oldWidth
    heightScaleFactor = float(containerHeight) / oldHeight
    # use minimum scale to ensure that the final dimensions fit in the container
    minScale = min(widthScaleFactor, heightScaleFactor)
    return (min(oldWidth * minScale, containerWidth), 
            min(oldHeight * minScale, containerHeight))

''' create a copy of a PIL image resized to the given dimensions, cropping the 
  largest area possible and focusing on as much of the central region 
  as possible 

  @param img
    the original PIL image to resize (make sure it is open before calling this!)
  @param targWidth
    the target width of the final image
  @param targHeight
    the target height of the final image
  @param cxPercent
    a percentage, given as a float between 0 and 1, of where the horizontal
    center of the image should be
  @param cyPercent
    a percentage, given as a float between 0 and 1, of where the vertical
    center of the image should be
  @return
    a PIL copy of the orig image, cropped and resized to the target dimensions
'''
def resizeImage(img, targWidth, targHeight, cxPercent, cyPercent):
    assert targWidth >= 0
    assert targHeight >= 0
    assert 0 <= cxPercent <= 1
    assert 0 <= cyPercent <= 1

    imgWidth, imgHeight = img.size
    assert imgWidth > 0
    assert imgHeight > 0

    # return blank dummy image if requested a zero image
    if targWidth == 0 or targHeight == 0:
        return Image.new("RGB", (targWidth, targHeight))

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