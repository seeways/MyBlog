import hashlib

import datetime
from django.shortcuts import render, redirect
from . import models, forms
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate, login, logout  # 个django验证系统内置方法
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
import markdown2
import urllib
from urllib import parse


# Create your views here.


# 主页
def index(request):
    latest_article_list = models.Article.objects.query_by_time()  # 默认按发布时间排序
    loginform = forms.LoginForm()
    context = {'latest_article_list': latest_article_list, 'loginform': loginform}
    return render(request, 'index.html', context)


# 文章
def article(request, article_id):
    """
    since visitor input a url with invalid id:
    try:
        article = Article.objects.get(pk=article_id)  # pk???
    except Article.DoesNotExist:
        raise Http404("Article does not exist")
        """
    # 如果找不到该文章id，则报404错误，404也可以自己写
    article = get_object_or_404(models.Article, id=article_id)
    # 内容，支持markdown,考虑到只有自己写，就放弃富文本了
    # 富文本参考：https://code.ziqiangxuetang.com/django/django-cms-develop2.html
    content = markdown2.markdown(article.content, extras=["code-friendly",
                                                          "fenced-code-blocks", "header-ids", "toc", "metadata"])
    commentform = forms.CommentForm()
    loginform = forms.LoginForm()
    comments = article.comment_set.all

    return render(request, 'article_page.html', {
        'article': article,
        'loginform': loginform,
        'commentform': commentform,
        'content': content,
        'comments': comments
    })


# 评论
@login_required
def comment(request, article_id):
    form = forms.CommentForm(request.POST)  # 表单
    url = parse.urljoin('/blog/', article_id)  # 文章url
    # form自带的验证
    if form.is_valid():
        # 获取请求用户，文章，评论并保存
        user = request.user
        article = models.Article.objects.get(id=article_id)
        new_comment = form.cleaned_data['comment']
        c = models.Comment(content=new_comment, article_id=article_id)  # have tested by shell
        c.user = user
        c.save()
        article.comment_num += 1  # 文章评论数+1
    return redirect(url)

"""
以下3个函数因为需要记录用户，所以都需要登录才能操作。

article_id 这个参数是通过 article_page.html 文件传入到路由(urls.py),然后转接到相关函数的。
parse.urljoin 函数是python用来拼接url的，以前是urlparse.urljoin()
redirect()函数是django内置的一个快捷函数，用来重定向。

因为文章与用户是多对多关系，所以logged_user.article_set.all()会得到这个登录用户对应
的所有文章(即它收藏的文章)
"""


# 收藏
@login_required
def get_keep(request, article_id):
    logged_user = request.user
    article = models.Article.objects.get(id=article_id)
    articles = logged_user.article_set.all()
    if article not in articles:
        article.user.add(logged_user)  # for m2m linking, have tested by shell
        article.keep_num += 1
        article.save()
        return redirect('/blog/')
    else:
        url = parse.urljoin('/blog/', article_id)
        return redirect(url)


# 获取文章点赞
@login_required
def get_poll_article(request, article_id):
    logged_user = request.user
    article = models.Article.objects.get(id=article_id)
    polls = logged_user.poll_set.all()
    articles = []
    for poll in polls:
        articles.append(poll.article)

    if article in articles:
        url = parse.urljoin('/blog/', article_id)
        return redirect(url)
    else:
        article.poll_num += 1
        article.save()
        poll = models.Poll(user=logged_user, article=article)
        poll.save()
        data = {}
        return redirect('/blog/')


"""
由于内置方法已经包含login和logout函数，所以加下划线区分

@login_required这个装饰器是django内置的
它的作用是使所装饰的函数必须是登录的用户才继续运行，否则进入指定的login_url
由于本地没有指定login_url，所以在settings.py中添加以下代码：
LOGIN_URL = "/myweb/login/?next='article_id'"
"""


# 登录
def log_in(request):
    if request.method == 'GET':
        form = forms.LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['uid']
            password = form.cleaned_data['pwd']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                url = request.POST.get('source_url', '/blog')
                return redirect(url)
            else:
                return render(request, 'login.html', {'form': form, 'error': "password or username is not ture!"})

        else:
            return render(request, 'login.html', {'form': form})


# 退出
@login_required
def log_out(request):
    url = request.POST.get('source_url', '/blog/')
    logout(request)
    return redirect(url)


# 注册
def register(request):
    message = "this name is already exist"

    if request.method == 'GET':
        form = forms.RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        # 验证用户名是否存在
        if request.POST.get('raw_username', 'erjgiqfv240hqp5668ej23foi') != 'erjgiqfv240hqp5668ej23foi':  # if ajax
            try:
                models.NewUser.objects.get(username=request.POST.get('raw_username', ''))
            except ObjectDoesNotExist:
                message = "this name is valid"
            return render(request, 'register.html', {'form': form, 'msg': message})

        else:
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    return render(request, 'register.html', {'form': form, 'msg': "two password is not equal"})
                else:
                    user = models.NewUser(username=username, email=email, password=password1)
                    user.save()
                    # return render(request, 'login.html', {'success': "you have successfully registered!"})
                    return redirect('/blog/login')
            else:
                return render(request, 'register.html', {'form': form})

