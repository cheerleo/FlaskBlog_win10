from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

# 一、定义Blueprint蓝图

# 【作用】将原来放在一起的routes定义，分拆到users、posts、main路径下的routes.py中，最后再通过Blueprint整合起来
# 设置posts的Blueprint类实例
posts = Blueprint("posts", __name__)   # 由于使用了blueprint，用posts.route()替换原有的app.route()

# 二、定义posts相关的routes

# 1、设置博文创建界面

@posts.route("/post/new", methods=["GET", "POST"])  # 【注意】必须添加POST方法，否则无法接收用户写入的博文信息
@login_required
def set_new_post():
    post_form = PostForm()
    # （1）设置POST方法
    # 博文创建时需要空白的form表单待用户填写，并不需要GET方法提前为用户展示数据，因此无需设置GET方法
    # 出现validate_on_submit()即默认为POST方法
    if post_form.validate_on_submit():
        # （2）通过验证，写入数据
        # 依据models.py里设置的Post数据表（table）结构，将前端获取用户输入的post_form中的各类数据，存储进数据库
        # 【注意】这里是生成新的post对象
        post = Post(title=post_form.title.data, content=post_form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f"您的文章《{post.title}》创建成功！", "success")
        return redirect(url_for("main.set_home"))
    return render_template("create_post.html", title="New Post", legend="创建博文", post_form=post_form)

# 2、设置博文单独展示界面

# 这里需要向url路径中传入参数post_id，使用int:将post_id限定为integer类型的数据
# 【注意】由于设置了路径参数<int:post_id>，因此要获取post.html页面，则必须要传入相应的post_id
@posts.route("/post/<int:post_id>")
def set_read_post(post_id):
    # 使用get_or_404方法，通过post_id在后端数据库中查询是否有对应的post数据，如果没有，则返回Not Found，避免由于NoneType而报错
    post = Post.query.get_or_404(post_id)
    return render_template("read_post.html", title=post.title, post=post)

# 3、设置博文修改界面（与创建博文使用同一个create_post.html文件，只是legend不同）

@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def set_update_post(post_id):
    # （1）先通过post_id查询post数据
    post = Post.query.get_or_404(post_id)
    # （2）如果查询到的post.author对象（即该post对应的User类对象）与当前登录的User类对象不匹配，则返回403，显示Forbidden。
    # 该语句限定了：登录的用户只能修改自己对应的post博文!
    if post.author != current_user:
        abort(403)
    # （3）实例化PostForm表单
    post_form = PostForm()
    # （4）设置GET和POST方法
    # 【设置GET方法】：若用户使用GET方法，即用户进入".../update"超链接的一瞬间（通过地址栏输入url按回车，或者点击超链接按钮），就发送了一个GET请求
    # 此时，页面上需要给用户展示已有的post数据，因此才有下述从后端服务器中提取数据，再展示到前端form表单的过程！！！
    if request.method == "GET":
        post_form.title.data = post.title
        post_form.content.data = post.content

    # 【设置POST方法】：若用户在前端form表单填写了新的数据，点击submit按钮（数据库表结构中设置了名为“Post”），就发送了一个POST请求。此时立即触发form表单的validate_on_submit()数据验证方法
    # 【注意】出现validate_on_submit()即默认为POST方法
    elif post_form.validate_on_submit():
        post.title = post_form.title.data
        post.content = post_form.content.data
        db.session.commit()
        flash(f"您的文章《{post.title}》已更新!", "success")
        return redirect(url_for("posts.set_read_post", post_id=post.id))

    return render_template("create_post.html", title="Update Post", legend="修改博文", post_form=post_form)

# 4、设置博文删除界面
@posts.route("/post/<int:post_id>/delete", methods=["POST"]) # 【注意】这里设置该视图函数（即删除功能）只能通过POST方法调用，更安全，防止用GET方法时直接输入url即触发删除！！！！
@login_required
def set_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(f"您的文章《{post.title}》已删除！", "success")
    return redirect(url_for("main.set_home"))