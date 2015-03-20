from django.contrib import admin
import mainapp.models

class SrcImageAdmin(admin.ModelAdmin):
    list_display = ("imageName", "cxPercent", "cyPercent")
    readonly_fields = ("imageThumb", "imageName")

class GenImageAdmin(admin.ModelAdmin):
    list_display = (
        "imageName", "width", "height", "srcImage", "assignedDate", 
        "createdTimestamp", "createdTimestampISO"
    )
    readonly_fields = (
        "imageThumb", "imageName", "createdTimestamp", "createdTimestampISO"
    )

# Register your models here.
admin.site.register(mainapp.models.SrcImage, SrcImageAdmin)
admin.site.register(mainapp.models.GenImage, GenImageAdmin)