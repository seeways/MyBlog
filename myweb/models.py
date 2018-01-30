import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


class NewUser(AbstractUser):  # 避免和继承的User重名
    profile = models.CharField('profile', default='', max_length=256)

    def __str__(self):
        return self.username


# 和User表形成一对一的关系，对User和注册码进行验证,然后去admin注册
# 完成之后，要进行迁移操作 1. python manage.py makemigrations 2. python manage.py migrate
# class ConfirmString(models.Model):
#     code = models.CharField(max_length=256)  # hash后的注册码
#     user = models.OneToOneField("NewUser")  # 一对一关联
#     create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
#
#     def __str__(self):
#         return self.user.username + ":  " + self.code
#
#     class Meta:
#         ordering = ["-create_time"]
#         verbose_name = "确认码"
#         verbose_name_plural = "确认码"


"""
cms系统
"""


# 文章查询
class ArticleManager(models.Manager):
    # 分类查询
    def query_by_column(self, column_id):
        query = self.get_queryset().filter(column_id=column_id)

    # 按用户
    def query_by_user(self, user_id):
        user = User.objects.get(id=user_id)
        article_list = user.article_set.all()
        return article_list

    # 按点赞
    def query_by_polls(self):
        query = self.get_queryset().order_by('poll_num')
        return query

    # 按时间
    def query_by_time(self):
        query = self.get_queryset().order_by('-pub_date')
        return query

    # 按关键词
    # 按关键词
    def query_by_keyword(self, keyword):
        query = self


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
    user = models.ManyToManyField("NewUser", blank=True)  # 多对多 用户

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

    objects = ArticleManager()  # 申明文章管理类


# 评论
class Comment(models.Model):
    user = models.ForeignKey("NewUser", null=True)
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
    user = models.ForeignKey('NewUser', null=True)
    article = models.ForeignKey(Article, null=True)
    comment = models.ForeignKey(Comment, null=True)
