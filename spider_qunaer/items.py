# # Define here the models for your scraped items
# #
# # See documentation in:
# # https://docs.scrapy.org/en/latest/topics/items.html
#
# import scrapy
# from warehouse.models import Scenery,Evaluate
# from scrapy_djangoitem import DjangoItem
#
# # class SpiderSceneryItem(DjangoItem.Item):
# #     django_model = Scenery
# # class SpiderEvaluteItem(DjangoItem):
# #     django_model = Evaluate
#
# # spider_qunaer/items.py
# import os
# import django
#
# # 初始化 Django 环境
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunan_web.settings')
# django.setup()
#
# # 现在可以安全导入 Django 模型
# from scrapy.item import Item, Field
# from warehouse.models import Scenery, Evaluate
#
# # 定义 Scrapy Items
# class SpiderSceneryItem(Item):
#     scenery_name = Field()
#     rank = Field()
#     people_percent = Field()
#     score = Field()
#     play_time = Field()
#     city = Field()
#
# class SpiderEvaluteItem(Item):
#     content = Field()
#     send_time = Field()
#     user_name = Field()
#     score = Field()
#     scenery_name = Field()
#

# 此前都是

# spider_qunaer/items.py
import scrapy
from scrapy.item import Item, Field

class SpiderSceneryItem(Item):
    scenery_name = Field()
    rank = Field()
    people_percent = Field()
    score = Field()
    play_time = Field()
    city = Field()
    address = Field()  # 新增地址字段

class SpiderEvaluteItem(Item):
    content = Field()
    send_time = Field()
    user_name = Field()
    score = Field()
    scenery_name = Field()