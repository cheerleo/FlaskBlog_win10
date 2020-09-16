from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class PredictForm(FlaskForm):

    picture = FileField("", validators=[FileAllowed(["jpg", "jpeg", "png"])])
    submit = SubmitField("上传")
