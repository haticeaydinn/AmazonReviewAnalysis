import os
from selectorlib import Extractor
import requests 
import json
import csv
from dateutil import parser as dateparser
import emoji
from .models import ReviewTable


def scrape(url):    
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    # Create an Extractor by reading from the YAML file
    selector_file = os.path.dirname(os.path.realpath(__file__)) + '/selectors.yml'
    e = Extractor.from_yaml_file(selector_file) 
    return e.extract(r.text)


def get_product_reviews(url_example):
    print(url_example)
    # slice the url
    url_base = url_example.split('/')
    url_splitted = 'https://www.amazon.com/' + url_base[3] + '/product-reviews/' + url_base[5] + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
    #print(url_splitted)
    # end slicing
    for page_num in range(1,51):
        url_new = url_splitted + '&pageNumber=' + str(page_num)
        #print(url_new + '\n')
        data = scrape(url_new) 
        if data:
            if data['reviews'] == None:
                print("No page founded!!!")
                continue
            else:
                for r in data['reviews']:
                    r["product"] = data["product_title"]
                    r['url'] = url_new
                    if 'verified' in r:
                        if r['verified'] == None:
                            r['verified'] = 'No'
                        else:
                            if 'Verified Purchase' in r['verified']:
                                r['verified'] = 'Yes'
                            else:
                                r['verified'] = 'Yes'
                    if r['rating'] == None:
                        r['rating'] = 0.0
                    else:
                        r['rating'] = r['rating'].split(' out of')[0]
                    date_posted = r['date'].split('on ')[-1]
                    if r['images']:
                        r['images'] = "\n".join(r['images'])
                    r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
                    reviews_content = r['content']
                    r['content'] = emoji.get_emoji_regexp().sub(u'', reviews_content)
                    my_str = r['author']
                    #encode() method
                    strencode = my_str.encode("ascii", "ignore")               
                    #decode() method
                    strdecode = strencode.decode()
                    strdecode_str = str(strdecode)
                    r['author'] = strdecode_str
                    reviews_title = r['title']
                    r['title'] = emoji.get_emoji_regexp().sub(u'', reviews_title)
                    # writer.writerow(r)
                    # write to postgres
                    a_review = ReviewTable()
                    a_review.title = r['title']
                    a_review.content = r['content']
                    a_review.date = r['date']
                    a_review.variant = r['variant']
                    if r['images']:
                        a_review.images = r['images']
                    a_review.verified = r['verified']
                    a_review.author = r['author']
                    a_review.rating = r['rating']
                    a_review.product = data["product_title"]
                    a_review.url = r['url']
                    a_review.product_id = url_base[5]
                    a_review.save()


def get_product_reviews_csv(url_example):
    print(url_example)
    data_file = os.path.dirname(os.path.realpath(__file__)) + '/data.csv'
    print(data_file)
    with open(data_file,'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["title","content","date","variant","images","verified","author","rating","product","url"],quoting=csv.QUOTE_ALL)
        writer.writeheader()
        # slice the url
        url_base = url_example.split('/')
        url_splitted = 'https://www.amazon.com/' + url_base[3] + '/product-reviews/' + url_base[5] + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
        #print(url_splitted)
        # end slicing
        for page_num in range(1,51):
            url_new = url_splitted + '&pageNumber=' + str(page_num)
            #print(url_new + '\n')
            data = scrape(url_new) 
            if data:
                if data['reviews'] == None:
                    print("No page founded!!!")
                    continue
                else:
                    for r in data['reviews']:
                        r["product"] = data["product_title"]
                        r['url'] = url_new
                        if 'verified' in r:
                            if r['verified'] == None:
                                r['verified'] = 'No'
                            else:
                                if 'Verified Purchase' in r['verified']:
                                    r['verified'] = 'Yes'
                                else:
                                    r['verified'] = 'Yes'
                        r['rating'] = r['rating'].split(' out of')[0]
                        date_posted = r['date'].split('on ')[-1]
                        if r['images']:
                            r['images'] = "\n".join(r['images'])
                        r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
                        reviews_content = r['content']
                        r['content'] = emoji.get_emoji_regexp().sub(u'', reviews_content)
                        my_str = r['author']
                        #encode() method
                        strencode = my_str.encode("ascii", "ignore")               
                        #decode() method
                        strdecode = strencode.decode()
                        strdecode_str = str(strdecode)
                        r['author'] = strdecode_str
                        reviews_title = r['title']
                        r['title'] = emoji.get_emoji_regexp().sub(u'', reviews_title)
                        writer.writerow(r)
                        # write to postgres
                        a_review = ReviewTable()
                        a_review.title = r['title']
                        a_review.content = r['content']
                        a_review.date = r['date']
                        a_review.variant = r['variant']
                        if r['images']:
                            a_review.images = r['images']
                        a_review.verified = r['verified']
                        a_review.author = r['author']
                        a_review.rating = r['rating']
                        a_review.product = data["product_title"]
                        a_review.url = r['url']
                        a_review.save()