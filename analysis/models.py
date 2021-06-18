from django.db import models


class ReviewTable(models.Model):
    title = models.CharField(max_length=500)
    content = models.CharField(max_length=4000)
    date = models.CharField(max_length=20)
    variant = models.CharField(max_length=1000)
    images = models.CharField(max_length=2083)
    verified = models.CharField(max_length=10)
    author = models.CharField(max_length=300)
    rating = models.FloatField(default=0.0)
    product = models.CharField(max_length=500)
    url = models.CharField(max_length=2083)
    avg_polarity = models.FloatField(default=0.0)
    sentiment = models.CharField(max_length=10, default='No Info')


class ConsecutiveWordsTable(models.Model):
    word_pairs = models.CharField(max_length=1000)
    times = models.IntegerField(default=0)