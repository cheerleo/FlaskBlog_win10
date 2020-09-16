from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email

# 一、定义Blueprint蓝图

# 【作用】将原来放在一起的routes定义，分拆到users、posts、main路径下的routes.py中，最后再通过Blueprint整合起来
# 设置users的Blueprint类实例
users = Blueprint("users", __name__)   # 由于使用了blueprint，用users.route()替换原有的app.route()

# 二、定义users相关的routes

# 1、设置“/register”注册页面
@users.route("/register", methods=["GET", "POST"])   # 【注意】users.route()默认为GET方法，这里必须添加POST方法，才能接收用户传入信息
def set_register():
    # （1）生成注册表单实例
    register_form = RegistrationForm()

    # （2）自动获取前端用户输入的注册信息，进行验证
    # Step 1 验证注册【信息格式】及【唯一性】
    # 使用flash-WTF自带的validate_on_submit()验证用户提交的注册数据【是否符合格式要求】且【是否具有唯一性】
    # 【注意】预计这里将调用forms.py中自定义的validate_username、validate_email方法验证【数据唯一性】
    if register_form.validate_on_submit():
        # Step 2 若通过验证，则执行：
        # 哈希加密用户的密码 --> 将用户注册信息存入后端数据库 --> 弹出注册成功的提示 --> 跳转到登录页面

        # I、使用bcrypt模块，将用户注册时输入的密码使用哈希加密，生成hashed_password
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode("utf-8")

        # II、将用户注册信息储存在后台db数据库中
        # 【注意】在使用User()储存用户注册数据之前，必须要确保已经执行了db.create_all()创建数据库（我们在命令行中执行过了），否则报错，no such table:User！！！！
        user = User(username=register_form.username.data, email=register_form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # III、弹出注册成功的提示
        flash(f"Account created for {register_form.username.data} 注册成功，请登录!!", category="success")
        # 在layout.html文件中(将传入register.html文件)，使用get_flashed_messages方法调用这里的flash提示
        # 第二个参数category默认为message（无底色），但是可以传入基于bootstrap的六大标签类型default、primary、success、info、warning、danger，代表不同的底色

        # IV、登录成功后的网页跳转 redirect
        return redirect(url_for("users.set_login"))
        # redirect模块用于重定向至新的url，url_for("main.set_home")可以自动生成set_home函数对应的url路径
        # 重定向至/home路径之后，给用户展示的是home.html，且已添加flash页面提示。

    # 这里的else：pass可以省略不写，这里仅仅为了展示清晰
    else:
        pass

    # 本语句表示如果用户已经处于登录状态，在地址栏输入“/register”将直接重定向至set_home的页面
    if current_user.is_authenticated:
        return redirect(url_for("main.set_home"))

    # 【注意】这里的render_template渲染页面无论是否进行了验证，都是会执行的
    return render_template("register.html", title="Register Page", register_form=register_form)

# 2、设置“/login”登录页面

@users.route("/login", methods=["GET", "POST"])  # 【注意】必须添加POST方法，否则无法接收用户传入的登录信息
def set_login():
    # （1）生成登录表单实例
    login_form = LoginForm()

    # （2）自动获取前端用户输入的登录信息，进行验证
    # Step 1 验证登录【信息格式】
    # 用户登录也需要使用flash-WTF自带的validate_on_submit()验证用户信息，但是由于是登录，因此仅需验证【是否符合格式要求】
    # 【注意】此处没有验证【数据唯一性】的需求，因此我们在forms.py中也无需设置validate_username、validate_email函数
    if login_form.validate_on_submit():
        # Step 2 根据用户输入的email，在数据库中查找账户信息是否存在
        user = User.query.filter_by(email=login_form.email.data).first()
        # Step 3 若存在账户信息，则提取先前保存的password，与此次用户输入的password比对
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            # I、如果账户信息存在、且password比对成功，则使用flask_login模块旗下login_user函数来实现用户登录：
            login_user(user, remember=login_form.remember.data)
            # 区分不同的登录方式：【输入"/account"】或者【点击页面Login按钮】
            # 未登录情况下直接输入"/account"，将跳转到set_login登录界面，地址栏显示"/login?next=%2Faccount"，使用request.args.get获取对应account页面的url
            next_page = request.args.get("next")
            if next_page:
                # 【情况1：输入"/account"】：如果用户在浏览器地址栏直接输入"/account"进行登录，成功登录之后直接进入account页面
                flash(f"Welcome back {user.username}! 登录成功！", "success")
                return redirect(next_page)
            else:
                # 【情况2：点击页面Login按钮】：如果是点击的Login按钮进行登录，成功登录之后跳转到set_home视图页面
                flash(f"Welcome back {user.username}! 登录成功！", "success")
                return redirect(url_for("main.set_home"))
        else:
            # II、账户信息不存在或者password比对不成功，则弹出登录失败
            flash("登录失败 Login Unsuccessful. Please check your email and password.", "danger")
    # 这里的else：pass可以省略不写，这里仅仅为了展示清晰
    else:
        pass

    # 本语句表示如果用户已经处于登录状态，在地址栏输入“/login”将直接重定向至set_home的页面
    if current_user.is_authenticated:
        return redirect(url_for("main.set_home"))

    # 【注意】这里的render_template渲染页面无论是否进行了验证，都是会执行的
    return render_template("login.html", title="Login 登录", login_form=login_form)

# 3、设置用户登出的url和视图函数

# 注意：这里的视图函数set_logout不返回任何render_template渲染页面，仅有redirect重定向功能
@users.route("/logout")
def set_logout():
    # 使用flask_login模块旗下logout_user函数来实现用户登出
    logout_user()
    flash(f"已退出登录", "warning")
    return redirect(url_for("main.set_home"))

# 4、设置用户账户及账户更新界面

# 装饰器 @login_required 的作用是使得"/account"这个路由和视图函数只能在已登录的情况下访问，如果不加@login_required，输入任何情况下输入"/account"皆可访问，明显不合理；
# 加上 @login_required 之后，未登录情况下如果直接输入"/account"，将自动跳转到视图函数set_login的登录界面，地址栏显示"/login?next=%2Faccount"
# 【注意 1】
# （1）这里跳转的前提是__init__.py文件中定义了login_manager.login_view = "set_login"，告诉login_manager实例我们的登录主界面是set_login
# （2）__init__.py文件中还定义了login_manager.login_message_category = "info"，在自动跳转到set_login登录界面的同时，弹出bootstrap提示
# 【注意 2】
# 账户的默认图片default.jpg是在models.py里设置的。即定义数据库列image_file的时候，规定了默认图片为default.jpg！！

@users.route("/account", methods=["GET", "POST"])   # 【注意】必须添加POST方法，否则无法接收用户传入的账户更新信息
@login_required
def set_account():
    # （1）实例化UpdateAccountForm表单
    account_form = UpdateAccountForm()
    # "GET"和"POST"的重要区别：
    # GET方法用于获取数据，用户在浏览器地址栏输入完整url，按Enter回车键时触发。表现为后端往前端传数据，展示给用户。
    # POST方法用于提交数据，用户在前端form表单填写完数据之后，点击submit按钮时触发。表现为前端往后端传数据，存到数据库。

    # （2）设置GET和POST方法
    # 【设置GET方法】：用户进入".../account"超链接的一瞬间（通过地址栏输入url按回车，或者点击超链接按钮），就发送了一个GET请求
    # 此时，页面上需要给用户展示已有的account数据，因此才有下述从后端服务器中提取数据，再展示到前端form表单的过程！！！
    if request.method == "GET":
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email

    # 【设置POST方法】：用户填完表单数据，点击submit按钮（users/forms.py中设置了名为“Update”），即发送了POST请求
    # 调用validate_on_submit()方法，则默认用户使用 "POST" 方法传入信息。
    elif account_form.validate_on_submit():

        # （1）更新picture
        # 如果用户上传了新的picture，则使用下列代码更新账户picture
        if account_form.picture.data:
            picture_file = save_picture(account_form.picture.data)
            current_user.image_file = picture_file

        # （2）更新username和email
        # 【注意】current_user是属于flask_login模块的，是后端user账户数据的封装，便于管理当前登录的账户信息
        current_user.username = account_form.username.data
        current_user.email = account_form.email.data
        # 更新数据提交到服务器上，【注意】由于是更新信息，所以不需要add，只需commit
        db.session.commit()
        flash("Account Info Updated! 账户信息已更新！", "success")
        # 返回的依然是"/account"页面
        return redirect(url_for("users.set_account"))

    # 这里的else：pass可以省略不写，这里仅仅为了展示清晰
    else:
        pass

    image_file = url_for("static", filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account 账户页面", image_file=image_file, account_form=account_form)

# 5、得到一个用户的所有post文章（与home页面一样对所有post分页显示）
@users.route("/user/<string:username>")
def set_user_posts(username):
    page_num = request.args.get("page", default=1, type=int)
    # 通过传入的username查询用户信息，first_or_404表示获取第一个匹配的用户信息，如果查找不到，不会报错而是显示404 Not Found
    user = User.query.filter_by(username=username).first_or_404()
    # 通过找到的用户信息，查找这位用户所有的post文章，按照发布时间降序排列，并且分页
    posts = Post.query.filter_by(author=user).order_by(Post.post_date.desc()).paginate(page=page_num, per_page=5)
    # 【注意】这里传给前端页面的只是某一页的posts
    return render_template("user_posts.html", posts=posts, user=user)

# 6、设置提交重置密码请求的页面
@users.route("/reset_password", methods=["GET", "POST"])
def set_reset_request():
    # （1）如果用户已登录，进入url:"/reset_password"将直接重定向至set_home的页面 ----- 需要去掉已登录就不让修改密码的情况，因为我们在account页面也要增加重置密码功能
    # if current_user.is_authenticated:
    #     return redirect(url_for("main.set_home"))
    # （2）如果用户未登录，进入提交重置密码请求的页面，用户填写request_form表单
    request_form = RequestResetForm()
    # 用户填完表单数据，点击submit按钮，即发送了POST请求，根据RequestResetForm中定义好的验证方法来验证email信息
    if request_form.validate_on_submit():
        user = User.query.filter_by(email=request_form.email.data).first()
        send_reset_email(user)
        flash("重置密码的邮件已发送至您的邮箱，请查收！", "info")
        if current_user.is_authenticated:
            return redirect(url_for("users.set_account"))
        else:
            return redirect(url_for("users.set_login"))
    return render_template("reset_request.html", title="重置密码", request_form=request_form)

# 7、设置验证token及重置密码页面
@users.route("/reset_password/<token>", methods=["GET", "POST"])
def set_reset_token(token):
    # （1）如果用户已登录，进入url:"/reset_password/<token>"将直接重定向至set_home的页面 ----- 需要去掉已登录就不让修改密码的情况，因为我们在account页面也要增加重置密码功能
    # if current_user.is_authenticated:
    #     return redirect(url_for("main.set_home"))
    # （2）如果用户未登录，用户传入收到的token进行验证
    # 通过类名User调用静态方法verify_reset_token()验证token通过之后，得到返回的用户信息user
    user = User.verify_reset_token(token)
    # 情况 1：如果user不存在，则返回set_reset_request视图函数页面，重新提交重置请求
    if user is None:
        flash("抱歉，您的token已过期或者失效。", "warning")
        return redirect(url_for("users.set_reset_request"))
    # 情况 2：如果user存在，则进入重置密码的页面
    reset_form = ResetPasswordForm()
    if reset_form.validate_on_submit():
        # 哈希加密用户输入的新密码
        hashed_password = bcrypt.generate_password_hash(reset_form.password.data).decode("utf-8")
        # 用新密码重新赋值给数据库中的user.password
        user.password = hashed_password
        db.session.commit()
        flash(f"{user.username}账户密码更改成功!!", category="success")
        if current_user.is_authenticated:
            return redirect(url_for("users.set_account"))
        else:
            return redirect(url_for("users.set_login"))
    return render_template("reset_token.html", title="重置密码", reset_form=reset_form)
