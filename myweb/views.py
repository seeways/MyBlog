from django.shortcuts import render, redirect
from . import models


# Create your views here.


def index(request):
    return render(request, 'myweb/index.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get("username", None)  # 默认值为None
        password = request.POST.get("password", None)
        message = "请填写完整信息！"
        print("username:", username, "password:", password)
        if username and password:  # 非空验证
            username = username.strip()  # 去空
            try:
                user = models.User.objects.get(username=username)
                if user.password == password:
                    return redirect("/index/")
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'myweb/login.html', {"message": message})
    return render(request, 'myweb/login.html')


def register(request):
    return render(request, 'myweb/register.html')


def logout(request):
    return redirect("/index/")
