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
            {
                'id': forum.db_id,
                'course_name': forum.course_name,
                'posts': [
                    {
                        'id': post.db_id,
                        'title': post.title,
                        'message': post.message,
                        'poster': post.poster.username if post.poster else None,
                        'is_deleted': post.is_deleted
                    }
                    for post in forum.getPosts()
                ]
            }
            for forum in user.getforums()
        ],
        'posts': [
            {
                'id': post.db_id,
                'title': post.title,
                'message': post.message,
                'forum_id': getattr(post, 'forum_id', None),
                'is_deleted': post.is_deleted
            }
            for post in user.getposts()
        ]
    }

@app.route('/api/login', methods=['POST', 'OPTIONS'])
@app.route('/login', methods=['POST', 'OPTIONS'])  # backward-compatible path
def login():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    email = data.get('email')
    username = data.get('username')
    major = data.get('major')
    year = data.get('year')

    if not email or not isinstance(email, str) or not email.endswith('@scu.edu'):
        return jsonify({'error': 'A valid scu.edu email is required'}), 400

    # Existing user by email -> return profile
    user = User.load_by_email(email)
    if user is not None:
        return jsonify(_serialize_user(user))

    # New user path requires username, major, year
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

if __name__ == '__main__':
    app.run(debug=True)
