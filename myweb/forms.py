#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by TaoYuan on 2018/1/23 0023. 
# @Link    : http://blog.csdn.net/lftaoyuan  
# Github   : https://github.com/seeways
from django import forms
from captcha.fields import CaptchaField

"""
Django生成表单

1. 要先导入forms模块
2. 所有的表单类都要继承forms.Form类
3. 表单字段对应 HTML中<form>内的一个input元素
4. label参数用于设置<label>标签
5. max_length可以同时限制前后端长度
6. widget=forms.PasswordInput用于指定该字段在form表单里的type
7. attrs 设置css
"""


# 登录表单
# class UserForm(forms.Form):
#     username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}))
#     password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={"class": "form-control"}))
#     # captcha = CaptchaField(label="图形认证")
#
#
# # 注册表单
# class RegisterForm(forms.Form):
#     gender = (
#         ('male', "男"),
#         ('female', "女"),
#     )
#     username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     nickname = forms.CharField(label="昵称", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     password2 = forms.CharField(label="确认密码", max_length=256,
#                                 widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
#     sex = forms.ChoiceField(label='性别', choices=gender)
#     captcha = CaptchaField(label='验证码')


# 登录表单
class LoginForm(forms.Form):
    uid = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'uid', 'placeholder': 'Username'}))
    pwd = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'id': 'pwd', 'placeholder': 'Password'}))


# 注册表单
class RegisterForm(forms.Form):
    username = forms.CharField(
        label='username',
        max_length=100,
        widget=forms.TextInput(
            attrs={'id': 'username', 'onblur': 'authentication()'}))
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


# 设置用户名
class SetInfoForm(forms.Form):
    username = forms.CharField()


# 评论
class CommentForm(forms.Form):
    comment = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': '60', 'rows': '6'}))


# 搜索
class SearchForm(forms.Form):
    keyword = forms.CharField(widget=forms.TextInput)
