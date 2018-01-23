from django.db import models


class User(models.Model):
    gender = (
        ("male", "男"),
        ("female", "女"),
    )

    username = models.CharField(max_length=128, unique=True)  # 用户名
    password = models.CharField(max_length=128)  # 密码
    email = models.EmailField(unique=True)  # Email
    sex = models.CharField(max_length=32, choices=gender, default="男")  # 性别
    nickname = models.CharField(max_length=128, default='')  # 昵称
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    has_confirmed = models.BooleanField(default=False)  # 是否验证

    def __str__(self):
        if self.nickname == '' or self.nickname is None:
            return self.username
        else:
            return self.username + "(" + self.nickname + ")"

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
