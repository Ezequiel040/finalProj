from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from passlib.hash import sha256_crypt
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
#im scared abt the midterm
#me too :( I think i will fail 
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'FProj/static/Images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Database Information & Classes
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    ingredients = db.Column(db.String, nullable = False)
    label = db.Column(db.String(), nullable = False)
    picture = db.Column(db.String(), nullable = False)
    upvote = db.Column(db.Integer, default = 0, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))

#Comments used only for posts
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    comment = db.Column(db.String, nullable = False)
    upvote = db.Column(db.Integer, default = 0, nullable = False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

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

# @app.route('/forum')
# def post_page():
#     return render_template('forum.html')

# @app.route('/forum', methods =['POST','GET'])


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

@app.route('/account')
@login_required
def account():
    posts = current_user.posts
    num_posts = len(posts)
    return render_template('account.html', posts=posts, num_posts=num_posts)

#Add Student To Course if logged in
# #Main Page for Users
# @app.route('/main')
# def mainPage():
#     return render_template('main.html')
@app.route('/users')
def display_users():
    # Query all users from the database
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/main')
def mainPage():
    if current_user.is_authenticated:
        posts = Post.query.all()
        popularPosts = Post.query.order_by(Post.upvote.desc()).all()
        
        topPosts = popularPosts[:3]
        return render_template('main.html', posts=posts,popularPosts = topPosts)
    else:
        return redirect(url_for('login'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    # Find the post by its ID
    post = Post.query.get(post_id)
    if post:
        # Increment the upvote count for the post
        post.upvote += 1
        # Commit the changes to the database
        db.session.commit()
        # Return a JSON response indicating success
        return jsonify({'success': True, 'message': 'Post upvoted successfully'})
    else:
        # If post with the given ID doesn't exist, return a JSON response with error message
        return jsonify({'success': False, 'message': 'Post not found'}), 404

# No need for another route '/main' with login_required decorator

# @app.route('/main')
# def mainPage():
#     return render_template('main.html')

# @app.route('/main')
# @login_required
# def viewFront(post_id):
#     user = User.query.filter_by(username = current_user.username).first()
#     postt = Post.query.filter(post_id=post.id).all()
#     comments = Comments.query.filter_by(post_id=post_id).all()
#     #Will need Comments query.join later 
#     #ex: comments = Comment.query.join(commentwhatever)
#     posts = []
#     for i in postt:
#         post = Post.query.get(i.post_id)
#         if post:
#             posts.append(post)
#     return render_template('main.html', posts = posts)
        # return render_template('main.html', post=post, comments=comments, post_id=post_id)

#Search Bar for Images
@app.route('/search')
def searchPage():
    return render_template('search.html')

#Making sure the student can make a post
############
@app.route('/post')
@login_required
def postPage():
    return render_template('post.html')

#View a specific post, will be useful for main
@app.route('/postView/<int:post_id>')
@login_required
def viewPost(post_id):
    post = Post.query.get(post_id)
    comments = Comments.query.filter_by(post_id=post_id).all()
    print(post)
    #Will need Comments query.join later 
    #ex: comments = Comment.query.join(commentwhatever)
    if post:
        return render_template('postView.html', post=post, comments=comments, post_id=post_id)
    else:
        #Error, will send you back if it doesnt find a post
        return render_template('/main')

@app.route('/submit', methods=['POST'])
@login_required
def submitPostInfo():
    title = request.form['title']
    description = request.form['post']
    label = request.form['label']

    # Will take the list of ingredients and parse them using commas
    ingredients = request.form['ingredients']
    #ingredientList = ingredients.split(",")
    user_id = current_user.id
    #Get the image in request
    if 'file' not in request.files:
        print('No file part')
    file = request.files['file']
    if file.filename == '':
        print('No selected file')
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #specific way in order for images to load in our static folder
    shownPath = 'Images/'+filename
    if file:
        file.save(file_path)
        print('File uploaded successfully')
    #upload all the relevant info in the post db
    #1 is the user_id, we don't have a login system 
    add_post(user_id, title, description, label, shownPath, ingredients)
    print("post uploaded successfully!")
    return render_template('post.html')

@app.route('/submitComment', methods=['POST'])
@login_required
def submitComment():
    comment = request.form['comment']
    user_id = current_user.id

    #We can grab the currentPostID using request.args.get
    #using action="/submitComment?post_id={{post.id}}" this lets us grab the value for /submit
    post_id = request.args.get('post_id')
    add_comment(user_id, post_id, comment)
    return redirect(url_for('viewPost', post_id=post_id))


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

def add_comment(user_id, post_id, comment):
    post = Post.query.get(post_id)
    user = User.query.get(user_id)
    if user and post:
        new_comment = Comments(user_id = user_id, post_id = post_id, comment = comment)
        db.session.add(new_comment)
        db.session.commit()
        return True
    else:
        return False

def add_post(user_id, title, description, label, picture, ingredients):
    user = User.query.get(user_id)
    if user:
        new_post = Post(user_id=user_id, title=title, description=description, label=label, picture = picture, ingredients=ingredients)
        db.session.add(new_post)
        db.session.commit()
        return True
    else:
        return False   

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
