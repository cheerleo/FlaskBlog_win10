from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app   # 使用flask模块已有的current_app模块管理app
from flaskblog import db, login_manager  # 相当于from flaskblog.__init__ import db, login_manager, app
from flask_login import UserMixin


################################################################################################
#                                      【 后 端 数 据 库 设 置  】                                #
# ----------------------------- models文件：设置后端数据库中的各类table  --------—--------------#
#   ！！！！！！！！！！！！！！   注意区分后端数据库table和前端的form表单  ！！！！！！！！！！！！！！！！ #
################################################################################################

# 一、管理用户登录状态
# 使用flask_login模块旗下LoginManager类生成的实例login_manager，管理用户登录状态信息 ----- 这是个回调函数？？？？？？？？
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 二、重要：使用python类的构建形式，创建后端数据库内的各种表（table）！

# 1、创建名为User的表（table），管理账户信息
# 【注意】这里同时也继承了flask_login模块下的UserMixin类，实现用户登录状态管理

class User(db.Model, UserMixin):
    # （1）设置table相关属性
    # __tablename__ = "User"                                                    # 用于设置table的名字，table表名默认为类名User
    id = db.Column(db.Integer, primary_key=True)                                # 定义为primary_key的属性会自动生成编号
    username = db.Column(db.String(20), unique=True, nullable=False)            # db.String(20)中的20表示限制最大length，nullable=False表示不能为空
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(20), nullable=False)

    # 【这里的posts并不是新增的column，而是与Post类相连，在Post类中增加一个column称为author。】 db.relationship的用法需要学习！！！！！！！
    # 【注意】由于author的存在，Post类对象.author等价于与其相对应的User类对象
    # 因此，print(Post类对象.author)等价于print(对应User类对象)，将输出"用户信息< 用户名：{对应User类对象.username}, 邮箱：{对应User类对象.email}, 头像：{对应User类对象.image_file} >"
    # 另外，也可以直接使用print(Post类对象.author.username)等输出账户相关的信息，相当于print(对应User类对象.username)
    posts = db.relationship("Post", backref="author", lazy=True)

    # 用户修改密码的处理流程：？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？需确认？？？？？？？？？？？？？？？
    # step 1：用户提出修改密码请求时，后台根据用户email地址，查询到对应的user_id（即self.id），打包生成token秘钥，
    # step 2：后台将token发送到用户email地址，
    # step 3：用户拿着这个收到的token，提交给后台，后台解析出包含的user_id（即self.id）
    # step 4：后台根据user_id（即self.id）查询对应的账户信息，从而允许用户修改密码

    # （2）设置生成重置token秘钥的方法
    # expires_sec=1800表示生成的秘钥在1800秒内失效
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_sec)
        # 将self.id打包进token秘钥，将token发送到用户email地址，用户可以拿着这个秘钥，解析出包含的self.id，即可查询到对应的账户信息，从而修改密码？？？？？？？？？
        return s.dumps({"user_id": self.id}).decode("utf-8")

    # （3）设置解析token秘钥，获取user_id（即self.id）的方法
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        # 利用try...except捕捉异常，except后边通常应该加上具体的“异常名称”，这里没写
        try:
            user_id = s.loads(token)["user_id"]   # 从获取的token中，解析出user_id（即self.id）
        except:
            return None                           # 如果因为token过期、token错误等各种情况，解析不出user_id，则返回None
        return User.query.get(user_id)            # 利用解析出的user_id（即self.id），查询对应的账户信息



    # （4）定义了直接print(User类对象)的输出内容
    def __repr__(self):
        return f"用户信息< 用户名：{self.username}, 邮箱：{self.email}, 头像：{self.image_file} >"

# 2、创建名为Post的表（table），管理博文信息

class Post(db.Model):
    # （1）设置table相关属性
    # __tablename__ = "Post"                                                    # 用于设置table的名字，table表名默认为类名Post
    id = db.Column(db.Integer, primary_key=True)                                # 定义为primary_key的属性会自动生成编号
    title = db.Column(db.String(100), nullable=False)
    post_date = db.Column(db.DateTime, nullable=False, default=datetime.now) # 使用datetime模块中的datetime.utcnow方法获取当前时间
    # 我们在alexnet模型代码中，写了：now_str = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")  使用datetime模块里的datetime.now()方法取得当前时间，并格式化 #
    content = db.Column(db.Text, nullable=False)

    # 【这里的user_id需要理解！】  db.ForeignKey的用法需要学习！！！！！！！
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # （2）定义了直接print(Post类对象)的输出内容
    def __repr__(self):
        return f"博文信息< 文章标题：{self.title}, 发布时间：{self.post_date} >"