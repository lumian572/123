# from django.db import models
#
# from warehouse.models import Evaluate
#
#
# # 定义用户会话信息模型 并定义了一个用户信息表
# class Userinfo(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     username = models.CharField(max_length=32)
#     password = models.CharField(max_length=64)
# class Evaluation(models.Model):
#     eid = models.AutoField(primary_key=True)
#     content = models.TextField(blank=True,null=True)
#     sent_time = models.DateTimeField(blank=True,null=True)
#     user_name = models.CharField(max_length=32,blank=True,null=True)
#     score = models.FloatField(blank=True,null=True)
#     scenery_name = models.CharField(max_length=32,blank=True,null=True)
# class Scenery(models.Model):
#     sid = models.AutoField(primary_key=True)
#     city = models.CharField(max_length=64,blank=True,null=True)
#     people_percent = models.FloatField(blank=True,null=True,max_length=32)
#     play_time = models.DateTimeField(blank=True,null=True,max_length=64)
#     rank = models.FloatField(blank=True,null=True)
#     scenery_name = models.CharField(max_length=64,blank=True,null=True)
#     score = models.FloatField(blank=True,null=True)
#     evaluates = models.ManyToManyField(Evaluate)
#
#

from django.db import models

# Create your models here.


class Userinfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)


class Evaluate(models.Model):
    eid = models.AutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    send_time = models.DateField(blank=True, null=True)
    user_name = models.CharField(max_length=32, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    scenery_name = models.CharField(max_length=32, blank=True, null=True)


class Scenery(models.Model):
    sid = models.AutoField(primary_key=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    people_percent = models.CharField(max_length=32, blank=True, null=True)
    play_time = models.CharField(max_length=64, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    scenery_name = models.CharField(max_length=64, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    evaluates = models.ManyToManyField(Evaluate)


