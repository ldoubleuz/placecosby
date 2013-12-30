from django.contrib import admin
import mainapp.models

class SrcImageAdmin(admin.ModelAdmin):
    list_display = ("imageName", "cxPercent", "cyPercent")
    readonly_fields = ("imageThumb",)

# Register your models here.
admin.site.register(mainapp.models.SrcImage, SrcImageAdmin)