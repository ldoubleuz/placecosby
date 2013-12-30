from django.core.management.base import BaseCommand, CommandError
from mainapp.models import SrcImage
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
import os, json

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

        for imageName in imageFilenames:
            # read center stats from json
            if imageName not in centerPercents:
                continue
            [cxPercent, cyPercent] = centerPercents[imageName]
            imagePath = os.path.join(IMAGE_DIR, imageName)

            # create the new SrcImage object
            newImageObj = SrcImage(cxPercent=cxPercent, cyPercent=cyPercent)

            # actually open and save the image file contents to the new object
            with open(imagePath, "rb") as imageFile:
                self.stdout.write("saving %s..." % imageName, ending="")
                # use save=True to also save the SrcImage object
                newImageObj.image.save(imageName, File(imageFile), save=True)
                self.stdout.write("saved to %s!" % newImageObj.image.url)