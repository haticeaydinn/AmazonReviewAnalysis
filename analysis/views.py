from django.http.response import HttpResponse
from django.shortcuts import render
from .get_reviews import get_product_reviews
import emoji
from matplotlib.figure import Figure
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
import matplotlib.pyplot as plt; plt.rcdefaults()
from collections import Counter
import string
import io
import pandas as pd
import os
import re
from textblob import TextBlob
import json
from .models import ReviewTableNew, ProductTable
from django_q.tasks import async_task
import psycopg2
from django.db.models import Sum
from django.db import close_old_connections
from django.db import connections

# Create your views here.
def index(request):
    #return HttpResponse('Enter comments URL from Amazon.com: ')
    #amazonurl= request.POST.get('Amazonurl')
    prod_id = request.POST.get('item_id')
    submitbutton= request.POST.get('Submit')
    products = ProductTable.objects.all()
    context= {'prod_id': prod_id, 'products': products, 'submitbutton': submitbutton}
    global val
    def val():
        return prod_id

    try:
        if request.method =='POST':
            # get 1000 reviews from amazon
            print("Data collection is starting!")
            # async_task(write_table_v1, text, user, s_id, date)
            #get_product_reviews(amazonurl)
            #close_old_connections()
            for conn in connections.all():
                conn.close()
            #async_task(get_product_reviews, amazonurl)
            for conn in connections.all():
                conn.close()
            print("Data collection is done!")

        return render(request, 'index.html', context)
    except psycopg2.OperationalError:
        error_message = "There are lots of connection to db right now. Please contact to administrator or send an email to 'hatice3178@yahoo.com.tr'. Thank you!"
        return HttpResponse(error_message, content_type="text/plain")

def common_words(request):
    return render(request, 'commonwords.html')


def display_common_words(request):
    fig = Figure()

    product_id = val()
    print(product_id)
    
    for conn in connections.all():
        conn.close()
    db_post = ReviewTableNew.objects.filter(asin=product_id)
    for conn in connections.all():
        conn.close()

    text_list = db_post.values_list('reviewText', flat=True)

    my_string = ''
    for element in text_list:
        my_string += element + ' '
    
    tokens = word_tokenize(my_string)

    # convert to lower case
    tokens = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if (not w in stop_words and  w != 'nt')]
    # word_freq = Counter(nouns)
    word_freq = Counter(words)

    common_nouns = word_freq.most_common(10)

    x_n = []
    for i in range(len(common_nouns)):
        word = common_nouns[i][0]
        x_n.append(word)

    y_n = []
    for i in range(len(common_nouns)):
        freq = common_nouns[i][1]
        y_n.append(freq)

    plt.switch_backend('agg')
    f, ax = plt.subplots(figsize=(9, 4))  # set the size that you'd like (width, height)

    ax.bar(x_n, y_n,width=0.4)
    #plt.text() , you need to give (x,y) location , where you want to put the numbers,
    #So here index will give you x pos and data+1 will provide a little gap in y axis.
    for index,data in enumerate(y_n):
        plt.text(x=index , y =data+0.2 , s=f"{data}" , fontdict=dict(fontsize=10))

    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Most Common Words')

    # plt.savefig('example.png')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    for conn in connections.all():
        conn.close()
    return response


def freq(input_string):
    '''
    This function is from https://stackoverflow.com/questions/33723089/how-to-get-consecutive-word-count-of-a-string-python
    '''
    freq = {}
    words = input_string.split()
    if len(words) == 1:
        return freq

    for idx, word in enumerate(words):
        if idx+1 < len(words):
            word_pair = (word, words[idx+1])
            if word_pair in freq:
                freq[word_pair] += 1
            else:
                freq[word_pair] = 1

    return freq


def cooccurance_words(request):
    product_id = val()

    for conn in connections.all():
        conn.close()
    df = ReviewTableNew.objects.filter(asin=product_id)
    for conn in connections.all():
        conn.close()

    posts = df.values_list('reviewText', flat=True)

    new_post = ''
    words = ''
    for post in posts:
        post = re.sub('\s', ' ', post)
        new_post += post + ' '
        for token in word_tokenize(post):
            token = token.lower()
            table = str.maketrans('', '', string.punctuation)
            token = token.translate(table)
            stop_words = set(stopwords.words('english'))
            if token not in stop_words and len(token) > 1 and token != 'nt':
                words += token + " "
        words += ". "
    
    #smt = freq(words)
    finder = BigramCollocationFinder.from_words(word_tokenize(words))
    #print(type(finder))

    element_dict = {}
    for k,v in finder.ngram_fd.items():
        if "." not in k:
            element_dict[k] = v
    

    sorted_dict = sorted(element_dict.items(), key=lambda x: x[1], reverse=True)[0:20]

    bigram_word_list = []
    freq_list = []
    for data,freq in sorted_dict:
        bigram_words = data[0] + " " + data[1]
        bigram_word_list.append(bigram_words)
        freq_list.append(freq)

    fig = Figure()
    plt.switch_backend('agg')

    f, ax = plt.subplots(figsize=(15, 10))  # set the size that you'd like (width, height)

    Words = bigram_word_list
    Freq = freq_list

    plt.style.use('ggplot')

    for i, v in enumerate(Freq):
        plt.text(v, i, " "+str(v), color='blue', va='center', fontweight='bold')

    plt.barh(Words, Freq)
    plt.title('Bigram Words Graph')
    plt.ylabel('Words Group')
    plt.xlabel('Frequency')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    for conn in connections.all():
        conn.close()
    return response

    #return render(request, "occurance.html", post_dict)


