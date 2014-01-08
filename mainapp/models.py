from django.db import models
from django.core.exceptions import ValidationError
from django.utils.html import format_html

import os

def fileExists(fileField):
    exists = True
    try:
        fileField.open()
    except IOError:
        exists = False
    finally:
        fileField.close()
    return exists

# model for a source image to be used for image generation
class SrcImage(models.Model):
    image = models.ImageField(upload_to="src")
    cxPercent = models.FloatField()
    cyPercent = models.FloatField()

    def imageName(self):
        return os.path.basename(self.image.url).split("?")[0]
    imageName.admin_order_field = "image"

    def imageThumb(self):
        return format_html('<img src="%s" style="max-width:150px;max-height:150px"/>' % self.image.url)
    imageThumb.allow_tags = True

    def imageExists(self):
        return fileExists(self.image)

    def __unicode__(self):
        return self.imageName()

    def clean(self):
        if self.cxPercent < 0 or self.cxPercent > 1:
            raise ValidationError("Center x percent must be a fraction"
                                  " between 0 and 1")
        if self.cyPercent < 0 or self.cyPercent > 1:
            raise ValidationError("Center y percent must be a fraction"
                                  " between 0 and 1")

    class Meta:
        ordering = ["image"]

# model to be used for a generated/cropped image
class GenImage(models.Model):
    # the generated image itself
    genImage = models.ImageField(upload_to="generated", 
                                 width_field="width", height_field="height")

    # the dimensions of the generated image
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    # the ordinal date this image has been assigned to be the default for,
    # such that requests for these dimensions on this date will always return
    # this image
    assignedDate = models.IntegerField(null=True, blank=True)

    # the SrcImage this image was created from
    srcImage = models.ForeignKey("SrcImage", related_name="generatedImages")

    def imageName(self):
        return os.path.basename(self.genImage.url).split("?")[0]
    imageName.admin_order_field = "genImage"

    def imageThumb(self):
        return format_html('<img src="%s" style="max-width:150px;max-height:150px"/>' % self.genImage.url)
    imageThumb.allow_tags = True

    def imageExists(self):
        return fileExists(self.genImage)

    class Meta:
        ordering = ["-assignedDate", "srcImage", "width", "height"]