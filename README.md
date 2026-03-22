# 创建django项目
```
C:\Users\3229629598\miniconda3\envs\wx_backend\Scripts\django-admin startproject wx_backend
```
# 第一次启动
settings.py的INSTALLED_APPS中添加‘rest_framework’，命令行输入
```
python manage.py runserver
```
# 创建应用
```
python manage.py startapp goods
```
# 数据迁移
对数据库进行增删表、修改字段等，保持与数据库模型同步
```
python manage.py makemigrations
python manage.py migrate
```
# 创建超级管理员
```
python manage.py createsuperuser
```
# 导出第三方模块到requirements.txt
```
pip install pipreqs
pipreqs --force .
```
