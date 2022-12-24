from flask import Flask
from werkzeug.utils import secure_filename
from flask import Flask,render_template,request,redirect
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_login import login_user, logout_user, current_user, login_required



UPLOAD_FOLDER = os.path.join('static', 'uploads')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/postsave'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hardsecretkeyxyz'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Post(db.Model):
    with app.app_context():
        sno = db.Column(db.Integer, primary_key=True)
        title= db.Column(db.String(80), nullable=False)
        desc = db.Column(db.String(200), nullable=False)
        name = db.Column(db.String(20), nullable=False)
        category = db.Column(db.String(20),nullable=False)
        image = db.Column(db.String(100), nullable=False)
        
    def __repr__(self):
        return '<User %r>' % self.title
app.app_context().push()        
db.create_all()

class Information(db.Model):
    name = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(200),  primary_key=True)
    massage = db.Column(db.String(20), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.name
db.create_all()

class Register(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username
db.create_all()

@app.route("/postsave",methods =['GET','POST'])
@login_required
def postsave():
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        name = request.form['name']
        category = request.form['cate']
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        print("filename",filename)
        todo = Post(title=title, desc=desc, name=name, category=category, image=filename)
        db.session.add(todo)
        db.session.commit()
    all = Post.query.all()
    
    return render_template("admin.html",all=all)  

@app.route("/update/<int:sno>",methods =['GET','POST'])
@login_required
def update(sno):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        name = request.form['name']
        category = request.form['cate']
        todo= Post.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc= desc
        todo.name = name
        todo.category = category
        db.session.add(todo)
        db.session.commit()
        return redirect("/postsave")

    
    todo= Post.query.filter_by(sno=sno).first()

    return render_template('update.html',todo=todo)    

@app.route('/delete/<int:sno>')
@login_required
def delete(sno):
    todo= Post.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/postsave')  


@app.route('/')
def home():
    all = Post.query.all()
    return render_template("index.html",all = all)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact',methods =['GET','POST']) 
def contactas():
    if request.method=='POST':
        # print(request.Post)
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        todo = Information(name=name, email=email, massage=message)
        db.session.add(todo)
        db.session.commit()
    return render_template("contact.html")
  
@app.route('/blog')
def blog():
    all = Post.query.all()
    return render_template("blog.html",all=all)

@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

@app.route('/login',methods =['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        obj = Register.query.filter_by(username =username, password = password).first()
        login_user(obj)
        print("object",obj)
        print(username)
        print(password)
        return redirect('/')
    return render_template('login.html')    
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@app.route('/register',methods =['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        print(username)
        if password1==password2:
         data = Register(username = username, email = email, password = password1)
         db.session.add(data)
         db.session.commit()
        else:
            print("password1 and password2 are different") 
    return render_template("register.html")
    

if __name__ == "__main__" :
    app.run(debug=True)      