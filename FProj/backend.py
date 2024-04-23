
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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # follow = db.Column(db.Integer, default = 0)
    # following = db.Column(db.Integer, default = 0)
    # numPost = db.Column(db.Integer, default = 0)
    # is_admin = db.Column(db.Boolean, default = False) 

    def check_password(self, password):
        return self.password == password 





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
    new_user = User(username=username, password=hashedPassword)
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
