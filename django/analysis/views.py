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
import matplotlib.pyplot as plt; plt.rcdefaults()
from collections import Counter
import string
import io
import pandas as pd
import os
import re

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


def common_words(request):
    return render(request, 'commonwords.html')


def display_common_words(request):
    fig = Figure()
    
    data_file = os.path.dirname(os.path.realpath(__file__)) + '\\data.csv'
    db_post = pd.read_csv(data_file, engine='python')
    text_list = db_post['content'].tolist()

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
    # plt.bar(x_n, y_n)
    # deneme

    ax.bar(x_n, y_n,width=0.4)
    #Now the trick is here.
    #plt.text() , you need to give (x,y) location , where you want to put the numbers,
    #So here index will give you x pos and data+1 will provide a little gap in y axis.
    for index,data in enumerate(y_n):
        plt.text(x=index , y =data+0.2 , s=f"{data}" , fontdict=dict(fontsize=10))

    # deneme son
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Most Common Words')

    # plt.savefig('example.png')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
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
    data_file = os.path.dirname(os.path.realpath(__file__)) + '\\data.csv'
    df = pd.read_csv(data_file, engine='python')
    posts = df['content'].values

    new_post = ''
    words = ''
    for post in posts:
        post = re.sub('\s', ' ', post)
        print(post)
        new_post += post + ' '
        for token in word_tokenize(post):
            token = token.lower()
            table = str.maketrans('', '', string.punctuation)
            token = token.translate(table)
            stop_words = set(stopwords.words('english'))
            if token not in stop_words and len(token) > 1 and token != 'nt':
                words += token + " "
        words += ". "
    
    smt = freq(words)

    del_key_list=[]
    for key in smt:
        if "." in key:
            print(key)
            del_key_list.append(key)
            
    for keys in del_key_list:
        del smt[keys]

    sorted_dict = sorted(smt.items(), key=lambda x: x[1], reverse=True)[0:20]

    post_dict = {
        "post_title_data": sorted_dict
    }

    return render(request, "occurance.html", post_dict)