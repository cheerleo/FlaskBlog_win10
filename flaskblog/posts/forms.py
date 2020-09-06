from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

# 定义前端post博文的表单
class PostForm(FlaskForm):

    title = StringField("标题", validators=[DataRequired()])
    content = TextAreaField("正文", id="tinymce_editor")  # 注意：id="content"表示使用设置好的TinyMCE编辑器，与validators=[DataRequired()]不能共用，否则无法提交！！！！
    submit = SubmitField("Post")