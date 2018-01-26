import datetime
from django.db import models
from django.utils import timezone


class User(models.Model):  # 避免和继承的User重名
    gender = (
        ("male", "男"),
        ("female", "女"),
    )

    username = models.CharField(max_length=128, unique=True)  # 用户名
    password = models.CharField(max_length=128)  # 密码
    email = models.EmailField(unique=True)  # Email
    sex = models.CharField(max_length=32, choices=gender, default="男")  # 性别
    nickname = models.CharField(max_length=128)  # 昵称
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    has_confirmed = models.BooleanField(default=False)  # 是否验证

    profile = models.CharField('profile', default='', max_length=256)

    @property
    def __str__(self):
        if self.nickname is not None:
            return self.nickname
        else:
            return self.username

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


# 和User表形成一对一的关系，对User和注册码进行验证,然后去admin注册
# 完成之后，要进行迁移操作 1. python manage.py makemigrations 2. python manage.py migrate
class ConfirmString(models.Model):
    code = models.CharField(max_length=256)  # hash后的注册码
    user = models.OneToOneField("User")  # 一对一关联
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return self.user.username + ":  " + self.code

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


"""
cms系统
"""


# 文章分类
class Column(models.Model):
    name = models.CharField('column_name', max_length=256)  # 栏目名
    intro = models.TextField('introduction', default='')  # 栏目简介

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "column"
        verbose_name_plural = "column"


# 文章
class Article(models.Model):
    column = models.ForeignKey(Column, blank=True, null=True, verbose_name="belong to ")  # 外键 分类
    author = models.ForeignKey('Author')  # 外键 作者
    user = models.ManyToManyField("User", blank=True)  # 多对多 用户

    title = models.CharField(max_length=256)  # 标题
    content = models.TextField('content')  # 内容
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)  # 发布日期，自动添加，可编辑
    update_time = models.DateTimeField(auto_now=True, null=True)  # 更新日期，可空
    published = models.BooleanField('notDraft', default=True)  # 是否发布
    poll_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    keep_num = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = 'article'


# 评论
class Comment(models.Model):
    user = models.ForeignKey("User", null=True)
    article = models.ForeignKey(Article, null=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)
    poll_num = models.IntegerField(default=0)

    def __str__(self):
        return self.content


# 作者
class Author(models.Model):
    name = models.CharField(max_length=256)
    profile = models.CharField('profile', default='', max_length=256)
    password = models.CharField('password', max_length=256)
    register_date = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name


# 点赞
class Poll(models.Model):
    user = models.ForeignKey('User', null=True)
    article = models.ForeignKey(Article, null=True)
    comment = models.ForeignKey(Comment, null=True)
