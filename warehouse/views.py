# from django.shortcuts import render
#
# # Create your views here.
# # mainapp/views.py
# from mainapp.utils.all_map import AllMap
#
# def dashboard(request):
#     all_map = AllMap()
#     context = {
#         'map_chart': all_map.p1,  # 通过属性访问地图（无需括号）
#         'scenery_list': all_map.p2,  # 景点列表
#         'crowded_sceneries': all_map.p3,  # 人流量数据
#         'pie_chart': all_map.p4,  # 饼图
#         'wordcloud': all_map.p5,  # 词云
#     }
#     return render(request, 'dashboard.html', context)


# 导入相关模块
from mainapp.utils.md5_util import md5
import datetime
import re
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.db.models import Count
from django.utils import timezone
from pyecharts.charts import Pie, Line, WordCloud, Map
from pyecharts import options as opts
from pyecharts.globals import ThemeType, SymbolType
from mainapp import models
from django_pandas.io import read_frame
import jieba

from mainapp.utils import md5_util
from warehouse.models import Scenery, Evaluate, Spiderlog

# 首页高度和宽度
index_h = '278px'
index_w = '434px'

# 页面详情高度和宽度
page_h = '753px'
page_w = '1328px'


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

    # 用于生成长沙景点分布地图
    def get_p1(self, h, w, is_show=False):
        max_ = int(self.map_data.values.max())
        map_chart = (
            Map(
                init_opts=opts.InitOpts(height=h, width=w)
            )
            .add(
                '商家数量',
                [[i[0], int(i[1])] for i in zip(self.map_data.index, self.map_data.values)],
                maptype='长沙',
                is_roam=False,
                label_opts=opts.LabelOpts(is_show=True, color='#fff'),
                is_map_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title='title', is_show=False),
                legend_opts=opts.LegendOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
                visualmap_opts=opts.VisualMapOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
            )
        )
        return map_chart.render_embed()

    def get_p2(self, h=None, w=None, is_show=False):
        # 返回景点评分数据
        return self.scenery_obj

    def get_p3(self, h=None, w=None, is_show=False):
        # 返回景点浏览人数数据
        return self.df_p4.sort_values('people_percent', ascending=False).to_dict('records')

    def get_p4(self, h, w, is_show=False):
        # 返回景点人数分布饼图
        sum_people = self.df_p4['people_percent'].sum()
        self.df_p4['people_p4'] = self.df_p4['people_percent'].map(lambda x: round(float(x) / sum_people * 100, 2))

        pie = (
            Pie(
                init_opts=opts.InitOpts(height=h, width=w)
            )
            .add(
                '',
                self.df_p4[['scenery_name', 'people_p4']].values,
                label_opts=opts.LabelOpts(is_show=False, color='#fff')
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(formatter='{b}:{c}', color='#fff'),
            )
        )
        return pie.render_embed()

    def get_p5(self, h, w, is_show=False):
        # 生成景点评论词云
        words_list = []
        evaluates = Evaluate.objects.all()[:100]

        for evaluate in evaluates:
            txt = evaluate.content
            pattern = re.compile(r'\d+')
            filtered_text = re.sub(pattern, '', txt)
            words_list += jieba.lcut(filtered_text)

        counts = {}
        stopwords = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '的', '是', '在', '等')

        for word in words_list:
            if word not in stopwords and len(word) > 1:
                counts[word] = counts.get(word, 0) + 1

        # 排序
        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)

        # 设置词云图
        wordcloud = (
            WordCloud(init_opts=opts.InitOpts(height=h, width=w))
            .add(
                series_name='出现数量',
                data_pair=items,
                word_size_range=[20, 100],
                shape=SymbolType.DIAMOND
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title='评论词云', title_textstyle_opts=opts.TextStyleOpts(font_size=23),
                                          is_show=False),
                legend_opts=opts.LegendOpts(is_show=False, textstyle_opts=opts.TextStyleOpts(color='#fff')),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                visualmap_opts=opts.VisualMapOpts(is_show=False, max_=50, min_=0, range_color=['#ffffff', '#ffffff']),
            )
        )
        return wordcloud.render_embed()

    def get_p6(self, h, w, is_show=False):
        # 示例：生成景点浏览时间图表
        # 这里需要根据实际数据结构实现
        line = (
            Line(init_opts=opts.InitOpts(height=h, width=w))
            .add_xaxis(["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"])
            .add_yaxis(
                "浏览人数",
                [120, 132, 101, 134, 90, 230, 210],
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="景点浏览时间分布", is_show=False),
                legend_opts=opts.LegendOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
                xaxis_opts=opts.AxisOpts(name="时间", axislabel_opts=opts.LabelOpts(color="#fff")),
                yaxis_opts=opts.AxisOpts(name="人数", axislabel_opts=opts.LabelOpts(color="#fff")),
            )
        )
        return line.render_embed()

    def get_p7(self, h, w, is_show=False):
        # 示例：生成景点数量图表
        # 这里需要根据实际数据结构实现
        line = (
            Line(init_opts=opts.InitOpts(height=h, width=w))
            .add_xaxis(["一月", "二月", "三月", "四月", "五月", "六月"])
            .add_yaxis(
                "景点数量",
                [30, 35, 40, 45, 50, 55],
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="景点数量统计", is_show=False),
                legend_opts=opts.LegendOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
                xaxis_opts=opts.AxisOpts(name="月份", axislabel_opts=opts.LabelOpts(color="#fff")),
                yaxis_opts=opts.AxisOpts(name="数量", axislabel_opts=opts.LabelOpts(color="#fff")),
            )
        )
        return line.render_embed()

    def get_p8(self, h, w, is_show=False):
        # 示例：生成景点评分图表
        # 这里需要根据实际数据结构实现
        line = (
            Line(init_opts=opts.InitOpts(height=h, width=w))
            .add_xaxis(["景点A", "景点B", "景点C", "景点D", "景点E"])
            .add_yaxis(
                "评分",
                [4.5, 4.2, 4.8, 3.9, 4.6],
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="景点评分", is_show=False),
                legend_opts=opts.LegendOpts(is_show=is_show, textstyle_opts=opts.TextStyleOpts(color='#fff')),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#fff")),
                yaxis_opts=opts.AxisOpts(name="评分", min_=3, max_=5, axislabel_opts=opts.LabelOpts(color="#fff")),
            )
        )
        return line.render_embed()


