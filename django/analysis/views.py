from django.http.response import HttpResponse
from django.shortcuts import render
from .get_reviews import get_product_reviews

# Create your views here.
def index(request):
    #return HttpResponse('Enter comments URL from Amazon.com: ')
    amazonurl= request.POST.get('Amazonurl')
    submitbutton= request.POST.get('Submit')
    context= {'amazonurl': amazonurl, 'submitbutton': submitbutton}

    if request.method =='POST':
        # get 1000 reviews from amazon
        print("Data collection is starting!")
        get_product_reviews(amazonurl)
        print("Data collection is done!")

    return render(request, 'index.html', context)
    #return render(request, 'index.html')