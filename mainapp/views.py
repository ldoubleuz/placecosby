from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from mainapp.models import SrcImage
from PIL import Image
import datetime

import cropcosby

MAX_IMAGE_DIM = 5500

# Create your views here.
def requestIndex(request):
    return HttpResponse("hello, I am the index")

# return a randomly chosen index, based on the given size parameters and the
# current day (ie: change what image we display every day)
def getRandomSrcIndex(targWidth, targHeight, numSrcs):
    curDate = datetime.datetime.today().toordinal()

    hashCode = 0
    for hashable in (targWidth, targHeight, curDate):
        hashCode = 33 * hashCode + hash(hashable)
    # for best results, have a prime number of source images
    return hashCode % numSrcs

def parseIntOrNone(num):
    try: 
        return int(num)
    except:
        return None

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

    # determine the index of the src image to use
    numSrcs = allSrcs.count()
    index = parseIntOrNone(request.GET.get("image", None))
    if index is None or index < 0 or index >= numSrcs:
        index = getRandomSrcIndex(targWidth, targHeight, numSrcs)

    # grab SrcImage model and create the cropped version
    srcImageModel = allSrcs[index]

    # open the image before cropping
    try:
        srcImage = Image.open(srcImageModel.image)
    except IOError:
        print "unable to open %s" % srcImageObj.image.url
        srcImageModel.image.close()
        return HttpResponseServerError("unable to retrieve image")

    croppedImage = cropcosby.resizeImage(srcImage, targWidth, targHeight,
                                         srcImageModel.cxPercent, 
                                         srcImageModel.cyPercent)
    srcImageModel.image.close() # don't forget to close!

    # convert cropped image into an http response
    response = HttpResponse(content_type="image/png")
    croppedImage.save(response, "PNG")
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
