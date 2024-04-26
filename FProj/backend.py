from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from passlib.hash import sha256_crypt
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
#im scared abt the midterm
#me too :( I think i will fail 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#Database Information & Classes
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Post(db.model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String, unique = True, nullable = False)
    description = db.Column(db.String)
    label = db.Column(db.String())
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    numPost = db.Column(db.Integer, default=0)
    

    # Dynamic relationship to get followers count
    followers = db.Column(db.Integer, default=0, nullable=False)
    # Dynamic relationship to get following count
    following = db.Column(db.Integer, default=0, nullable=False)

    # Define relationship to UserFollowing table
    following_relationships = db.relationship("UserFollowing", foreign_keys='UserFollowing.user_id', backref='user')

    def check_password(self, password):
        return self.password == password 

    def update_followers_count(self):
        self.followers = db.session.query(db.func.count(UserFollowing.follower_id)).filter(UserFollowing.user_id == self.id).scalar()

    def update_following_count(self):
        self.following = db.session.query(db.func.count(UserFollowing.follower_id)).filter(UserFollowing.follower_id == self.id).scalar()

class UserFollowing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 

    
#Admin , we can go to the admin page with /admin
#We do not need any special html that comes with it
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/login')
def login_page():
    return render_template('login.html')

####################
# WORK HERE
####################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.username == username:
            storedPassword = user.password
            if sha256_crypt.verify(password, storedPassword):
                login_user(user)
                return redirect(url_for('account'))
            else:
                return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forum')
def post_page():
    return render_template('forum.html')

@app.route('/forum', methods =['POST','GET'])


# Add User to DB 
@app.route('/register')
def register():
    return render_template('create.html')

@app.route('/register', methods=['POST'])
def register_post():
    data = request.json
    print("Received JSON data:", data)  
    username = data.get('username')
    password = data.get('password')
    
    hashedPassword = sha256_crypt.hash(password)
    if username is None or password is None:
        return jsonify({'error': 'Missing username or password'}), 400
    new_user = User(username=username, password=hashedPassword,followers = 0, following = 0, numPost = 0)
    print("New User ID:", new_user.id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully'}), 201


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        # Handle any POST requests for the account page here if needed
        pass
    return render_template('account.html')


def getUserID(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user.id
    else:
        return None

def add_follower(user_id, follower_id):
    new_following = UserFollowing(user_id=user_id, follower_id=follower_id)
    db.session.add(new_following)
    db.session.commit()
    user = User.query.get(user_id)
    follower = User.query.get(follower_id)
    user.update_followers_count()
    follower.update_following_count()
    db.session.commit()
    
#Add Student To Course if logged in
#Main Page for Users
@app.route('/main')
def mainPage():
    return render_template('main.html')
#Search Bar for Images
@app.route('/search')
def searchPage():
    return render_template('search.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
