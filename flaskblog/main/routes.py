from flask import render_template, request, Blueprint
from flaskblog.models import Post

# 一、定义Blueprint蓝图

# 【作用】将原来放在一起的routes定义，分拆到users、posts、main路径下的routes.py中，最后再通过Blueprint整合起来
# 设置main的Blueprint类实例
main = Blueprint("main", __name__)   # 由于使用了blueprint，用main.route()替换原有的app.route()

# 二、定义main相关的routes

# 1、设置“/”根目录及"/home"目录页面

# 定义的set_home函数称为【视图函数】，通过路由router与传入的url相连
# 通过两个装饰器，将set_home【视图函数】与【路径url】："/"、"/home"同时相连
# app.route()默认为HTTP的GET方法，其他方法需要使用methods=["GET", "POST"]手动添加

@main.route("/")
@main.route("/home")
# @login_required       # 如果这里加上@login_required，则进入网站主页首先要登录，可以根据需求添加这个装饰器 -------------- 可以思考如何关闭注册通道，仅允许已有的用户登录，保持隐私！！！
def set_home():
    # （1）定义page变量用于翻页
    # 【原理】：用户使用GET方法时，如果需要传递参数，就必须在url上直接明文传入，例如用户输入这样的url："/home?page=xxx"
    # 【获取GET参数】：使用request.args.get()方法，即可获取用户通过url传入的参数值。page称为key，xxx就是对应的value。
    # 这里default=1表示如果用户没有输入page参数值，则默认page=1，因此page_num默认为1。另外，定义用户输入的page value必须为int类型。
    page_num = request.args.get("page", default=1, type=int)
    # （2）使用paginate方法将所有post自动分页，之后可分页查询数据库中的post数据，per_page=3表示每页展示3个post，page=page表示传入用户输入的page value
    # 使用order_by(Post.post_date.desc())对查到的post按照发布时间，降序排列
    posts = Post.query.order_by(Post.post_date.desc()).paginate(page=page_num, per_page=5)
    # （3）将查询到的post数据传给前端home.html显示
    # 【注意】这里传给前端页面的只是某一页的posts！！！
    return render_template("home.html", posts=posts)
    # render_template的功能是先引入home.html，同时根据传入的关键字参数，对html进行修改渲染。
    # 【注意】这里绕过了前端form表单，直接将后端数据展示给用户（浏览器） ！！！！

# 2、设置“/about”目录页面

@main.route("/about")
def set_about():
    return render_template("about.html", title="About Page")