# def hash_code(s, salt='TaoYuan'):  # hash加密
#     h = hashlib.sha256()
#     s += salt
#     h.update(s.encode())  # 值需为bytes
#     return h.hexdigest()
#
#
# def send_email(email, code):
#     from django.core.mail import EmailMultiAlternatives
#     subject = "TaoYuan博客 注册确认"
#     text_content = """
#     感谢注册， 当你看到这条消息的时候，说明你没法收到注册码，换个邮箱吧。
#     如果你和我一样懒，也没关系，没有验证码也可以用！
#     但是超过注册时间还是得重新注册！
#     """
#     html_content = """
#     感谢注册：
#
#         <h2><a href='http://{}/confirm/?code={}'>点击验证</a></h2>
#
#         <p>上述有效期为{}天</p>
#
#     <p>Github:<a href='https://github.com/seeways/MyBlog'>本博客源码</a></p><br>
#     <p>我的GitHub:<a href='https://github.com/seeways'>seeways</a></p><br>
#     <p>我的CSDN:<a href='http://blog.csdn.net/lftaoyuan'>TaoYuan</a></p>
#     """.format("127.0.0.1:8000", code, settings.CONFIRM_DAYS)
#     # 优先发送html_content, html内容无效时，发送text
#     msg = EmailMultiAlternatives(
#         subject,
#         text_content,
#         settings.EMAIL_HOST_USER,
#         [email, ])
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
#
#
# # 创建确认码
# def make_confirm_string(user):
#     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     code = hash_code(user.username, now)
#     models.ConfirmString.objects.create(code=code, user=user, )
#     return code
#
# def index(request):
#     return render(request, 'myweb/index.html')
#
# def login(request):
#     if request.session.get('is_login', None):
#         return redirect("/index/")
#     if request.method == "POST":
#         # 接收post表单数据并验证
#         login_form = forms.UserForm(request.POST)
#         message = message = "请填写完整信息！"
#         # django自带的is_valid进行数据验证
#         if login_form.is_valid():
#             # cleaned_data字典验证表单的值
#             username = login_form.cleaned_data["username"]
#             password = login_form.cleaned_data["password"]
#             # 以下try块为值验证过程
#             try:
#                 user = models.NewUser.objects.get(username=username)
#                 # 邮件确认
#                 if not user.has_confirmed:
#                     message = "请通过邮件确认！"
#                     return render(request, "myweb/login.html", locals())
#                 # 密码hash比对
#                 if user.password == hash_code(password):
#                     request.session['is_login'] = True
#                     request.session['user_id'] = user.id
#                     request.session['user_name'] = user.username
#                     request.session['user_nick'] = user.nickname
#                     return redirect("/index/")
#                 else:
#                     message = "密码不正确！"
#             except:
#                 message = "用户名不存在！"
#         # locals()函数返回本地变量字典
#         return render(request, "myweb/login.html", locals())
#     # 非POST请求直接返回空表单
#     login_form = forms.UserForm()
#     return render(request, "myweb/login.html", locals())
#
#
# def register(request):
#     if request.session.get("is_login", None):
#         # 登录状态禁止注册
#         return redirect("/index/")
#     if request.method == "POST":
#         register_form = forms.RegisterForm(request.POST)
#         message = message = "请填写完整信息！"
#         if register_form.is_valid():  # 获取数据
#             username = register_form.cleaned_data['username']
#             nickname = register_form.cleaned_data["nickname"]
#             password1 = register_form.cleaned_data['password1']
#             password2 = register_form.cleaned_data['password2']
#             email = register_form.cleaned_data['email']
#             sex = register_form.cleaned_data['sex']
#             if password1 != password2:  # 判断两次密码是否相同
#                 message = "两次输入的密码不同！"
#                 return render(request, 'myweb/register.html', locals())
#             else:
#                 same_name_user = models.NewUser.objects.filter(username=username)
#                 if same_name_user:  # 用户名唯一
#                     message = '用户已经存在！'
#                     return render(request, 'myweb/register.html', locals())
#                 same_email_user = models.NewUser.objects.filter(email=email)
#                 if same_email_user:  # 邮箱地址唯一
#                     message = '该邮箱地址已被注册！'
#                     return render(request, 'myweb/register.html', locals())
#
#                 # 创建新用户
#                 new_user = models.NewUser.objects.create()
#                 new_user.username = username
#                 new_user.nickname = nickname
#                 new_user.password = hash_code(password2)  # 存储hash密码
#                 new_user.email = email
#                 new_user.sex = sex
#                 new_user.save()
#                 # 确认邮件
#                 code = make_confirm_string(new_user)
#                 send_email(email, code)
#
#                 message = "请前往注册邮箱进行确认！"
#                 return render(request, "myweb/confirm.html", locals())
#     register_form = forms.RegisterForm()
#     return render(request, 'myweb/register.html', locals())
#
#
# def logout(request):
#     if not request.session.get('is_login', None):
#         # 如果本来就未登录，也就没有登出一说
#         return redirect("/index/")
#     request.session.flush()
#     # 或者清空部分信息
#     # del request.session['is_login']
#     # del request.session['user_id']
#     # del request.session['user_name']
#     return redirect("/index/")
#
#
# def user_confirm(request):
#     code = request.GET.get("code", None)  # 获取验证码
#     message = ""  # 提示信息
#     try:
#         # 数据库查找对应的验证码，如果没有，则返回确认页面，并提示
#         confirm = models.ConfirmString.objects.get(code=code)
#     except:
#         message = "无效请求！"
#         return render(request, "myweb/confirm.html", locals())
#
#     create_time = confirm.create_time
#     now = datetime.datetime.now()
#     # 如果超过链接给定时间，则提示超时
#     if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
#         confirm.user.delete()
#         message = "您的邮件已经过期！请重新注册"
#         return render(request, "myweb/confirm.html", locals())
#     else:
#         # 如果没超时，修改字段并保存
#         confirm.user.has_confirmed = True
#         confirm.user.save()
#         # 然后就可以删掉验证码了
#         confirm.delete()
#         # 最后调到确认页面并提示成功
#         message = "确认成功，请使用账户登录！"
#         return render(request, "myweb/confirm.html", locals())
