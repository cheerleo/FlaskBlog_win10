from flask import Blueprint, render_template

# 一、创建errors的蓝图实例
errors = Blueprint("errors", __name__)

# 二、定义处理错误界面（404、403、500）的route，这里称为errorhandler
# handlers.py的作用类似routes.py

# app_errorhandler方法对整个app有效
@errors.app_errorhandler(404)
def error_404(error):
    return render_template("errors/404.html"), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template("errors/403.html"), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template("errors/500.html"), 500