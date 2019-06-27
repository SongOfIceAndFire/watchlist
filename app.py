import os
import sys
import click

from flask import Flask,render_template
from flask import url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy

WIN=sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False   #关闭对模型修改的监控
app.config['SECRET_KEY']='dev'                       #等同于 app.secret_key = 'dev'

db=SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True) #主键
    name=db.Column(db.String(60))             #名字


class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True) #主键
    title=db.Column(db.String(60))            #电影标题
    year=db.Column(db.String(4))              #电影年份



@app.context_processor
def inject_user():
    user=User.query.first()
    return dict(user=user)


#initialize the database.
@app.cli.command() #注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.')  #设置选项
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('initialize the database.')

#generate fake data.
@app.cli.command()
def forge():
    db.create_all()
    name='yangyuheng'
    movies=[
        {'title':'My neighbor Totoro','year':'1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},

    ]
    user=User(name=name)
    db.session.add(user)

    for m in movies:
        movie=Movie(title=m['title'],year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done')





@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        title=request.form.get('title')
        year=request.form.get('year')

        #验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        movie=Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies=Movie.query.all()
    return render_template('index.html',movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
    movie=Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))




#404错误处理函数
@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html'),404


