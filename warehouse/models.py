from django.db import models

# Create your models here.





class Evaluate(models.Model):
    eid = models.AutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    send_time = models.DateField(blank=True, null=True)
    user_name = models.CharField(max_length=32, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    scenery_name = models.CharField(max_length=32, blank=True, null=True)


class Scene(models.Model):
    sid = models.AutoField(primary_key=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    people_percent = models.CharField(max_length=32, blank=True, null=True)
    play_time = models.CharField(max_length=64, blank=True, null=True)
    rank = models.FloatField(blank=True, null=True)
    scenery_name = models.CharField(max_length=64, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    evaluate = models.ManyToManyField(Evaluate)



class Spiderlog(models.Model):
    id = models.AutoField(primary_key=True)
    spider_time = models.DateTimeField(auto_now_add=True)