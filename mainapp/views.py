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

MAX_IMAGE_DIM = 5500

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

def regenerateCroppedImage(genImageModel):
    try:
        generateCroppedImage(genImageModel.srcImage, genImageModel.width, 
                             genImageModel.height, genImageModel.assignedDate, 
                             genImageModel=genImageModel)
    except IOError as e:
        print "unable to regenerate image %s" % genImageModel.imageName
        raise e

def generateCroppedImage(srcImageModel, targWidth, targHeight, assignedDate, 
                         genImageModel=None):
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
    cropWidth, cropHeight = croppedImage.size

    # actually generate the model for the generated image, if not already given
    if not genImageModel:
        kwargs = {
            "srcImage": srcImageModel,
            "width": cropWidth, 
            "height": cropHeight
        }
        genImageModel = get_object_or_None(GenImage, **kwargs)
        if not genImageModel:
            genImageModel = GenImage(assignedDate=assignedDate, **kwargs)
            genImageModel.save()

    imageName = "%s-%s_%s" % (cropWidth, cropHeight, srcImageModel.imageName())

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
        return cachedImage

    # in cases where either the image doesn't already exist,
    # generate a new image
    return generateCroppedImage(srcImage, targWidth, targHeight, assignedDate)

# for requests that don't specify a source image to use
def getDefaultGenImage(targWidth, targHeight, allSrcs, numSrcs):
    curDate = datetime.datetime.today().toordinal()
    cachedImage = get_object_or_None(GenImage, width=targWidth, 
                                     height=targHeight, assignedDate=curDate)
    if cachedImage:
        return cachedImage
    
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
    
    # since 0 sized images end up needing to be rendered as at least 1 size
    # anyways, constrain to a minimum of 1px instead of 0px
    targWidth = max(targWidth, 1) 
    targHeight = max(targHeight, 1)

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
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError("unable to retrieve image")

    # convert cropped image into an http response
    response = HttpResponse(content_type="image/jpeg")
    # open the stored image and output directly to the response
    try:
        try:
            outputGenImage.genImage.open("rb")
        # make one attempt to regenerate image if it is missing
        except Exception:
            regenerateCroppedImage(outputGenImage)
            outputGenImage.genImage.open("rb")
        outputImage = PIL.Image.open(outputGenImage.genImage)
        outputImage.load()
        outputImage.save(response, "JPEG")
    except Exception:
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
