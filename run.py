################################################################################################
#                                                                                              #
# ---------------------------- run文件：整个项目的服务器启动入口-------------—---------------------#
#                                                                                              #
################################################################################################

from flaskblog import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