# 登录
@api_view(['GET', 'POST'])
def login(request):
    temp_txt = {
        'tip': '请登录',
        'username': '用户名',
        'password': '密码',
        'remember': '记住密码',
        'login': '登录',
        'go': '去注册',
        'year': datetime.date.today().year,
        'next_year': datetime.date.today().year + 1,
        'error': '',
    }

    if request.method == 'GET':
        return render(request, 'login.html', temp_txt)

    if request.method == 'POST':
        post_data = request.POST
        username = post_data.get('username')
        password = md5(post_data.get('password'))  # 直接使用md5函数

        user = models.Userinfo.objects.filter(username=username, password=password).first()

        if user:
            request.session['user_info'] = username
            return redirect('/index')
        else:
            temp_txt['error'] = '用户名或者密码错误'
            return render(request, 'login.html', temp_txt)

# 处理用户注册请求
def register(request):
    temp_txt = {
        'tip': '注册用户',
        'username': '用户名',
        'password': '密码',
        'remember': '记住密码',
        'login': '注册',
        'go': '去登录',
        'year': datetime.date.today().year,
        'next_year': datetime.date.today().year + 1,
        'error': '',
    }

    if request.method == 'GET':
        return render(request, 'register.html', temp_txt)

    elif request.method == 'POST':
        post_data = request.POST
        username = post_data.get('username')
        password = post_data.get('password')
        repassword = post_data.get('repassword')

        if not (3 <= len(username) <= 16):
            temp_txt['error'] = '用户名长度应为3-16个字符！'
        elif repassword != password:
            temp_txt['error'] = '密码不一致'
        elif models.Userinfo.objects.filter(username=username).first():
            temp_txt['error'] = '用户名已存在'
        elif not (6 <= len(password) <= 16):
            temp_txt['error'] = '密码长度应为6-16个字符'

        if temp_txt['error']:
            return render(request, 'register.html', temp_txt)

        # 密码加密
        encrypted_password = md5(password)  # 直接使用md5函数
        # 创建用户
        models.Userinfo.objects.create(username=username, password=encrypted_password)
        return redirect('/login')

@api_view(['GET', 'POST'])
def index(request):
    # 在视图函数中实例化AllMap并获取数据
    all_map = AllMap()
    data = {}
    data['spider_time'] = all_map.spider_time
    data['p1'] = all_map.get_p1(index_h, index_w, is_show=True)  # 修改为方法调用
    data['p2'] = all_map.get_p2()  # 修改为方法调用
    data['p3'] = all_map.get_p3()  # 修改为方法调用
    data['p4'] = all_map.get_p4(index_h, index_w, is_show=True)  # 修改为方法调用
    data['p5'] = all_map.get_p5(index_h, index_w, is_show=True)  # 修改为方法调用
    data['p6'] = all_map.get_p6(index_h, index_w, is_show=True)  # 修改为方法调用
    data['p7'] = all_map.get_p7(index_h, '898px', is_show=True)  # 修改为方法调用
    data['p8'] = all_map.get_p8(index_h, index_w, is_show=True)  # 修改为方法调用

    return render(request, 'index.html', data)