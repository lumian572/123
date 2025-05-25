# # Define your item pipelines here
# #
# # Don't forget to add your pipeline to the ITEM_PIPELINES setting
# # See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#
#
# # useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
#
#
# class SpiderQunaerPipeline:
#     def process_item(self, item, spider):
#         item.save()
#         return item
#
# # spider_qunaer/pipelines.py
# from warehouse.models import Scenery, Evaluate
#
# class SpiderQunaerPipeline:
#     def process_item(self, item, spider):
#         if isinstance(item, dict):  # 如果是普通字典
#             if 'scenery_name' in item:  # 风景项
#                 Scenery.objects.create(
#                     scenery_name=item.get('scenery_name'),
#                     rank=item.get('rank'),
#                     people_percent=item.get('people_percent'),
#                     score=item.get('score'),
#                     play_time=item.get('play_time'),
#                     city=item.get('city')
#                 )
#             elif 'content' in item:  # 评论项
#                 Evaluate.objects.create(
#                     content=item.get('content'),
#                     send_time=item.get('send_time'),
#                     user_name=item.get('user_name'),
#                     score=item.get('score'),
#                     scenery_name=item.get('scenery_name')
#                 )
#         return item
#
#
# 此前都是
#

# spider_qunaer/pipelines.py
from warehouse.models import Scenery, Evaluate
from itemadapter import ItemAdapter

class SpiderQunaerPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'scenery_name' in adapter:  # 风景项
            Scenery.objects.create(
                scenery_name=adapter.get('scenery_name'),
                rank=adapter.get('rank'),
                people_percent=adapter.get('people_percent'),
                score=adapter.get('score'),
                play_time=adapter.get('play_time'),
                city=adapter.get('city'),
                address=adapter.get('address')  # 新增地址字段
            )
        elif 'content' in adapter:  # 评论项
            # 修正字段名称为 date
            Evaluate.objects.create(
                content=adapter.get('content'),
                send_time=adapter.get('date'),  # 修改为 date
                user_name=adapter.get('user_name'),
                score=adapter.get('score'),
                scenery_name=adapter.get('scenery_name')
            )
        return item