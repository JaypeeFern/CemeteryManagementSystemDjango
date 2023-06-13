from django.shortcuts import render
from .models import DeceasedInformation

# Create your views here.

def RenderDeceasedSearch(request):
    return render(request, "search/index.html", {
        'data': DeceasedInformation.objects.all()
    })
   
def tables(request):
    return render(request, "search/tables.html")
 