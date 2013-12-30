from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

# Create your views here.
def requestIndex(request):
    return HttpResponse("hello, I am the index")

def requestSize(request, targWidth, targHeight):
    print request.GET
    return HttpResponse("Size requested: (%s, %s)" % (targWidth, targHeight))

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
