from django.db import models
from django.core.exceptions import ValidationError
from django.utils.html import format_html

import os

# Create your models here.
class SrcImage(models.Model):
    image = models.ImageField(upload_to="src")
    cxPercent = models.FloatField()
    cyPercent = models.FloatField()

    def imageName(self):
        return os.path.basename(self.image.url)
    imageName.admin_order_field = "image"

    def imageThumb(self):
        return format_html('<img src="%s" style="max-width:150px;max-height:150px"/>' % self.image.url)
    imageThumb.allow_tags = True

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