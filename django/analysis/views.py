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
from textblob import TextBlob
import json

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
        #print(post)
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
            #print(key)
            del_key_list.append(key)
            
    for keys in del_key_list:
        del smt[keys]

    sorted_dict = sorted(smt.items(), key=lambda x: x[1], reverse=True)[0:20]

    post_dict = {
        "post_title_data": sorted_dict
    }

    return render(request, "occurance.html", post_dict)


def sentiment_graph(request):
    data_file = os.path.dirname(os.path.realpath(__file__)) + '\\data.csv'
    df = pd.read_csv(data_file, engine='python')

    for index, row in df.iterrows():
        text = row['content']
        #print(index, text)
        blob = TextBlob(text)
        #print(len(blob.sentences))
        
        avg_pol = 0
        avg_sentiment = 0
        for sentence in blob.sentences:
            #print(len(blob.sentences))
            #print(sentence.sentiment.polarity)
            avg_pol += sentence.sentiment.polarity
        
        avg_sentiment = avg_pol/len(blob.sentences)
        #print(f'Average polarity: {avg_sentiment}')
        
        df.at[index,'avg_polarity'] = avg_sentiment
        
        if avg_sentiment > 0.0:
            df.at[index,'sentiment'] = 'Positive'
        elif avg_sentiment < 0.0:
            df.at[index,'sentiment'] = 'Negative'
        else:
            df.at[index,'sentiment'] = 'Neutral'
    

    file2 = df['sentiment'].values

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
    return response


def positive_df(request):
    data_file = os.path.dirname(os.path.realpath(__file__)) + '\\data.csv'
    df = pd.read_csv(data_file, engine='python')

    for index, row in df.iterrows():
        text = row['content']
        #print(index, text)
        blob = TextBlob(text)
        #print(len(blob.sentences))
        
        avg_pol = 0
        avg_sentiment = 0
        for sentence in blob.sentences:
            #print(len(blob.sentences))
            #print(sentence.sentiment.polarity)
            avg_pol += sentence.sentiment.polarity
        
        avg_sentiment = avg_pol/len(blob.sentences)
        #print(f'Average polarity: {avg_sentiment}')
        
        df.at[index,'avg_polarity'] = avg_sentiment
        
        if avg_sentiment > 0.0:
            df.at[index,'sentiment'] = 'Positive'
        elif avg_sentiment < 0.0:
            df.at[index,'sentiment'] = 'Negative'
        else:
            df.at[index,'sentiment'] = 'Neutral'
    
    pos_df = df.sort_values(by=['avg_polarity'], ascending=False).head(5)

    # parsing the DataFrame in json format.
    json_records = pos_df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    
    #return HttpResponse(pos_df.to_html())
    return data


def negative_df(request):
    data_file = os.path.dirname(os.path.realpath(__file__)) + '\\data.csv'
    df = pd.read_csv(data_file, engine='python')

    for index, row in df.iterrows():
        text = row['content']
        #print(index, text)
        blob = TextBlob(text)
        #print(len(blob.sentences))
        
        avg_pol = 0
        avg_sentiment = 0
        for sentence in blob.sentences:
            #print(len(blob.sentences))
            #print(sentence.sentiment.polarity)
            avg_pol += sentence.sentiment.polarity
        
        avg_sentiment = avg_pol/len(blob.sentences)
        #print(f'Average polarity: {avg_sentiment}')
        
        df.at[index,'avg_polarity'] = avg_sentiment
        
        if avg_sentiment > 0.0:
            df.at[index,'sentiment'] = 'Positive'
        elif avg_sentiment < 0.0:
            df.at[index,'sentiment'] = 'Negative'
        else:
            df.at[index,'sentiment'] = 'Neutral'
    
    neg_df_before = df.sort_values(by=['avg_polarity'], ascending=False).tail(5)

    # parsing the DataFrame in json format.
    neg_df = neg_df_before.sort_values(by=['avg_polarity'])
    json_records = neg_df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    
    #return HttpResponse(neg_df.to_html())
    return data


def sentiment_all(request):
    neg_context = negative_df(request)
    pos_context = positive_df(request)
    return render(request, "sentiment.html", {'p': pos_context,'n': neg_context})