from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User

# 一、定义前端register注册表单

class RegistrationForm(FlaskForm):

    # （一）定义表单属性及数据格式要求
    # 【注意 1】以下定义的皆为类变量，可以用类名、对象名调用
    # 【注意 2】内置数据格式判断语句，错误提示出现在相应的输入框下边：
    # username：raise ValidationError("Field must be between 2 and 20 characters long.")，
    # email：raise ValidationError("Invalid email address.")
    # password：raise ValidationError("Field cannot be longer than 20 characters.")
    # confirm_password：raise ValidationError("Field must be equal to password.")

    username = StringField("username", validators=[DataRequired(), Length(min=2, max=20)])  # validators用来规定输入的数据格式。DataRequired表示不能为空，Length约定了最小和最大字符数
    email = StringField("email", validators=[DataRequired(), Email()])  # DataRequired表示不能为空，Email表示需要符合邮件格式
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    # （二）自定义方法 —— 保证数据的唯一性
    # 自动验证用户输入的username是否唯一，不唯一则报错ValidationError
    # 【注意】函数名必须是validate_username，否则该验证函数失效！！！！！！---------------------------------为什么一定要固定写validate_username(self, username)，且这个函数如何被调用的待研究！！！！！！！
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("该用户名已被注册")
            # 【注意】raise的提示将出现在username输入框的下边，在前端html代码里设置显示格式，与flash提示不同！！！！！

    # 自动验证用户输入的email是否唯一，不唯一则报错ValidationError
    # 【注意】函数名必须是validate_email，否则该验证函数失效！！！！！！------------------------------------为什么一定要固定写validate_username(self, email)，且这个函数如何被调用的待研究！！！！！！！
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("该邮箱已被注册")
            # 【注意】raise的提示将出现在email输入框的下边，在前端html代码里设置显示格式，与flash提示不同！！！！！

# 二、定义前端login登录表单

class LoginForm(FlaskForm):

    # （一）定义表单属性及数据格式要求
    # 【注意】我们这里定义了需要email和password来登录，当然也可以根据需要设置用户可以使用username登录
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

    # （二）无需另外自定义方法
    # 注意：与register注册表单需要验证username和email的唯一性不同，login登录需要的是查找username和email是否存在，因此这里不定义验证函数！！！！

# 三、定义前端account update信息更新表单

class UpdateAccountForm(FlaskForm):

    # （一）定义表单属性及数据格式要求
    username = StringField("username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("email", validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg", "jpeg", "png", "gif"])])
    submit = SubmitField("Update")

    # （二）自定义方法 —— 保证数据的唯一性
    def validate_username(self, username):
        # 只有当新输入的username与当前已登录用户current_user的username不相同时，才执行以下验证：
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("该用户名已被注册")

    def validate_email(self, email):
        # 只有当新输入的email与当前已登录用户current_user的email不相同时，才执行以下验证：
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("该邮箱已被注册")


# 四、定义提交重置密码请求的表单

class RequestResetForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:  # 【注意】这里需要判断的与RegistrationForm里相反
            raise ValidationError("该邮箱未注册，请直接注册！")

# 五、定义设置新密码的表单

class ResetPasswordForm(FlaskForm):
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")
