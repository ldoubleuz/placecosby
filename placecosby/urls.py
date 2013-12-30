from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^", include("mainapp.urls", namespace="mainapp"))
)

# serve source media files in debug mode so that we can see them during 
# development, but not when live
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)