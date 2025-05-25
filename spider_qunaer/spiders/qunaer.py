# from copy import deepcopy
# import scrapy
# import json
# import logging
#
# # 初始化Django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunan_web.settings')
# django.setup()
#
# # 导入Django模型
# from warehouse.models import Scenery, Spiderlog, Evaluate
# from spider_qunaer import items
#
#
# class QunaerSpider(scrapy.Spider):
#     name = "qunaer"
#     start_urls = ["https://travel.qunar.com/p-cs300022-changsha-jingdian"]
#     page_num = 1
#     max_pages = 10  # 定义最大页数，便于维护
#
#     custom_settings = {
#         'LOG_LEVEL': 'DEBUG',  # 调试模式
#         'DOWNLOAD_DELAY': 2,  # 下载延迟，避免被封
#         'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机延迟
#     }
#
#     async def start(self):
#         self.spider_log = Spiderlog.objects.create()
#         yield scrapy.Request(self.start_urls[0], callback=self.parse)
#
#     def parse(self, response):
#         # 仅在响应为HTML时解析内容
#         if response.headers.get('Content-Type', b'').startswith(b'text/html'):
#             item_scenery = items.SpiderSceneryItem()
#
#             # 更新景点列表XPath，适应新页面结构
#             scenery_list = response.xpath('//div[contains(@class, "list_item") and contains(@class, "js_list_item")]')
#             self.logger.info(f"Page {self.page_num}: Found {len(scenery_list)} scenic spots")
#
#             if not scenery_list:
#                 self.logger.warning("No scenic spots found, check XPath selector")
#                 self.logger.debug(f"Page content sample: {response.text[:500]}")
#
#             for scenery in scenery_list:
#                 # 更新景点名称XPath
#                 scenery_name = scenery.xpath('.//h3/a/text()').get()
#                 if not scenery_name:
#                     self.logger.debug("Scenery name not found, skipping item")
#                     continue
#
#                 item_scenery["scenery_name"] = scenery_name.strip()
#
#                 # 更新排名信息XPath
#                 rank = scenery.xpath('.//span[@class="ranking"]/text()').get()
#                 item_scenery["rank"] = rank.strip() if rank else None
#
#                 # 更新热度信息XPath
#                 people_percent = scenery.xpath('.//div[contains(@class, "hot_num")]/span/text()').get()
#                 item_scenery["people_percent"] = people_percent.strip() if people_percent else None
#
#                 # 更新详情页URL
#                 detail_url = scenery.xpath('./a/@href').get()
#
#                 # 调试输出，确认提取的数据
#                 self.logger.debug(f"Extracted: {scenery_name}, Rank: {rank}, URL: {detail_url}")
#
#                 if detail_url:
#                     # 暂时注释掉数据库检查，便于调试
#                     # if not Scenery.objects.filter(scenery_name=scenery_name).exists():
#                     yield scrapy.Request(
#                         detail_url,
#                         callback=self.get_detail,
#                         meta={"item_scenery": deepcopy(item_scenery)}
#                     )
#
#         # 分页逻辑保持不变
#         if self.page_num < self.max_pages:
#             self.page_num += 1
#             next_page = f"{self.start_urls[0]}-1-{self.page_num}"
#             self.logger.info(f"Requesting page {self.page_num}: {next_page}")
#             yield scrapy.Request(next_page, callback=self.parse)
#         else:
#             self.logger.info("Reached max page limit")
#
#     def get_detail(self, response):
#         item_scenery = response.meta["item_scenery"]
#         content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore')
#
#         self.logger.debug(f"Parsing detail page: {response.url}")
#
#         if 'application/json' in content_type:
#             try:
#                 data = response.json()
#                 item_scenery["score"] = data.get('score', 0.0)
#                 self.logger.debug(f"JSON data parsed: {data.get('name')}, Score: {item_scenery['score']}")
#             except json.JSONDecodeError:
#                 self.logger.error(f"JSON decode error in {response.url}")
#                 return
#         else:
#             # 更新评分XPath
#             score = response.xpath(
#                 '//div[contains(@class, "mp-description")]//span[contains(@class, "score")]/text()').get()
#             item_scenery["score"] = float(score) if score else 0.0
#
#             # 更新游玩时间XPath
#             play_time = response.xpath('//div[contains(@class, "time")]/text()').get()
#             item_scenery["play_time"] = play_time.split("：")[-1].strip() if play_time else None
#
#             # 更新城市信息XPath
#             city = response.xpath('//td[@class="td_l"]/dl[1]/dd/span/text()').get() or response.xpath(
#                 '//div[contains(@class, "mp-baseinfo")]//dd[1]/span/text()').get()
#             item_scenery["city"] = city.strip() if city else None
#
#             # 更新景点地址XPath
#             address = response.xpath('//td[@class="td_l"]/dl[2]/dd/span/text()').get() or response.xpath(
#                 '//div[contains(@class, "mp-baseinfo")]//dd[2]/span/text()').get()
#             item_scenery["address"] = address.strip() if address else None
#
#         if not item_scenery["scenery_name"]:
#             self.logger.warning(f"Skipping invalid item from {response.url}")
#             return
#
#         self.logger.info(f"Scraped item: {item_scenery['scenery_name']}, Score: {item_scenery['score']}")
#         yield item_scenery
#
#         # 爬取评论
#         self.crawl_comments(response, item_scenery)
#
#     def crawl_comments(self, response, item_scenery):
#         # 更新评论页XPath
#         comment_pages = response.xpath('//div[@class="n_paging"]/a/@href').getall()
#         self.logger.info(f"Found {len(comment_pages)} comment pages for {item_scenery['scenery_name']}")
#
#         for i, comment_url in enumerate(comment_pages):
#             if i < 4:  # 只爬取前4页评论，避免抓取过多
#                 self.logger.debug(f"Requesting comment page {i + 1}: {comment_url}")
#                 yield scrapy.Request(
#                     comment_url,
#                     callback=self.get_evaluate,
#                     meta={"item_scenery": deepcopy(item_scenery)}
#                 )
#
#     def get_evaluate(self, response):
#         item_scenery = response.meta["item_scenery"]
#
#         # 更新评论列表XPath
#         comment_list = response.xpath('//div[contains(@class, "comment_item")]')
#         self.logger.info(f"Found {len(comment_list)} comments on {response.url}")
#
#         for comment in comment_list:
#             item_evaluate = items.SpiderEvaluateItem()
#
#             # 提取评论信息
#             item_evaluate["scenery_name"] = item_scenery["scenery_name"]
#             item_evaluate["user_name"] = comment.xpath('.//div[@class="user_name"]/text()').get().strip()
#             item_evaluate["content"] = comment.xpath('.//div[@class="comment_txt"]/text()').get().strip()
#             item_evaluate["score"] = comment.xpath('.//span[@class="score"]/text()').get()
#             item_evaluate["date"] = comment.xpath('.//div[@class="comment_time"]/text()').get().strip()
#
#             # 保存评论
#             self.logger.debug(f"Scraped comment from {item_evaluate['user_name']}: {item_evaluate['content'][:20]}...")
#             yield item_evaluate
#
#
#
# 此前都是


