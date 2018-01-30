"""MyBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from myweb import views
from myweb import urls as myweb_urls

urlpatterns = [
    # url(r'^index/', views.index),
    # url(r'^login/', views.login),
    # url(r'^register/', views.register),
    # url(r'^logout/', views.logout),
    # url(r'^captcha', include('captcha.urls')),
    # url(r'^confirm/$', views.user_confirm),

    url(r'^blog/', include(myweb_urls)),
    url(r'^$', views.index, name='index'),  # 默认主页转发到index
    url(r'^admin/', include(admin.site.urls)),
]

