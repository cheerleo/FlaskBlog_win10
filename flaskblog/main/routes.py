from flask import render_template, url_for, flash, request, Blueprint, current_app, jsonify, redirect
from flaskblog.models import Post
from flaskblog.main.forms import PredictForm
from flaskblog.main.utils import save_pred_picture
from flask_login import current_user, login_required
from flaskblog import db

import os
import json
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from flaskblog.mobile_model import MobileNetV2


# 一、定义Blueprint蓝图

# 【作用】将原来放在一起的routes定义，分拆到users、posts、main路径下的routes.py中，最后再通过Blueprint整合起来
# 设置main的Blueprint类实例
main = Blueprint("main", __name__)   # 由于使用了blueprint，用main.route()替换原有的app.route()

# 二、设置“/”根目录及"/home"目录页面

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


# 三、定义"/ai"图像分类预测主页面
# set_ai视图函数主要用于读取并展示图片
# 【注意】
# （1）没有图片上传时，print(current_user.pic_name)输出current_user.pic_name，此时pic_url为"/static/predict_pics/current_user.pic_name"
# （2）发生图片上传时，print(current_user.pic_name)输出{文件名}，此时pic_url为"/static/predict_pics/{文件名}"

@main.route("/ai", methods=["GET", "POST"])
@login_required
def set_ai():

    predict_form = PredictForm()

    # 【设置GET方法】：展示读取的图片
    # 已通过jinja2实现有图片上传时，显示上传的图片
    print(f"新POST前导入的图片名：{current_user.pic_name}")  # 如果没有图片上传，则输出current_user.pic_name

    # 【设置POST方法】：用户填完表单数据，点击submit按钮
    if predict_form.validate_on_submit():
        # 如果用户上传了新的picture，则使用下列代码更新picture
        if predict_form.picture.data:
            pic_name = save_pred_picture(predict_form.picture.data)
            # 【注意】save_pred_picture的作用是存储读取的图片、输出自定义的文件名
            current_user.pic_name = pic_name
            # 这里的current_user.pic_name是两个路由"/ai"和"/ai/predict"之间传递图像的关键桥梁，但实际上并没有在db文件中创建Pred的实例！！！！！！！！
            db.session.commit()

    print(f"导入的图片名：{current_user.pic_name}")
    pic_url = url_for("static", filename=f"predict_pics/{current_user.pic_name}")

    print(f"导入的图片保存路径：{pic_url}")
    return render_template("ai.html", title="预测图片", predict_form=predict_form, pic_url=pic_url)

# 四、定义"/ai/predict"预测主routes
@main.route("/ai/predict", methods=["GET", "POST"])
@torch.no_grad()                   # torch.no_grad()提高测试运行效率
@login_required
def predict():
    # 1. 定义模型初始化相关信息
    # （1）定义权重文件和类别说明文件的路径
    weights_path = f"{current_app.root_path}/static/mobile_net/MobileNetV2(flower).pth"  # 【注意】这里必须用current_user定位路径，用url_for会报错！！
    class_json_path = f"{current_app.root_path}/static/mobile_net/class_indices.json"  # 【注意】这里必须用current_user定位路径，用url_for会报错！！
    assert os.path.exists(weights_path), "抱歉，无法执行预测，模型权重文件不存在"  # assert后面的判断语句如果为false，程序崩溃抛出异常。
    assert os.path.exists(class_json_path), "抱歉，无法执行预测，类别说明文件不存在"
    # （2）选择设备：cpu或者gpu
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # print(device)
    # （3）生成MobileNet模型实例
    model = MobileNetV2(num_classes=5)
    # （4）读取训练得到的权重文件
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.to(device)
    # （5）读取储存了训练类别的json文件
    json_file = open(class_json_path, 'rb')
    class_indict = json.load(json_file)

    # 2. 读取图片并转换
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])

    img_pil = Image.open(f"{current_app.root_path}/static/predict_pics/{current_user.pic_name}")       # 传入要预测的图片s2.jpg
    img_tensor = my_transforms(img_pil)
    img_tensor = img_tensor.to(device)
    img_tensor = torch.unsqueeze(img_tensor, dim=0)      # 【重要】使用unsqueeze添加batch_size的维度，使该tensor符合模型运算要求。shape变为torch.Size([1, 3, 224, 224])

    # 3. 启动预测主程序
    model.eval()

    pred = model(img_tensor)                             # 经过模型运算，pred的shape变成torch.Size([1, 10])。其中，dim=0维度值是1，表示Height，dim=1维度值是10，表示一行的Width
    pred_index = pred.argmax(dim=1).item()               # argmax(dim=1)表示在Width范围上，取一行中最大值的索引号
    pred_prob_num = F.softmax(pred, dim=1).max().item()  # dim=1表示在Width范围上，计算一行中每个元素的softmax概率值，这些概率值相加的和为1
    # 【重要】先算出预测结果pred中每个元素的softmax概率(每个元素概率和为1)，再找出其中的最大值，即为预测属于最可能的类别的概率

    flash(f"分类识别结果：{class_indict[str(pred_index)]}， 类别概率：{pred_prob_num:.8f}", "success")  # :.8f保留六位小数
    return redirect(url_for("main.set_ai"))

