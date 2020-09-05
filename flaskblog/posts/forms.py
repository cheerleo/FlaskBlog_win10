from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

# 定义前端post博文的表单
class PostForm(FlaskForm):

    title = StringField("标题", validators=[DataRequired()])
    content = TextAreaField("正文", validators=[DataRequired()])
    submit = SubmitField("Post")