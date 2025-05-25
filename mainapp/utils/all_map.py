import datetime
import re
from django.utils import timezone
from pyecharts.charts import Pie, Line, WordCloud, Map
from pyecharts import options as opts
from django_pandas.io import read_frame
import jieba
from pyecharts.globals import SymbolType
from warehouse.models import Scenery, Evaluate, Spiderlog


class AllMap:
    def __init__(self):
        # 初始化爬虫时间
        try:
            latest_log = Spiderlog.objects.last()
            self.spider_time = timezone.localtime(latest_log.spider_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.spider_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 初始化地图数据
        qs = Scenery.objects.filter(city__isnull=False)
        df_p1 = read_frame(qs)
        df_p1['county'] = df_p1['city'].map(lambda x: self.get_county(x))
        self.map_data = df_p1.groupby('county').count()['scenery_name']
        self.map_data = self.map_data.sort_values()

        # 初始化景点评分数据
        self.scenery_obj = Scenery.objects.filter(score__isnull=False).exclude(score=0).order_by('-score')

        # 初始化景点人数分布数据
        qs = Scenery.objects.exclude(people_percent='0%').all()
        self.df_p4 = read_frame(qs=qs)
        self.df_p4['people_percent'] = self.df_p4['people_percent'].str.replace('%', '').astype('int')

    def get_county(self, full_county_name):
        conut_list = ['芙蓉区', '天心区', '岳麓区', '望城区', '雨花区', '开福区', '宁乡市', '浏阳市', '长沙县',
                      '宁乡县']
        for i in conut_list:
            if i in full_county_name:
                return i
        return full_county_name  # 如果没有匹配的区县，返回原始名称

    # 生成长沙景点分布地图
    def get_p1(self, h, w, is_show=False):
        max_val = int(self.map_data.values.max())
        return (
            Map(init_opts=opts.InitOpts(height=h, width=w))
            .add("景点数量", [[i[0], int(i[1])] for i in zip(self.map_data.index, self.map_data.values)],
                 maptype="长沙", is_roam=False, label_opts=opts.LabelOpts(is_show=True, color="#fff"))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="长沙景点分布", is_show=False),
                visualmap_opts=opts.VisualMapOpts(is_show=is_show, max_=max_val)
            )
            .render_embed()
        )

    def get_p2(self, h=None, w=None, is_show=False):
        # 返回景点评分数据
        return self.scenery_obj

    def get_p3(self, h=None, w=None, is_show=False):
        # 返回景点浏览人数数据
        return self.df_p4.sort_values('people_percent', ascending=False).to_dict('records')

    def get_p4(self, h, w, is_show=False):
        # 返回景点人数分布饼图
        total = self.df_p4['people_percent'].sum()
        self.df_p4['people_p4'] = self.df_p4['people_percent'].map(lambda x: round(x / total * 100, 2))
        return (
            Pie(init_opts=opts.InitOpts(height=h, width=w))
            .add("", self.df_p4[['scenery_name', 'people_p4']].values,
                 label_opts=opts.LabelOpts(formatter="{b}: {c}%", color="#fff"))
            .set_global_opts(legend_opts=opts.LegendOpts(is_show=is_show))
            .render_embed()
        )

    def get_p5(self, h, w, is_show=False):
        # 生成景点评论词云
        words = []
        evaluates = Evaluate.objects.all()[:100]
        for evaluate in evaluates:
            if evaluate.content:
                filtered_text = re.sub(r'\d+', '', evaluate.content)
                words += jieba.lcut(filtered_text)

        counts = {}
        stopwords = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '的', '是', '在', '等', '了', '和', '与', '也',
                     '有', '景区', '景点', '一个'}
        for word in words:
            if word not in stopwords and len(word) > 1:
                counts[word] = counts.get(word, 0) + 1

        items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:100]
        return (
            WordCloud(init_opts=opts.InitOpts(height=h, width=w))
            .add("评论词云", items, word_size_range=[20, 100])
            .set_global_opts(title_opts=opts.TitleOpts(title="用户评论词云", is_show=is_show))
            .render_embed()
        )

    def get_p6(self, h, w, is_show=False):
        # 生成景点浏览时间分布
        return (
            Line(init_opts=opts.InitOpts(height=h, width=w))
            .add_xaxis(["上午", "中午", "下午", "晚上"])
            .add_yaxis("浏览人数", [3000, 2000, 5000, 4000])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="景点浏览时间分布", is_show=is_show),
                toolbox_opts=opts.ToolboxOpts(is_show=True)
            )
            .render_embed()
        )

    def get_p7(self, h, w, is_show=False):
        # 生成景点数量统计
        return (
            Pie(init_opts=opts.InitOpts(height=h, width=w))
            .add(
                "景点类型",
                [("自然风光", 45), ("人文历史", 30), ("主题公园", 15), ("其他", 10)],
                radius=["30%", "75%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="景点类型分布", is_show=is_show),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
            )
            .render_embed()
        )

    def get_p8(self, h, w, is_show=False):
        # 生成景点评分分布
        return (
            Line(init_opts=opts.InitOpts(height=h, width=w))
            .add_xaxis(["岳麓山", "橘子洲", "世界之窗", "湖南省博物馆", "石燕湖"])
            .add_yaxis("评分", [4.8, 4.7, 4.5, 4.6, 4.4])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="主要景点评分", is_show=is_show),
                yaxis_opts=opts.AxisOpts(min_=4.0, max_=5.0),
            )
            .render_embed()
        )