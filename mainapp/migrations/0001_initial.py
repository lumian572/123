# 导入相关模块
from django.contrib.auth.password_validation import password_changed
from django.db import migrations,models
# 定义迁移类
class Migration(migrations.Migration):
    # 是否初始迁移
    initial = True
    # 依赖关系
    dependencies = []
    operations = [
        # 创建模型
        migrations.CreateModel(
            # 模型名称
            name='Evaluate',
            fields=[
                # 自增主键
                ('eid', models.AutoField(primary_key=True,serialize=False)),
                # 文本内容
                ('content', models.TextField(blank=True,null=True)),
                # 评价发送日期
                ('send_time', models.DateTimeField(blank=True,null=True)),
                # 用户名
                ('username', models.TextField(blank=True,max_length=32,null=True)),
                # 评分
                ('score',models.FloatField(blank=True,null=True)),
                # 景点名称
                ('scenery_name', models.TextField(blank=True,max_length=32,null=True)),
            ],
        ),
        # 创建用户会话模型
        migrations.CreateModel(
            # 模型名称
            name='Userinfo',
            # 模型字段
            fields=[
                ('id', models.AutoField(primary_key=True,serialize=False)),
                ('username', models.TextField(max_length=32)),
                ('password', models.TextField(max_length=64)),
            ],
        ),
        # 定义景点模型
        migrations.CreateModel(
            name='Scenery',
            fields=[
                ('sid', models.AutoField(primary_key=True,serialize=False)),
                ('city', models.TextField(blank=True,max_length=64,null=True)),
                ('people_percent', models.FloatField(blank=True,max_length=32,null=True)),
                ('rank', models.FloatField(blank=True,null=True)),
                ('scenery_name', models.TextField(blank=True,max_length=64,null=True)),
                ('score', models.FloatField(blank=True,null=True)),
                ('evaluates', models.ManyToManyField(to='mainapp.Evaluate')),
            ],
        ),
    ]
