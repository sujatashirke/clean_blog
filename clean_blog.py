from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from werkzeug.utils  import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import json
import os
from datetime import datetime
import math

with open('config.json', 'r') as f:
    params = json.load(f)["params"]

app = Flask(__name__)
app.config['SECRET_KEY']="mynameissujata"
app.config['UPLOAD_FOLDER']= params["upload_location"]
if params["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI']= params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='sujatashirke1993@gmail.com'
app.config['MAIL_PASSWORD']='Sanvi#2817'
app.config['MAIL_DEFAULT_SENDER']='sujatashirke1993@gmail.com'

mail=Mail(app)

db= SQLAlchemy(app)

class Contact(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(80), nullable=False)
    date= db.Column(db.String(50), nullable=True)

def __repr__(self):
    return '<name %r>' % self.name

class Post(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=True)
    post_by = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    post_date = db.Column(db.String(80), nullable=True)
    imgfile= db.Column(db.String(80), nullable=True)

def __repr__(self):
    return '<title %r>' % self.title

@app.route('/post/<sno>')
def post_route(sno):
    if 'user' in session and session['user'] == 'admin':
        post = Post.query.filter_by(srno=sno).first()
        return render_template('post.html', post=post)
    else:
        return redirect(url_for('login'))

@app.route('/edit/<string:post_sno>', methods=['GET', 'POST'])
def edit(post_sno):
    if 'user' in session and session['user'] == 'admin':
        post = Post.query.filter_by(srno=post_sno).first()
        if request.method == 'POST':
            if post_sno == '0':
                title = request.form['p_title']
                slug = request.form.get('p_slug')
                tagline = request.form.get('p_tagline')
                content = request.form.get('p_content')
                img_file= request.files['img_file']
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
                print("title {}|slug {}|tagline {}|content {}".format(title, slug, tagline, content))
                post = Post(title=title, slug=slug, tagline=tagline, content=content, post_by=session['user'],post_date=datetime.now(), imgfile=img_file)
                db.session.add(post)
                db.session.commit()
                flash('post data added successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                post.title = request.form.get('p_title')
                post.slug = request.form.get('p_slug')
                post.tagline = request.form.get('p_tagline')
                post.content = request.form.get('p_content')
                img_file = request.files['img_file']
                img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename)))
                post.imgfile=secure_filename(img_file.filename)
                db.session.commit()
                flash('post data updated successfully', 'success')
                return redirect(url_for('dashboard'))
        else:
            return render_template('edit.html', post=post, sno=post_sno)
    return redirect(url_for('login'))

@app.route('/delete/<string:post_sno>', methods=['GET', 'POST'])
def delete(post_sno):
    if 'user' in session and session['user'] == 'admin':
        post = Post.query.filter_by(srno=post_sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('update_post'))
    return redirect(url_for('login'))


@app.route('/update_post', methods=['GET', 'POST'])
def update_post():
    if 'user' in session and session['user'] == 'admin':
        posts= Post.query.all()
        return render_template('update_post.html', posts=posts)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user' in session and session['user'] == 'admin':
        page= request.args.get('page', 1, type=int)
        no_of_pages = math.ceil(Post.query.count()/4)
        print("page=", page)
        ltidx = page * 4
        posts= Post.query.order_by(desc(Post.post_date)).all()[ltidx-4:ltidx]
        #posts = Post.query.all()[ltidx-4:ltidx]
        print("no of pages", no_of_pages)
        if page == 1:
            next= "?page="+ str(page+1)
            prev= "#"
        elif page >= no_of_pages:
            next="#"
            prev="?page="+ str(page-1)
        else:
            next = "?page="+ str(page+1)
            prev = "?page="+ str(page-1)
        print("size of posts", len(posts))
        print("next", next)
        print("prev=", prev)
       # print(no_of_pages, type(no_of_pages))
        return render_template('index.html', posts=posts, next=next, prev=prev)
    else:
        posts = Post.query.order_by(desc(Post.post_date)).limit(4).all()
        return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    uname = request.form.get('uname')
    pwd = request.form.get('password')
    if request.method == 'POST':
        if uname == 'admin' and pwd == 'admin':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        else:
            flash("Username / password is incorrect", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name= request.form.get('name')
        phone=request.form.get('phone')
        email=request.form.get('email')
        message=request.form.get('message')
        contact= Contact(name=name, phone=phone, email=email, message=message, date=datetime.now())
        db.session.add(contact)
        db.session.commit()
        msg= Message()
        msg.subject="New Message from {}".format(name)
        msg.recipients=["sujatashirke1993@gmail.com", email]
        msg.html="<b>Name:</b> {}<br><b>phone: </b>{}<br><b>message:</b> {}".format(name, phone, message)
        mail.send(msg)
        flash('We receive your message.will contact you soon', 'success')
        return redirect(url_for('contact'))
    else:
        return render_template('contact.html')

if __name__=='__main__':
    app.run(debug=True)
