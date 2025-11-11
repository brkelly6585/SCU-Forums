from flask import Flask, request, jsonify
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post

app = Flask(__name__)

# Simple CORS headers for local React dev (adjust origin as needed)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

def _serialize_user(user: User):
    return {
        'id': user.db_id,
        'username': user.username,
        'email': user.email,
        'major': user.major,
        'year': user.year,
        'is_deleted': user.is_deleted,
        'forums': [
            _serialize_forum(forum)
            for forum in user.getforums()
        ],
        'posts': [
            _serialize_post(post)
            for post in user.getposts()
        ]
    }

def _serialize_forum(forum: Forum):
    return {
        'id': forum.db_id,
        'course_name': forum.course_name,
        'posts': [
            _serialize_post(post)
            for post in forum.getPosts()
        ],
        'users': [
            {
                'id': user.db_id,
                'username': user.username,
                'email': user.email
            }
            for user in forum.getUsers()
        ]
    }

def _serialize_post(post: Post):
    return {
        'id': post.db_id,
        'forum_id': getattr(post, 'forum_id', None),
        'title': post.title,
        'message': post.message,
        'poster': post.poster.username if post.poster else None,
        'is_deleted': post.is_deleted,
        'reactions': [
            {
                'id': reaction.db_id,
                'reaction_type': reaction.reaction_type,
                'user': reaction.user.username if reaction.user else None
            }
            for reaction in post.getReactions()
        ],
        'comments': [_serialize_post(comment) for comment in post.getComments()]
    }

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return ('', 204)

    # Necessary data from Frontend
    data = request.get_json(silent=True) or {}
    email = data.get('email')

    if not email or not isinstance(email, str) or not email.endswith('@scu.edu'):
        return jsonify({'error': 'A valid scu.edu email is required'}), 400

    # Existing user by email -> return profile
    user = User.load_by_email(email)
    if user is not None:
        return jsonify(_serialize_user(user)), 200
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/api/create_user', methods=['POST', 'OPTIONS'])
def create_user():
    if request.method == 'OPTIONS':
        return ('', 204)

    # Necessary data from Frontend
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    username = data.get('username')
    major = data.get('major')
    year = data.get('year')

    if not email or not isinstance(email, str) or not email.endswith('@scu.edu'):
        return jsonify({'error': 'A valid scu.edu email is required'}), 400

    # Check for existing user
    existing_user = User.load_by_email(email)
    if existing_user is not None:
        return jsonify({'error': 'User already exists'}), 400

    # Validate and create new user
    missing = []
    if not username:
        missing.append('username')
    if not major:
        missing.append('major')
    if year is None:
        missing.append('year')
    if missing:
        return jsonify({'error': f"Missing required fields for new user: {', '.join(missing)}"}), 400

    # Attempt to create a new user
    try:
        # Year may come as string from frontend; coerce if needed
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        new_user = User(username, email, major, year, None, None, None)
        return jsonify(_serialize_user(new_user)), 201
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/create_forum', methods=['POST', 'OPTIONS'])
def create_forum():
    if request.method == 'OPTIONS':
        return ('', 204)

    # Necessary data from Frontend
    data = request.get_json(silent=True) or {}
    course_name = data.get('course_name')
    creator_email = data.get('creator_email')

    if not course_name or not isinstance(course_name, str):
        return jsonify({'error': 'A valid course name is required'}), 400

    # Check for existing forum
    existing_forum = Forum.load_by_course_name(course_name)
    if existing_forum is not None:
        return jsonify({'error': 'Forum already exists'}), 400

    # Attempt to create a new forum
    try:
        creator = User.load_by_email(creator_email)
        if creator is None:
            return jsonify({'error': 'Creator not found'}), 404

        new_forum = Forum(course_name, creator)
        return jsonify({'message': 'Forum created successfully', 'forum': _serialize_forum(new_forum)}), 201
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/forums', methods=['GET', 'OPTIONS'])
def list_forums():
    if request.method == 'OPTIONS':
        return ('', 204)

    forums = Forum.load_all_forums()
    serialized_forums = [_serialize_forum(forum) for forum in forums]
    return jsonify({'forums': serialized_forums}), 200
    
@app.route('/api/users/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user_profile(user_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    user = User.load_by_id(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(_serialize_user(user)), 200

@app.route('/api/forums/<int:forum_id>', methods=['GET', 'OPTIONS'])
def get_forum_profile(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    return jsonify(_serialize_forum(forum)), 200

@app.route('/api/posts/<int:post_id>', methods=['GET', 'OPTIONS'])
def get_post_profile(post_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    return jsonify(_serialize_post(post)), 200
    
@app.route('/api/forums/<int:forum_id>/posts', methods=['POST', 'OPTIONS'])
def get_forum_posts(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    posts = forum.getPosts()
    serialized_posts = [_serialize_post(post) for post in posts]
    return jsonify({'posts': serialized_posts}), 200

@app.route('/api/posts/<int:post_id>/comments', methods=['POST', 'OPTIONS'])
def get_post_comments(post_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    comments = post.getComments()
    serialized_comments = [_serialize_post(comment) for comment in comments]
    return jsonify({'comments': serialized_comments}), 200

if __name__ == '__main__':
    app.run(debug=True)
