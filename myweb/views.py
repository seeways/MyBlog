import hashlib

import datetime
from django.shortcuts import render, redirect
from . import models, forms
from django.conf import settings


# Create your views here.


def hash_code(s, salt='TaoYuan'):  # hash加密
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # 值需为bytes
    return h.hexdigest()


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "TaoYuan博客 注册确认"
    text_content = """
    感谢注册， 当你看到这条消息的时候，说明你没法收到注册码，换个邮箱吧。
    如果你和我一样懒，也没关系，没有验证码也可以用！
    但是超过注册时间还是得重新注册！
    """
    html_content = """
    感谢注册：
        
        <h2><a href='http://{}/confirm/?code={}'>点击验证</a></h2>
        
        <p>上述有效期为{}天</p>
    
    <p>Github:<a href='https://github.com/seeways/MyBlog'>本博客源码</a></p><br>
    <p>我的GitHub:<a href='https://github.com/seeways'>seeways</a></p><br>
    <p>我的CSDN:<a href='http://blog.csdn.net/lftaoyuan'>TaoYuan</a></p> 
    """.format("127.0.0.1:8000", code, settings.CONFIRM_DAYS)
    # 优先发送html_content, html内容无效时，发送text
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [email, ])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 创建确认码
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    models.ConfirmString.objects.create(code=code, user=user, )
    return code


def index(request):
    return render(request, 'myweb/index.html')


def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        # 接收post表单数据并验证
        login_form = forms.UserForm(request.POST)
        message = message = "请填写完整信息！"
        # django自带的is_valid进行数据验证
        if login_form.is_valid():
            # cleaned_data字典验证表单的值
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            # 以下try块为值验证过程
            try:
                user = models.User.objects.get(username=username)
                # 邮件确认
                if not user.has_confirmed:
                    message = "请通过邮件确认！"
                    return render(request, "myweb/login.html", locals())
                # 密码hash比对
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    request.session['user_nick'] = user.nickname
                    return redirect("/index/")
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        # locals()函数返回本地变量字典
        return render(request, "myweb/login.html", locals())
    # 非POST请求直接返回空表单
    login_form = forms.UserForm()
    return render(request, "myweb/login.html", locals())


def register(request):
    if request.session.get("is_login", None):
        # 登录状态禁止注册
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = message = "请填写完整信息！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            nickname = register_form.cleaned_data["nickname"]
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'myweb/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在！'
                    return render(request, 'myweb/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册！'
                    return render(request, 'myweb/register.html', locals())

                # 创建新用户
                new_user = models.User.objects.create()
                new_user.username = username
                new_user.nickname = nickname
                new_user.password = hash_code(password2)  # 存储hash密码
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                # 确认邮件
                code = make_confirm_string(new_user)
                send_email(email, code)

                message = "请前往注册邮箱进行确认！"
                return render(request, "myweb/confirm.html", locals())
    register_form = forms.RegisterForm()
    return render(request, 'myweb/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者清空部分信息
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")


def user_confirm(request):
    code = request.GET.get("code", None)  # 获取验证码
    message = ""  # 提示信息
    try:
        # 数据库查找对应的验证码，如果没有，则返回确认页面，并提示
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = "无效请求！"
        return render(request, "myweb/confirm.html", locals())

    create_time = confirm.create_time
    now = datetime.datetime.now()
    # 如果超过链接给定时间，则提示超时
    if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = "您的邮件已经过期！请重新注册"
        return render(request, "myweb/confirm.html", locals())
    else:
        # 如果没超时，修改字段并保存
        confirm.user.has_confirmed = True
        confirm.user.save()
        # 然后就可以删掉验证码了
        confirm.delete()
        # 最后调到确认页面并提示成功
        message = "确认成功，请使用账户登录！"
        return render(request, "myweb/confirm.html", locals())
