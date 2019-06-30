import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager




WIN=sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(app.root_path,os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False   #关闭对模型修改的监控
app.config['SECRET_KEY']=os.get('SECRET_KEY','dev')                       #等同于 app.secret_key = 'dev'

db=SQLAlchemy(app)

#Flask-Login 会把用户重定向到登录页面，并显示一个错误提示。为了让这个重定向操作正确执行，我们还需要把 login_manager.login_view 的值设为我们程序的登录视图端点（函数名）：
login_manager=LoginManager(app) #实例化拓展类

login_manager.login_view='login'
# 创建用户加载回调函数，接受用户 ID 作为参数
@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user=User.query.get(int(user_id))
    return user      #返回用户对象


@app.context_processor
def inject_user():
    from watchlist.models import User
    user=User.query.first()
    return dict(user=user)



from watchlist import views, errors, commands