from copy import deepcopy
import scrapy
import json
import logging

# 初始化Django环境
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunan_web.settings')
django.setup()

# 导入Django模型
from warehouse.models import Scenery, Spiderlog, Evaluate
from spider_qunaer import items


class QunaerSpider(scrapy.Spider):
    name = "qunaer"
    start_urls = ["https://travel.qunar.com/p-cs300022-changsha-jingdian"]
    page_num = 1
    max_pages = 10  # 定义最大页数，便于维护

    custom_settings = {
        'LOG_LEVEL': 'DEBUG',  # 调试模式
        'DOWNLOAD_DELAY': 2,  # 下载延迟，避免被封
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机延迟
    }

    async def start(self):
        self.spider_log = Spiderlog.objects.create()
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # 仅在响应为HTML时解析内容
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):
            item_scenery = items.SpiderSceneryItem()

            # 尝试新的XPath选择器，这里需要根据实际网页结构调整
            scenery_list = response.xpath('//div[@class="景点列表的实际类名"]')  # 需要替换为实际类名
            self.logger.info(f"Page {self.page_num}: Found {len(scenery_list)} scenic spots")

            if not scenery_list:
                self.logger.warning("No scenic spots found, check XPath selector")
                self.logger.debug(f"Page content sample: {response.text[:500]}")

            for scenery in scenery_list:
                # 更新景点名称XPath
                scenery_name = scenery.xpath('.//h3/a/text()').get()
                if not scenery_name:
                    self.logger.debug("Scenery name not found, skipping item")
                    continue

                item_scenery["scenery_name"] = scenery_name.strip()

                # 更新排名信息XPath
                rank = scenery.xpath('.//span[@class="ranking"]/text()').get()
                item_scenery["rank"] = rank.strip() if rank else None

                # 更新热度信息XPath
                people_percent = scenery.xpath('.//div[contains(@class, "hot_num")]/span/text()').get()
                item_scenery["people_percent"] = people_percent.strip() if people_percent else None

                # 更新详情页URL
                detail_url = scenery.xpath('./a/@href').get()

                # 调试输出，确认提取的数据
                self.logger.debug(f"Extracted: {scenery_name}, Rank: {rank}, URL: {detail_url}")

                if detail_url:
                    # 暂时注释掉数据库检查，便于调试
                    # if not Scenery.objects.filter(scenery_name=scenery_name).exists():
                    yield scrapy.Request(
                        detail_url,
                        callback=self.get_detail,
                        meta={"item_scenery": deepcopy(item_scenery)}
                    )

        # 分页逻辑保持不变
        if self.page_num < self.max_pages:
            self.page_num += 1
            next_page = f"{self.start_urls[0]}-1-{self.page_num}"
            self.logger.info(f"Requesting page {self.page_num}: {next_page}")
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            self.logger.info("Reached max page limit")

    def get_detail(self, response):
        item_scenery = response.meta["item_scenery"]
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore')

        self.logger.debug(f"Parsing detail page: {response.url}")

        if 'application/json' in content_type:
            try:
                data = response.json()
                item_scenery["score"] = data.get('score', 0.0)
                self.logger.debug(f"JSON data parsed: {data.get('name')}, Score: {item_scenery['score']}")
            except json.JSONDecodeError:
                self.logger.error(f"JSON decode error in {response.url}")
                return
        else:
            # 更新评分XPath
            score = response.xpath(
                '//div[contains(@class, "mp-description")]//span[contains(@class, "score")]/text()').get()
            item_scenery["score"] = float(score) if score else 0.0

            # 更新游玩时间XPath
            play_time = response.xpath('//div[contains(@class, "time")]/text()').get()
            item_scenery["play_time"] = play_time.split("：")[-1].strip() if play_time else None

            # 更新城市信息XPath
            city = response.xpath('//td[@class="td_l"]/dl[1]/dd/span/text()').get() or response.xpath(
                '//div[contains(@class, "mp-baseinfo")]//dd[1]/span/text()').get()
            item_scenery["city"] = city.strip() if city else None

            # 更新景点地址XPath
            address = response.xpath('//td[@class="td_l"]/dl[2]/dd/span/text()').get() or response.xpath(
                '//div[contains(@class, "mp-baseinfo")]//dd[2]/span/text()').get()
            item_scenery["address"] = address.strip() if address else None

        if not item_scenery["scenery_name"]:
            self.logger.warning(f"Skipping invalid item from {response.url}")
            return

        self.logger.info(f"Scraped item: {item_scenery['scenery_name']}, Score: {item_scenery['score']}")
        yield item_scenery

        # 爬取评论
        self.crawl_comments(response, item_scenery)

    def crawl_comments(self, response, item_scenery):
        # 更新评论页XPath
        comment_pages = response.xpath('//div[@class="n_paging"]/a/@href').getall()
        self.logger.info(f"Found {len(comment_pages)} comment pages for {item_scenery['scenery_name']}")

        for i, comment_url in enumerate(comment_pages):
            if i < 4:  # 只爬取前4页评论，避免抓取过多
                self.logger.debug(f"Requesting comment page {i + 1}: {comment_url}")
                yield scrapy.Request(
                    comment_url,
                    callback=self.get_evaluate,
                    meta={"item_scenery": deepcopy(item_scenery)}
                )

    def get_evaluate(self, response):
        item_scenery = response.meta["item_scenery"]

        # 更新评论列表XPath
        comment_list = response.xpath('//div[contains(@class, "comment_item")]')
        self.logger.info(f"Found {len(comment_list)} comments on {response.url}")

        for comment in comment_list:
            item_evaluate = items.SpiderEvaluteItem()

            # 提取评论信息
            item_evaluate["scenery_name"] = item_scenery["scenery_name"]
            item_evaluate["user_name"] = comment.xpath('.//div[@class="user_name"]/text()').get()
            if item_evaluate["user_name"]:
                item_evaluate["user_name"] = item_evaluate["user_name"].strip()
            item_evaluate["content"] = comment.xpath('.//div[@class="comment_txt"]/text()').get()
            if item_evaluate["content"]:
                item_evaluate["content"] = item_evaluate["content"].strip()
            item_evaluate["score"] = comment.xpath('.//span[@class="score"]/text()').get()
            item_evaluate["send_time"] = comment.xpath('.//div[@class="comment_time"]/text()').get()
            if item_evaluate["send_time"]:
                item_evaluate["send_time"] = item_evaluate["send_time"].strip()

            # 保存评论
            self.logger.debug(f"Scraped comment from {item_evaluate['user_name']}: {item_evaluate['content'][:20]}...")
            yield item_evaluate