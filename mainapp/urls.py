from django.conf.urls import patterns, url
from mainapp import views

urlpatterns = patterns("",
    url(r"^$", views.requestIndex, name="index"),
    url(r"^gallery/$", views.requestGallery, name="gallery"),
    url(r"^(?P<targWidth>\d+)/(?P<targHeight>\d+)/$", views.requestSize, name="request_size"),

    # redirect single-dimension square requests to 
    # corresponding width/height request
    url(r"^(?P<targSize>\d+)/$", views.requestSquare, name="request_square")
)