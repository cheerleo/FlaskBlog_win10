from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

################################################################################################
#                                                                                              #
# ---------------------------- __init__文件：存放初始化配置信息------------—----------------------#
#                              所有的app.config["xxxx"]转移到config.py文件中                     #
################################################################################################

# 一、初始化各类flask扩展模块

# 1、初始化后端数据库模块
db = SQLAlchemy()

# 2、初始化用于密码加密的模块
bcrypt = Bcrypt()

# 3、初始化用于管理用户登录状态的模块
login_manager = LoginManager()
# （1）使用login_view告诉login_manager实例，我们的登录页面为set_login这个视图函数关联的界面
# "users.set_login"相当于url_for("users.set_login")的作用
login_manager.login_view = "users.set_login"
# （2）使用login_message_category，定义跳转到登录页面时的跳出提示
# 这里的info是bootstrap的提示类型
login_manager.login_message_category = "info"

# 4、初始化用于发送验证邮件的模块
mail = Mail()

# 二、定义创建flask应用（app）的主函数

# 【作用】之所以用函数形式定义app的创建，是为了可以传入不同的配置文件（定义好的Config类），创建不同的app
# 【设置默认配置】默认配置设置：config_class=Config
def create_app(config_class=Config):

    # 1、创建Flask应用程序实例app
    # 传入的__name__是为了确定资源所在的路径
    app = Flask(__name__)

    # 2、导入各种基本配置
    app.config.from_object(config_class)

    # 3、将各类flask扩展模块与app实例关联起来
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # 4、调用blueprint
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    # 5、返回创建好的app
    return app
