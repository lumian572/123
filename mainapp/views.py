# mainapp/views.py
import datetime
from django.shortcuts import render, redirect
from mainapp import models
from mainapp.utils.all_map import AllMap
from mainapp.utils import md5_util

# 定义尺寸常量（避免循环导入）
index_h = '278px'
index_w = '434px'
page_h = '753px'
page_w = '1328px'

# 初始化数据
all_map = AllMap()
data = {}
data['spider_time'] = all_map.spider_time
data['p1'] = all_map.get_p1(index_h, index_w)  # 调用方法而非属性
data['p2'] = all_map.get_p2()  # 无参数方法
data['p3'] = all_map.get_p3()  # 无参数方法
data['p4'] = all_map.get_p4(index_h, index_w)  # 带参数方法
data['p5'] = all_map.get_p5(index_h, index_w)
data['p6'] = all_map.get_p6(index_h, index_w)
data['p7'] = all_map.get_p7(index_h, '898px')
data['p8'] = all_map.get_p8(index_h, index_w)

# 创建页面详情数据
is_show = True
p1 = all_map.get_p1(page_h, page_w, is_show)
p2 = all_map.get_p2()  # 无参数
p3 = all_map.get_p3()  # 无参数
p4 = all_map.get_p4(page_h, page_w, is_show)
p5 = all_map.get_p5(page_h, page_w, is_show)
p6 = all_map.get_p6(page_h, page_w, is_show)
p7 = all_map.get_p7(page_h, page_w, is_show)
p8 = all_map.get_p8(page_h, page_w, is_show)

map_list = {
    '某某景点分布': p1,
    '景点评分数据': data['p2'],
    '景点浏览人数': data['p3'],
    '景点人数分布': p4,
    '景点评论词云': p5,
    '景点浏览时间': p6,
    '景点数量': p7,
    '景点评分': p8,
}


def index(request):
    return render(request, 'index.html', data)


def page(request):
    result = {
        'is_chart': True,
        'spider_time': all_map.spider_time,
    }
    page = request.GET.get('p')
    if not page:
        page = 0
    else:
        page = int(page) - 1
    try:
        result['title'] = list(map_list.keys())[page]
        result['data'] = map_list[result['title']]  # 修正：使用字典索引而非get[]
        result['page_data'] = map_list
        if page in [1, 2]:  # 假设这两页是纯数据而非图表
            result['is_chart'] = False
    except (IndexError, ValueError):
        result['error'] = '页面不存在'
    return render(request, 'page/index.html', result)


# 登录视图
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
        # 修正：使用 request.POST 而非 request.POST()
        post_data = request.POST
        username = post_data.get('username')
        password = md5_util.md5(post_data.get('password'))

        user = models.Userinfo.objects.filter(username=username, password=password).first()
        if user:
            request.session['user_info'] = username  # 使用 setdefault 可能导致意外行为
            return redirect('/index')
        else:
            temp_txt['error'] = '用户名或者密码错误'
            return render(request, 'login.html', temp_txt)


# 注册视图
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

        if 3 > len(username) or len(username) > 16:
            temp_txt['error'] = '用户名长度应为3-16个字符！'
        elif repassword != password:
            temp_txt['error'] = '密码不一致'
        elif models.Userinfo.objects.filter(username=username).first():
            temp_txt['error'] = '用户名已存在'
        elif 16 < len(password) or len(password) < 6:
            temp_txt['error'] = '密码长度应为6-16个字符'

        if temp_txt['error']:
            return render(request, 'register.html', temp_txt)

        password = md5_util.md5(password)
        models.Userinfo.objects.create(username=username, password=password)
        return redirect('/login')