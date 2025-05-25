# 导入相关模块
from django.shortcuts import render,redirect
from django.utils.deprecation import MiddlewareMixin
# 创建一个class中间类
class UserAuth(MiddlewareMixin):
    # 定义中间件的方法函数，用于在请求时到达视图之前进行处理
    def process_request(self,request):
        # 检查请求路径方法
        if request.path_info in['/login/','/register/','/login.html/','','img/code/','/index/login.html']:
            return
        # 检查用户会话信息
        user_info = request.session.get('user_info')
        if user_info:
            return
        return redirect('/login/')