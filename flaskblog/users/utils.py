import os
import secrets
from PIL import Image
from flask import url_for, current_app # 使用flask模块已有的current_app模块管理app
from flask_mail import Message
from flaskblog import mail

# 定义保存用户上传账户照片的函数：
def save_picture(uploaded_pic):
    # （1）使用secrets库生成一个随机的8字节十六进制token，用于给uploaded_pic重命名，随机token命名的好处就是文件名不会有重复
    random_base = secrets.token_hex(nbytes=8)
    # （2）使用os.path.splitext获取uploaded_pic的原文件名pic_name、原文件扩展名pic_extension
    pic_base, pic_extension = os.path.splitext(uploaded_pic.filename)
    # （3）使用(随机文件名random_name + 原文件扩展名pic_extension)组成一个完整的新文件名new_filename
    new_filename = random_base + pic_extension
    # （4）定义uploaded_pic上传之后存储的路径，并且定义存储的文件名
    # app.root_path得到app生成的根目录，即E:\A-learn to code\python_learn\flask-learn\flaskblog
    # 注意：这里路径斜杠方向不一样，也是可以结合的
    save_path = f"{current_app.root_path}/static/profile_pics/{new_filename}"
    # （5）将uploaded_pic的尺寸进行压缩，并储存到save_path路径
    # 压缩的目的是为了不给服务器的存储空间造成太大压力
    compressed_pic = Image.open(uploaded_pic)
    # 【注意】这里使用的是Image模块下的thumbnail方法而不是resize方法!!!!!!!!!!!!!!!!!!
    # thumbnail方法用于制作当前图片的缩略图，参数size指定了图片的最大的宽度和高度（处理过的图片不会有拉伸），以达到减少图片大小的目的
    compressed_pic.thumbnail(size=(225, 225))
    compressed_pic.save(save_path)

    return new_filename


# 定义发送密码重置邮件的函数：
def send_reset_email(user):
    # 通过User类的对象user调用实例方法get_reset_token，加密user.id生成token，注意这个token只有1800秒的有效时间
    token = user.get_reset_token()
    # Message里的sender参数值必须和app.config["MAIL_USERNAME"]相同
    msg = Message("Password Reset Request", sender="zytleo@qq.com", recipients=[user.email])
    # _external=True参数表示生成的url是个绝对路径
    msg.body = f"""
               请点击以下链接重置密码，链接30分钟内有效:

               {url_for("users.set_reset_token", token=token, _external=True)}

               If you did not make this request, then simply ignore this email and no changes will be made.
                """
    # 【重要】必须要记得send邮件！！！
    mail.send(msg)