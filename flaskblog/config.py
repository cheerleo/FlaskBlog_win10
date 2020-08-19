import os

# 环境变量
# 【作用】将一些敏感的数值添加到环境变量中，是为了保密，使其不直接在代码中展示出来
# 【添加】系统属性 --> 高级 --> 环境变量 --> ASUS的用户变量处手动新建
# 【提取】使用os.environ.get()获取提前添加环境变量值
# 【注意】新添加的环境变量需要重启之后，才能获取到值！！！！！

class Config:

    # （1）创建RegistrationForm()时候必须要有。A secret key is required to use CSRF.
    # 具体的值已经提前手动添加到系统环境变量（ASUS的用户变量）中
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # （2）定义一个轻量级数据库的地址URI
    # 具体的值已经提前手动添加到系统环境变量（ASUS的用户变量）中
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # （3）自动发送验证邮件的邮箱配置
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = 465                      # SSL加密方式对应的端口
    MAIL_USE_SSL = True                  # qq邮箱需要SSL加密方式
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 我的qq邮箱地址已经提前添加到系统环境变量（ASUS的用户变量）中
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 【注意】这里是qq邮箱IMAP/SMTP服务授权码，不是邮箱登录密码。授权码已经提前添加到系统环境变量（ASUS的用户变量）中