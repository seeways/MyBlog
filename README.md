## 简介

动态博客系统

注释很详细，都在代码里，可以作为Django入门项目之一

如果你觉得还不错，帮我点个star吧

### 环境
- Python 3.6
- Django 1.11
- MySQL 5.7
- 安装环境 `pip install -r requirements.txt`



### 依赖
其他依赖在`requirements.txt`中了  

安装依赖库  
`pip install -r requirements.txt`

如果有需要，你也生成这样一个依赖  
`pip freeze >./requirements.txt`

### 数据库
除了依赖和settings之外，还没有建数据库和表

所以，运行migrate命令，创建数据库和数据表吧

### 关于settings

`settings.py` 是任何一个Django项目最重要和敏感的模块，几乎包含了所有的重要配置信息，务必了解其用法
