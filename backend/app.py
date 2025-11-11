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
            for reaction in post.getreactions()
        ],
        'comments': [_serialize_post(comment) for comment in post.getcomments()]
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
        new_forum = Forum(course_name)
        
        # If creator_email is provided, add them as a member
        if creator_email:
            creator = User.load_by_email(creator_email)
            if creator:
                creator.addForum(new_forum)
                new_forum.addUser(creator)
        
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
    
@app.route('/api/forums/<int:forum_id>/posts', methods=['GET', 'POST', 'OPTIONS'])
def forum_posts(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    if request.method == 'GET':
        posts = forum.getPosts()
        serialized_posts = [_serialize_post(post) for post in posts]
        return jsonify({'posts': serialized_posts}), 200
    
    # POST - Create new post
    data = request.get_json(silent=True) or {}
    title = data.get('title')
    message = data.get('message')
    user_email = data.get('user_email')

    # Debug logging
    print(f"[DEBUG] POST request data: {data}")
    print(f"[DEBUG] title={title}, message={message}, user_email={user_email}")

    if not title or not isinstance(title, str):
        print(f"[DEBUG] Title validation failed: title={title}, type={type(title)}")
        return jsonify({'error': 'A valid title is required'}), 400
    if not message or not isinstance(message, str):
        print(f"[DEBUG] Message validation failed: message={message}, type={type(message)}")
        return jsonify({'error': 'A valid message is required'}), 400
    if not user_email or not isinstance(user_email, str):
        print(f"[DEBUG] Email validation failed: user_email={user_email}, type={type(user_email)}")
        return jsonify({'error': 'User email is required'}), 400

    user = User.load_by_email(user_email)
    if user is None:
        print(f"[DEBUG] User not found: {user_email}")
        return jsonify({'error': 'User not found'}), 404

    # Check if user is member of forum (compare by db_id, not object identity)
    user_forums = user.getforums()
    user_forum_ids = [f.db_id for f in user_forums]
    print(f"[DEBUG] User {user.username} forums: {user_forum_ids}, checking forum {forum.db_id}")
    if forum.db_id not in user_forum_ids:
        print(f"[DEBUG] Membership check failed")
        return jsonify({'error': 'User is not a member of this forum'}), 403

    try:
        new_post = Post(poster=user, message=message, title=title)
        user.addPost(forum, new_post)
        print(f"[DEBUG] Post created successfully: {new_post.title}")
        return jsonify({'message': 'Post created successfully', 'post': _serialize_post(new_post)}), 201
    except (ValueError, TypeError) as e:
        print(f"[DEBUG] Exception creating post: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/api/posts/<int:post_id>/comments', methods=['GET', 'POST', 'OPTIONS'])
def post_comments(post_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    if request.method == 'GET':
        comments = post.getcomments()
        serialized_comments = [_serialize_post(comment) for comment in comments]
        return jsonify({'comments': serialized_comments}), 200
    
    # POST - Create new comment
    data = request.get_json(silent=True) or {}
    message = data.get('message')
    user_email = data.get('user_email')
    parent_comment_id = data.get('parent_comment_id')  # Optional for nested comments

    if not message or not isinstance(message, str):
        return jsonify({'error': 'A valid message is required'}), 400
    if not user_email or not isinstance(user_email, str):
        return jsonify({'error': 'User email is required'}), 400

    user = User.load_by_email(user_email)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    try:
        from backend.Messages import Comment
        
        # Determine the parent (either the post or another comment)
        if parent_comment_id:
            parent = Post.load_by_id(parent_comment_id)
            if parent is None:
                return jsonify({'error': 'Parent comment not found'}), 404
        else:
            # Top-level comment - parent is the post
            parent = post
        
        # Create the comment with the parent
        new_comment = Comment(poster=user, message=message, title="Comment", parent=parent)
        
        return jsonify({'message': 'Comment created successfully', 'comment': _serialize_post(new_comment)}), 201
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
