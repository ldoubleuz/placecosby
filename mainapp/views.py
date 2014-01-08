from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, \
                        HttpResponseServerError
from django.core.files.base import ContentFile 
from annoying.functions import get_object_or_None
from mainapp.models import SrcImage, GenImage

import PIL
import datetime
import random
import StringIO
import traceback

import cropcosby

MAX_IMAGE_DIM = 3000

def parseIntOrNone(num):
    try: 
        return int(num)
    except:
        return None

def requestIndex(request):
    return render(request, "mainapp/index.html")

def requestGallery(request):
    numSrcs = SrcImage.objects.order_by("image").count()
    return render(request, "mainapp/gallery.html", {"numSrcs" : numSrcs})

def generateCroppedImage(srcImageModel, targWidth, targHeight, assignedDate, genImageModel=None):
    # open the image before cropping
    try:
        srcImageModel.image.open("rb")
        # call load() to force the data to be read immediately
        srcImage = PIL.Image.open(srcImageModel.image)
        srcImage.load()
    except IOError as e:
        print "unable to open %s" % srcImageModel.image.url
        raise e
    finally:
        srcImageModel.image.close()
    
    # create a cropped PIL image 
    croppedImage = cropcosby.resizeImage(srcImage, targWidth, targHeight,
                                         srcImageModel.cxPercent, 
                                         srcImageModel.cyPercent)

    # actually generate the model for the generated image, if not already given
    if not genImageModel:
        genImageModel = GenImage(assignedDate=assignedDate, 
                                 srcImage=srcImageModel)

    imageName = "%s-%s_%s" % (targWidth, targHeight, srcImageModel.rawImageName())

    # create an image file from the cropped PIL image
    # based on http://stackoverflow.com/a/4544525
    imageIO = StringIO.StringIO()
    croppedImage.save(imageIO, format="JPEG") # save to the buffer
    imageFile = ContentFile(imageIO.getvalue())

    # finally save the image to the model
    genImageModel.genImage.save(imageName, imageFile, save=True)
    return genImageModel

# for requests that specify a source image to use
def getRequestedGenImage(targWidth, targHeight, srcImage, assignedDate=None):
    cachedImage = get_object_or_None(GenImage, width=targWidth, 
                                     height=targHeight, srcImage=srcImage)
    if cachedImage:
        # update date
        if assignedDate is not None:
            cachedImage.assignedDate = assignedDate
            cachedImage.save()
        if cachedImage.imageExists():
            return cachedImage

    # in cases where either the image doesn't already exist or the stored image 
    # has expired/gone missing, generate a new image
    return generateCroppedImage(srcImage, targWidth, targHeight, assignedDate, 
                                genImageModel=cachedImage)

# for requests that don't specify a source image to use
def getDefaultGenImage(targWidth, targHeight, allSrcs, numSrcs):
    curDate = datetime.datetime.today().toordinal()
    cachedImage = get_object_or_None(GenImage, width=targWidth, 
                                     height=targHeight, assignedDate=curDate)
    if cachedImage:
        if cachedImage.imageExists():
            return cachedImage
        # otherwise, indicate that we need to regenerate image
        else:
            srcImage = cachedImage.srcImage
    else:
        # pick a random source image to request
        srcImage = allSrcs[random.randint(0, numSrcs-1)]

    return getRequestedGenImage(targWidth, targHeight, srcImage, 
                                assignedDate=curDate)

def requestSize(request, targWidth, targHeight):
    targWidth = parseIntOrNone(targWidth)
    targHeight = parseIntOrNone(targHeight)

    if targWidth is None or targHeight is None:
        return HttpResponseBadRequest("invalid size parameter")
    elif targWidth > MAX_IMAGE_DIM or targHeight > MAX_IMAGE_DIM:
        return HttpResponseBadRequest("image too large, please request something smaller")
    
    targWidth = max(targWidth, 0)
    targHeight = max(targHeight, 0)

    allSrcs = SrcImage.objects.order_by("image")
    numSrcs = allSrcs.count()

    requestIndex = parseIntOrNone(request.GET.get("image", None))
    try:
        if requestIndex is None:
            outputGenImage = getDefaultGenImage(targWidth, targHeight, 
                                                allSrcs, numSrcs)
        else:
            outputGenImage = getRequestedGenImage(targWidth, targHeight, 
                                                  allSrcs[requestIndex % numSrcs])
    except IOError:
        traceback.print_exc()
        return HttpResponseServerError("unable to retrieve image")

    # convert cropped image into an http response
    response = HttpResponse(content_type="image/png")
    # open the stored image and output directly to the response
    try:
        outputGenImage.genImage.open("rb")
        outputImage = PIL.Image.open(outputGenImage.genImage)
        outputImage.load()
        outputImage.save(response, "PNG")
    except IOError:
        traceback.print_exc()
        response = HttpResponseServerError("unable to retrieve image")
    finally:
        outputGenImage.genImage.close()

    return response

# redirect view for redirecting a square dimension request 
# to a corresponding width/height request
def requestSquare(request, targSize):
    redirectUrl = reverse('mainapp:request_size', 
                            kwargs={"targWidth":targSize,
                                    "targHeight":targSize})
    # also add the query string to the url
    queryStr = request.META.get("QUERY_STRING", "")
    if queryStr:
        redirectUrl = "%s?%s" % (redirectUrl, queryStr)
    return redirect(redirectUrl, permanent=True) 
