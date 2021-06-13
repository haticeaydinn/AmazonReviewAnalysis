from django.http.response import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return HttpResponse('Enter comments URL from Amazon.com: ')
    #return render(request, 'index.html', {'data':data, 'date_interval':date_interval, 'user_selected': user_selected})