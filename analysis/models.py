from django.db import models


class ReviewTable(models.Model):
    title = models.CharField(max_length=500)
    content = models.CharField(max_length=6000)
    date = models.CharField(max_length=20)
    variant = models.CharField(max_length=1000, null=True)
    images = models.CharField(max_length=2083)
    verified = models.CharField(max_length=10)
    author = models.CharField(max_length=300)
    rating = models.FloatField(default=0.0)
    product = models.CharField(max_length=500)
    url = models.CharField(max_length=2083)
    avg_polarity = models.FloatField(default=0.0)
    sentiment = models.CharField(max_length=10, default='No Info')
    product_id = models.CharField(max_length=50, default='No Product')


class ReviewTableNew(models.Model):
    overall = models.IntegerField()
    verified = models.CharField(max_length=10)
    reviewTime = models.CharField(max_length=20)
    reviewerID = models.CharField(max_length=100)
    asin = models.CharField(max_length=50)
    style = models.CharField(max_length=1000, null=True)
    reviewerName = models.CharField(max_length=300)
    reviewText = models.CharField(max_length=11000)
    summary = models.CharField(max_length=500)
    unixReviewTime = models.DateField()
    vote = models.FloatField(null=True)
    image = models.CharField(max_length=2083, null=True)
    avg_polarity = models.FloatField(default=0.0, null=True)
    sentiment = models.CharField(max_length=10, default='No Info', null=True)
    pos_sentence_rate = models.FloatField(default=0.0, null=True)
    neg_sentence_rate = models.FloatField(default=0.0, null=True)


class ProductTable(models.Model):
    title = models.CharField(max_length=1000)
    main_cat = models.CharField(max_length=50)
    price = models.CharField(max_length=10, null=True)
    asin = models.CharField(max_length=50)
    imageURLHighRes = models.CharField(max_length=2000)