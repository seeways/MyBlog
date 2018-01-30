from django.contrib import admin
from django.db import models
from django import forms

from .models import Comment, Article, Column, NewUser, Author

# Register your models here.

"""
‘model.ModelAdmin’是django内置的处理自定义界面的模块
‘list_display’ 是数据模型的字段，可以自定义后台要现实哪些字段
‘formfield_overrides’ 可以更改字段默认的后台显示细节
"""


class NewUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_joined', 'profile')


class CommentAdmin(admin.ModelAdmin):
    list_display = ("user_id", "article_id", "pub_date", "content", "poll_num")


class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 41,
                   'cols': 100
                   })},
    }
    list_display = ("title", "pub_date", "poll_num")


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'intro')


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile')


admin.site.register(NewUser, NewUserAdmin)
# admin.site.register(ConfirmString)

admin.site.register(Comment, CommentAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Author, AuthorAdmin)