def cooccurance_words_view(request):
    product_id = val()
    rev_qs = ReviewTableNew.objects.filter(asin=product_id)
    reviews_no = len(rev_qs)
    product_name_list = ProductTable.objects.filter(asin=product_id).values_list('title', flat = True)
    product_name_str = list(product_name_list)[0]
    product_name = str(product_name_str)

    context = {
        'reviews_no': reviews_no,
        'prod_name': product_name
    }
    
    return render(request, 'occurance.html', context)


def sentiment_graph(request):
    product_id = val()

    for conn in connections.all():
        conn.close()
    df = ReviewTableNew.objects.filter(asin=product_id)
    for conn in connections.all():
        conn.close()

    file2 = df.values_list('sentiment', flat=True)

    pos_count = 0
    neg_count = 0
    neut_count = 0

    for line in file2:
        if line == 'Positive':
            pos_count += 1
        elif line == 'Negative':
            neg_count += 1
        elif line == 'Neutral':
            neut_count += 1

    plt.switch_backend('agg')
    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [pos_count, neg_count, neut_count]
    colors = ['#00cc00','#ff0000','#ffcc99']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, colors=colors)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    # plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    for conn in connections.all():
        conn.close()
    return response


def positive_df(request):
    product_id = val()

    for conn in connections.all():
        conn.close()
    data = ReviewTableNew.objects.filter(asin=product_id).order_by('-avg_polarity')[:5]
    for conn in connections.all():
        conn.close()
    
    return data


def negative_df(request):
    product_id = val()
    
    for conn in connections.all():
        conn.close()
    data = ReviewTableNew.objects.filter(asin=product_id).order_by('avg_polarity')[:5]
    for conn in connections.all():
        conn.close()
    return data


def sentiment_all(request):
    for conn in connections.all():
        conn.close()
    neg_context = negative_df(request)
    pos_context = positive_df(request)
    for conn in connections.all():
        conn.close()
    return render(request, "sentiment.html", {'p': pos_context,'n': neg_context})


def filter(request):
    for conn in connections.all():
        conn.close()
    qs = ReviewTableNew.objects.all()
    for conn in connections.all():
        conn.close()
    title_contains_query = request.GET.get('content')
    verified = request.GET.get('verified')
    not_verified = request.GET.get('notVerified')
    prod_id = request.GET.get('item_id')

    if title_contains_query != '' and title_contains_query is not None:
        for conn in connections.all():
            conn.close()
        qs = qs.filter(reviewText__icontains=title_contains_query)
        for conn in connections.all():
            conn.close()

    if prod_id != '' and prod_id is not None and prod_id != 'Choose':
        for conn in connections.all():
            conn.close()
        qs = qs.filter(asin=prod_id)
        for conn in connections.all():
            conn.close()


    if verified == 'on':
        for conn in connections.all():
            conn.close()
        qs = qs.filter(verified='True')
        for conn in connections.all():
            conn.close()
    elif not_verified == 'on':
        for conn in connections.all():
            conn.close()
        qs = qs.filter(verified='False')
        for conn in connections.all():
            conn.close()

    return qs

def FilterView(request):
    qs = filter(request)
    for conn in connections.all():
        conn.close()
    if qs:
        total_counter = len(qs)
        total_polarity = qs.aggregate(Sum('avg_polarity'))
        print(type(total_polarity))
        print(total_polarity)
        avg_polarity = list(total_polarity.values())[0] / total_counter
        if avg_polarity > 0.0:
            sentiment = 'Users have positive idea about this product.'
        elif avg_polarity == 0.0:
            sentiment = 'Users have neutral idea about this product.'
        else:
            sentiment = 'Users have negative idea about this product.'
    else:
        total_counter = 0
        sentiment = 'No info!'
    #products = ProductTable.objects.all().values('title')
    products = ProductTable.objects.all()
    prod_id = request.GET.get('item_id')
    if prod_id != '' and prod_id is not None and prod_id != 'Choose':
        product_name_list = ProductTable.objects.filter(asin=prod_id).values_list('title', flat = True)
        product_name_str = list(product_name_list)[0]
        product_name = 'Product name is ' + str(product_name_str)
        product_img_url_qs = ProductTable.objects.filter(asin=prod_id).values_list('imageURLHighRes', flat = True)
        product_img_url_list = list(product_img_url_qs)[0]
        product_img_url = str(product_img_url_list)[2:-2]
        product_amazon_url_list = ProductTable.objects.filter(asin=prod_id).values_list('asin', flat = True)
        product_amazon_url_str = list(product_amazon_url_list)[0]
        product_amazon_url = 'https://www.amazon.com/dp/' + str(product_amazon_url_str)
    else:
        product_name = 'No product is searched yet!'
        product_img_url = 'http://toolsandtoys.net/wp-content/uploads/2016/07/Canopy-hero.jpg'
        product_amazon_url = 'https://www.amazon.com'
    context = {
        'queryset': qs,
        'total_count': total_counter,
        'sentiment': sentiment,
        'products': products,
        'product_img_url': product_img_url,
        'product_name': product_name,
        'product_amazon_url': product_amazon_url
    }

    for conn in connections.all():
        conn.close()

    return render(request, "filtering.html", context)