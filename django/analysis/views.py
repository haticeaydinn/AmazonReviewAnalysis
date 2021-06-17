from django.http.response import HttpResponse
from django.shortcuts import render
from .get_reviews import get_product_reviews

# Create your views here.
def index(request):
    #return HttpResponse('Enter comments URL from Amazon.com: ')
    firstname= request.POST.get('Firstname')
    submitbutton= request.POST.get('Submit')
    context= {'firstname': firstname, 'submitbutton': submitbutton}

    return render(request, 'index.html', context)
    #return render(request, 'index.html')