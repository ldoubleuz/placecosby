from django.core.management.base import BaseCommand, CommandError
from mainapp.models import SrcImage
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile 
import os
import json
import PIL
import StringIO

COMMAND_DIR = os.path.dirname(os.path.realpath(__file__))
MANAGEMENT_DIR = os.path.dirname(COMMAND_DIR)
IMAGE_DIR = os.path.join(MANAGEMENT_DIR, "src_images")

class Command(BaseCommand):
    help = "Regenerates the source images in the database, using the image_centers.json file"

    def handle(self, *args, **options):
        self.stdout.write("clearing all old source images...", ending="")
        # clear all old images
        SrcImage.objects.all().delete()
        self.stdout.write("clearing done!")

        # read image center information from json file
        with open(os.path.join(MANAGEMENT_DIR, "image_centers.json"), "r") as file:
            centerPercents = json.load(file)

        imageFilenames = os.listdir(IMAGE_DIR)

        for origImageName in imageFilenames:
            # read center stats from json
            if origImageName not in centerPercents:
                continue
            [cxPercent, cyPercent] = centerPercents[origImageName]
            imagePath = os.path.join(IMAGE_DIR, origImageName)

            # convert copy of image to jpg
            newImageName = "%s.jpg" % os.path.splitext(origImageName)[0]
            newImageObj = PIL.Image.open(imagePath).copy().convert("RGB")

            # open jpg as file for saving
            imageIO = StringIO.StringIO()
            newImageObj.save(imageIO, format="JPEG") # save to the buffer
            imageFile = ContentFile(imageIO.getvalue())

            # create the new SrcImage object
            newImageModel = SrcImage(cxPercent=cxPercent, cyPercent=cyPercent)

            # save the image file contents to the new object
            self.stdout.write("saving %s..." % origImageName, ending="")
            # use save=True to also save the SrcImage object
            newImageModel.image.save(newImageName, imageFile, save=True)
            self.stdout.write("saved to %s!" % newImageModel.image.url)