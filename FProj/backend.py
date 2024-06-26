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
UPLOAD_FOLDER = 'FProj/static/Images/'
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

class PostReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reaction = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    ingredients = db.Column(db.String, nullable = False)
    label = db.Column(db.String(), nullable = False)
    picture = db.Column(db.String(), nullable = False)
    upvote = db.Column(db.Integer, default = 0, nullable = False)
    downvote = db.Column(db.Integer, default = 0, nullable = False)
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
    profile_picture = db.Column(db.String(255))


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

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    posts = current_user.posts
    num_posts = len(posts)

    #Get the image in request
    if 'file' not in request.files:
        print('No file part')
    file = request.files['file']
    if file.filename == '':
        print('No selected file')
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #specific way in order for images to load in our static folder
    shownPath = 'Images/'+filename
    if file:
        file.save(file_path)
        print('File uploaded successfully')
    current_user.profile_picture = shownPath
    db.session.commit()
    return render_template("account.html", posts=posts, num_posts=num_posts)


@app.route('/users')
def display_users():
    # Query all users from the database
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/main')
def mainPage():
    if current_user.is_authenticated:
        users = User.query.all()
        posts = Post.query.all()
        popularPosts = Post.query.order_by(Post.upvote.desc()).all()

        topPosts = popularPosts[:3]
        return render_template('main.html', posts=posts,popularPosts = topPosts, users=users)
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

@app.route('/dislike/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    # Find the post by its ID
    post = Post.query.get(post_id)
    if post:
        # Increment the upvote count for the post
        post.downvote -= 1
        # Commit the changes to the database
        db.session.commit()
        # Return a JSON response indicating success
        return jsonify({'success': True, 'message': 'Post upvoted successfully'})
    else:
        # If post with the given ID doesn't exist, return a JSON response with error message
        return jsonify({'success': False, 'message': 'Post not found'}), 404


#Search Bar for Images
@app.route('/search')
def searchPage():
    users = User.query.all()
    posts = Post.query.all()
    return render_template('search.html', posts=posts, users=users)

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
    filename = file.filename
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(file_path)
    #specific way in order for images to load in our static folder
    shownPath = 'Images/'+filename
    if file:
        file.save(file_path)
        print('File uploaded successfully')
    #upload all the relevant info in the post db
    #1 is the user_id, we don't have a login system
    add_post(user_id, title, description, label, shownPath, ingredients)
    print("post uploaded successfully!")

    return redirect(url_for('mainPage'))

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

@app.route('/search/<tag>')
def filter_posts(tag):
    filtered_posts = Post.query.filter(Post.label.contains(tag)).all()
    users = User.query.all()
    posts = Post.query.all()
    #Render template with filtered posts
    return render_template('search.html', posts = posts ,filtered_posts = filtered_posts, users=users)

@app.route('/react/<int:post_id>', methods=['POST'])
@login_required
def react_to_post(post_id):
    reaction_type = request.form['reaction']  # Assuming the form contains a field named 'reaction'

    # Find the post by its ID
    post = Post.query.get(post_id)
    if post:
        # Check if the user has already reacted to the post
        post_reaction = PostReaction.query.filter_by(post_id=post_id, user_id=current_user.id).first()

        if post_reaction:
            # If the user has already reacted to the post, update the reaction count
            if reaction_type == 'like':
                if post_reaction.reaction == 'like':
                    # If the user already liked the post, remove the like
                    post.upvote -= 1
                    post_reaction.reaction = None
                else:
                    # If the user disliked the post, change dislike to like
                    post.downvote -= 1
                    post.upvote += 1
                    post_reaction.reaction = 'like'
            else:  # Assuming reaction_type is 'dislike'
                if post_reaction.reaction == 'dislike':
                    # If the user already disliked the post, remove the dislike
                    post.downvote -= 1
                    post_reaction.reaction = None
                else:
                    # If the user liked the post, change like to dislike
                    post.upvote -= 1
                    post.downvote += 1
                    post_reaction.reaction = 'dislike'
        else:
            # If the user hasn't reacted to the post, create a new reaction
            new_reaction = PostReaction(post_id=post_id, user_id=current_user.id, reaction=reaction_type)
            db.session.add(new_reaction)
            if reaction_type == 'like':
                post.upvote += 1
            else:
                post.downvote += 1

        # Commit the changes to the database
        db.session.commit()
        # Return a JSON response indicating success
        return jsonify({'success': True, 'message': 'Post reacted successfully'})
    else:
        # If post with the given ID doesn't exist, return a JSON response with error message
        return jsonify({'success': False, 'message': 'Post not found'}), 404


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