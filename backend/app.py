from flask import Flask, request, jsonify
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post
from backend.db import SessionLocal
from backend.models import UserModel
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

GOOGLE_ID = "437960362432-34e8ipa7a4ivuvu1jsq32u6qu6j51uf7.apps.googleusercontent.com"

# Simple CORS headers
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    # Allow credentials: must echo exact origin, not '*'
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response



def _serialize_user(user: User):
    return {
        'id': user.db_id,
        'username': user.username,
        'email': user.email,
        'major': user.major,
        'year': user.year,
        'first_name': getattr(user, 'first_name', ''),
        'last_name': getattr(user, 'last_name', ''),
        'is_deleted': user.is_deleted,
        'is_admin': getattr(user, 'is_admin', False),
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
        'created_at': (getattr(forum, 'created_at', None).isoformat() + 'Z') if getattr(forum, 'created_at', None) else None,
        'posts': [
            _serialize_post(post)
            for post in forum.getPosts()
        ],
        'users': [
            {
                'id': user.db_id,
                'username': user.username,
                'email': user.email,
                'is_admin': getattr(user, 'is_admin', False)
            }
            for user in forum.getUsers()
        ],
        'authorized_users': [
            {
                'id': user.db_id,
                'username': user.username,
                'email': user.email
            }
            for user in getattr(forum, 'authorized', [])
        ],
        'restricted_users': [
            {
                'id': user.db_id,
                'username': user.username,
                'email': user.email
            }
            for user in getattr(forum, 'restricted', [])
        ]
    }



def _serialize_post(post: Post):
    return {
        'id': post.db_id,
        'forum_id': getattr(post, 'forum_id', None),
        'forum_name': getattr(post, 'forum_name', None),
        'title': post.title,
        'message': post.message,
        'poster': post.poster.username if post.poster else None,
        'is_deleted': post.is_deleted,
        'created_at': (getattr(post, 'created_at', None).isoformat() + 'Z') if getattr(post, 'created_at', None) else None,
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



@app.route('/api/googlelogin', methods=['POST', 'OPTIONS'])
def googlelogin():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    token = data.get('credential')
    print(token)
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_ID
        )

        email = id_info.get("email")
        name = id_info.get("name")
        google_user_id = id_info.get("sub")

        if not email or not isinstance(email, str) or not email.endswith('@scu.edu'):
            return jsonify({'error': 'A valid scu.edu email is required'}), 400
        
        user = User.load_by_email(email)
        if user is not None:
            return jsonify(_serialize_user(user)), 200
        else:
            return jsonify({'error': 'User not found', 'email': email}), 404
    except ValueError:
        return jsonify({'error': 'Invalid Google token'}), 401


    
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
    first_name = data.get('first_name')
    last_name = data.get('last_name')

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
        kwargs = {}
        if isinstance(first_name, str):
            kwargs['first_name'] = first_name
        if isinstance(last_name, str):
            kwargs['last_name'] = last_name
        new_user = User(username, email, major, year, None, None, None, **kwargs)
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



@app.route('/api/users/<int:user_id>/forums', methods=['POST', 'OPTIONS'])
def user_add_forum(user_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    forum_id = data.get('forum_id')

    user = User.load_by_id(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    try:
        user.addForum(forum)
        forum.addUser(user)
        return jsonify({'message': 'User added to forum successfully'}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/users_name/<string:username>', methods=['GET', 'OPTIONS'])
def get_user_profile_by_name(username):
    if request.method == 'OPTIONS':
        return ('', 204)

    user = User.load_by_username(username)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(_serialize_user(user)), 200



@app.route('/api/profile/update', methods=['POST', 'OPTIONS'])
def update_user_profile():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    user = User.load_by_id(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    try:
        dirty = False
        if 'username' in data and isinstance(data['username'], str):
            user.username = data['username']
            dirty = True
        if 'major' in data and isinstance(data['major'], str):
            user.major = data['major']
            dirty = True
        if 'year' in data:
            year = data['year']
            if isinstance(year, str) and year.isdigit():
                year = int(year)
            if isinstance(year, int):
                user.year = year
                dirty = True
        if 'first_name' in data and isinstance(data['first_name'], str):
            user.first_name = data['first_name']
            dirty = True
        if 'last_name' in data and isinstance(data['last_name'], str):
            user.last_name = data['last_name']
            dirty = True

        if dirty:
            session = SessionLocal()
            try:
                model = session.get(UserModel, user.db_id)
                if model:
                    model.username = user.username
                    model.major = user.major
                    model.year = user.year
                    model.first_name = user.first_name
                    model.last_name = user.last_name
                    session.add(model)
                    session.commit()
            finally:
                session.close()

        return jsonify(_serialize_user(user)), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/forums/<int:forum_id>', methods=['GET', 'OPTIONS'])
def get_forum_profile(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    return jsonify(_serialize_forum(forum)), 200



def _require_admin(admin_email: str):
    if not admin_email:
        return None, jsonify({'error': 'admin_email is required'}), 400
    admin_user = User.load_by_email(admin_email)
    if admin_user is None:
        return None, jsonify({'error': 'Admin user not found'}), 404
    if not getattr(admin_user, 'is_admin', False):
        return None, jsonify({'error': 'User is not an admin'}), 403
    return admin_user, None, None



def _require_admin_or_authorized(actor_email: str, forum: Forum):
    if not actor_email:
        return None, jsonify({'error': 'actor_email is required'}), 400
    actor = User.load_by_email(actor_email)
    if actor is None:
        return None, jsonify({'error': 'Actor user not found'}), 404
    if getattr(actor, 'is_admin', False):
        return actor, None, None
    # Check authorized status in forum (ensure freshest data)
    forum_users = forum.getUsers()
    authorized_ids = [u.db_id for u in getattr(forum, 'authorized', [])]
    if actor.db_id in authorized_ids:
        return actor, None, None
    return None, jsonify({'error': 'User lacks permission (admin or authorized required)'}), 403



@app.route('/api/forums/<int:forum_id>/authorize_user', methods=['POST', 'OPTIONS'])
def authorize_user(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    target_email = data.get('target_email')
    admin_email = data.get('admin_email')
    admin_user, err_resp, status = _require_admin(admin_email)
    if err_resp:
        return err_resp, status
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    target_user = User.load_by_email(target_email)
    if target_user is None:
        return jsonify({'error': 'Target user not found'}), 404
    try:
        forum.authorizeUser(target_user)
        return jsonify({'message': 'User authorized', 'forum': _serialize_forum(forum)}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/forums/<int:forum_id>/deauthorize_user', methods=['POST', 'OPTIONS'])
def deauthorize_user(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    target_email = data.get('target_email')
    admin_email = data.get('admin_email')
    admin_user, err_resp, status = _require_admin(admin_email)
    if err_resp:
        return err_resp, status
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    target_user = User.load_by_email(target_email)
    if target_user is None:
        return jsonify({'error': 'Target user not found'}), 404
    try:
        forum.deauthorizeUser(target_user)
        return jsonify({'message': 'User deauthorized', 'forum': _serialize_forum(forum)}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/forums/<int:forum_id>/restrict_user', methods=['POST', 'OPTIONS'])
def restrict_user(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    target_email = data.get('target_email')
    # Support either admin or authorized user (actor_email preferred, fallback to admin_email)
    actor_email = data.get('actor_email') or data.get('admin_email')
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    target_user = User.load_by_email(target_email)
    if target_user is None:
        return jsonify({'error': 'Target user not found'}), 404
    actor, err_resp, status = _require_admin_or_authorized(actor_email, forum)
    if err_resp:
        return err_resp, status
    try:
        forum.restrictUser(target_user)
        return jsonify({'message': 'User restricted', 'forum': _serialize_forum(forum)}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/forums/<int:forum_id>/unrestrict_user', methods=['POST', 'OPTIONS'])
def unrestrict_user(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    target_email = data.get('target_email')
    actor_email = data.get('actor_email') or data.get('admin_email')
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    target_user = User.load_by_email(target_email)
    if target_user is None:
        return jsonify({'error': 'Target user not found'}), 404
    actor, err_resp, status = _require_admin_or_authorized(actor_email, forum)
    if err_resp:
        return err_resp, status
    try:
        forum.unrestrictUser(target_user)
        return jsonify({'message': 'User unrestricted', 'forum': _serialize_forum(forum)}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/forums/<int:forum_id>/leave', methods=['POST', 'OPTIONS'])
def leave_forum(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    user_email = data.get('user_email')
    
    if not user_email:
        return jsonify({'error': 'user_email is required'}), 400
    
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    
    user = User.load_by_email(user_email)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        forum.removeUser(user)
        user.removeForum(forum)
        return jsonify({'message': 'Successfully left forum'}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/forums/<int:forum_id>/delete', methods=['POST', 'OPTIONS'])
def delete_forum(forum_id):
    """Admin-only: Permanently delete a forum, remove all posts/comments/reactions, and detach all users."""
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    admin_email = data.get('admin_email') or data.get('actor_email')

    # Require admin
    admin_user, err_resp, status = _require_admin(admin_email)
    if err_resp:
        return err_resp, status

    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404

    # Perform cascading deletion using direct DB operations
    try:
        from .db import SessionLocal
        from .models import ForumModel, PostModel, ReactionModel, forum_users, forum_authorized, forum_restricted
    except Exception:
        from backend.db import SessionLocal
        from backend.models import ForumModel, PostModel, ReactionModel, forum_users, forum_authorized, forum_restricted

    session = SessionLocal()
    try:
        forum_model = session.get(ForumModel, forum_id)
        if forum_model is None:
            return jsonify({'error': 'Forum not found'}), 404

        # Collect all post ids belonging to the forum (top-level posts)
        top_posts = session.query(PostModel).filter(PostModel.forum_id == forum_model.id).all()
        to_delete_ids = set(p.id for p in top_posts)

        # Iteratively collect all descendant comment ids
        # We traverse by repeatedly finding posts whose parent_id is in to_delete_ids
        changed = True
        while changed:
            changed = False
            child_posts = session.query(PostModel).filter(PostModel.parent_id.in_(to_delete_ids)).all() if to_delete_ids else []
            new_ids = [cp.id for cp in child_posts if cp.id not in to_delete_ids]
            if new_ids:
                to_delete_ids.update(new_ids)
                changed = True

        # Delete reactions tied to any of these posts/comments
        if to_delete_ids:
            session.query(ReactionModel).filter(ReactionModel.parent_id.in_(to_delete_ids)).delete(synchronize_session=False)

        # Delete posts/comments themselves
        if to_delete_ids:
            session.query(PostModel).filter(PostModel.id.in_(to_delete_ids)).delete(synchronize_session=False)

        # Detach all user associations (members, authorized, restricted)
        session.execute(forum_users.delete().where(forum_users.c.forum_id == forum_model.id))
        session.execute(forum_authorized.delete().where(forum_authorized.c.forum_id == forum_model.id))
        session.execute(forum_restricted.delete().where(forum_restricted.c.forum_id == forum_model.id))

        # Finally delete the forum itself
        session.delete(forum_model)
        session.commit()

        return jsonify({'message': 'Forum deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()



@app.route('/api/posts/<int:post_id>/delete', methods=['POST', 'OPTIONS'])
def delete_post(post_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    actor_email = data.get('actor_email') or data.get('admin_email')
    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Get the actor user
    actor_user = User.load_by_email(actor_email)
    if actor_user is None:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is the post owner
    post_owner = post.getposter()
    is_owner = post_owner and getattr(post_owner, 'db_id', None) == getattr(actor_user, 'db_id', None)
    
    # If not the owner, check admin/authorized permissions
    if not is_owner:
        # Load forum to check authorization if not admin
        try:
            from backend.Forum import Forum as ForumClass
            forum_id = getattr(post, 'forum_id', None)
            forum = ForumClass.load_by_id(forum_id) if forum_id else None
        except Exception:
            forum = None
        if forum is None and not getattr(actor_user, 'is_admin', False):
            return jsonify({'error': 'Forum context required for authorized user'}), 400
        actor, err_resp, status = _require_admin_or_authorized(actor_email, forum) if forum else _require_admin(actor_email)
        if err_resp:
            return err_resp, status
    
    # Soft delete: set is_deleted flag
    post.is_deleted = True
    try:
        from .db import SessionLocal
        from .models import PostModel
    except Exception:
        from backend.db import SessionLocal
        from backend.models import PostModel
    session = SessionLocal()
    post_model = session.get(PostModel, getattr(post, 'db_id', None))
    if post_model is not None:
        post_model.is_deleted = True
        session.add(post_model)
        session.commit()
    session.close()
    return jsonify({'message': 'Post deleted', 'post': _serialize_post(post)}), 200



@app.route('/api/comments/<int:comment_id>/delete', methods=['POST', 'OPTIONS'])
def delete_comment(comment_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or {}
    actor_email = data.get('actor_email') or data.get('admin_email')
    
    # Load comment (which is a Post/Comment object)
    from backend.Messages import Comment as CommentClass
    comment = CommentClass.load_by_id(comment_id)
    if comment is None:
        return jsonify({'error': 'Comment not found'}), 404
    
    # Get the actor user
    actor_user = User.load_by_email(actor_email)
    if actor_user is None:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is the comment owner
    comment_owner = comment.getposter()
    is_owner = comment_owner and getattr(comment_owner, 'db_id', None) == getattr(actor_user, 'db_id', None)
    
    # If not the owner, check admin/authorized permissions
    if not is_owner:
        # Load forum to check authorization if not admin
        try:
            from backend.Forum import Forum as ForumClass
            forum_id = getattr(comment, 'forum_id', None)
            forum = ForumClass.load_by_id(forum_id) if forum_id else None
        except Exception:
            forum = None
        
        if forum is None and not getattr(actor_user, 'is_admin', False):
            return jsonify({'error': 'Forum context required for authorized user'}), 400
        
        actor, err_resp, status = _require_admin_or_authorized(actor_email, forum) if forum else _require_admin(actor_email)
        if err_resp:
            return err_resp, status
    
    # Soft delete: set is_deleted flag and replace message
    comment.is_deleted = True
    comment.message = '[deleted]'
    comment.title = '[deleted]'
    
    try:
        from .db import SessionLocal
        from .models import PostModel
    except Exception:
        from backend.db import SessionLocal
        from backend.models import PostModel
    
    session = SessionLocal()
    comment_model = session.get(PostModel, getattr(comment, 'db_id', None))
    if comment_model is not None:
        comment_model.is_deleted = True
        comment_model.message = '[deleted]'
        comment_model.title = '[deleted]'
        session.add(comment_model)
        session.commit()
    session.close()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200



@app.route('/api/forums/<int:forum_id>/user_status', methods=['GET','OPTIONS'])
def forum_user_status(forum_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    # Accept user_email from query string or JSON body fallback
    user_email = request.args.get('user_email')
    if not user_email:
        data = request.get_json(silent=True) or {}
        user_email = data.get('user_email')
    if not user_email or not isinstance(user_email, str):
        return jsonify({'error': 'user_email is required'}), 400
    forum = Forum.load_by_id(forum_id)
    if forum is None:
        return jsonify({'error': 'Forum not found'}), 404
    user = User.load_by_email(user_email)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    # Ensure latest membership lists
    members = forum.getUsers()
    member_ids = [m.db_id for m in members]
    is_member = user.db_id in member_ids
    authorized_ids = [u.db_id for u in getattr(forum, 'authorized', [])]
    restricted_ids = [u.db_id for u in getattr(forum, 'restricted', [])]
    is_authorized = is_member and user.db_id in authorized_ids
    is_restricted = is_member and user.db_id in restricted_ids
    return jsonify({
        'forum_id': forum.db_id,
        'user_id': user.db_id,
        'user_email': user.email,
        'is_member': is_member,
        'is_authorized': is_authorized,
        'is_restricted': is_restricted
    }), 200



@app.route('/api/posts/<int:post_id>', methods=['GET', 'OPTIONS'])
def get_post_profile(post_id, user_id=None, forum_id=None):
    if request.method == 'OPTIONS':
        return ('', 204)

    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    if user_id is not None and (getattr(post, 'user_id', None) != user_id):
        return jsonify({'error': 'Post does not belong to the specified user'}), 404
    if forum_id is not None and (getattr(post, 'forum_id', None) != forum_id):
        return jsonify({'error': 'Post does not belong to the specified forum'}), 404
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
        
        # Determine the parent
        if parent_comment_id is not None:
            try:
                pid = int(parent_comment_id)
            except (TypeError, ValueError):
                return jsonify({'error': 'Invalid parent_comment_id'}), 400
            parent = Post.load_by_id(pid)
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
    
@app.route('/api/posts/react/<int:post_id>/<int:reaction_id>/<int:user_id>', methods=['GET', 'OPTIONS'])
def add_reaction(post_id, reaction_id, user_id):
    if request.method == 'OPTIONS':
        return ('', 204)

    post = Post.load_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    user = User.load_by_db_id(user_id)
    if user is None:
        return jsonify({'error': 'Invalid commenting user'}), 404
    
    try:
        from backend.Messages import Reaction
        reaction_name = ""
        if reaction_id == 1:
            reaction_name = "like"
        elif reaction_id == 2:
            reaction_name = "dislike"
        elif reaction_id == 3:
            reaction_name = "heart"
        elif reaction_id == 4:
            reaction_name = "flag"
        else:
            raise ValueError()
        
        new_reaction = Reaction(reaction_name, user)
        added = post.addreaction(new_reaction)

        if added:
            return jsonify({'message': 'Reaction added successfully', 'added': True}), 201
        else:
            return jsonify({'message': 'Reaction removed successfully', 'added': False}), 200
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400
    
    

if __name__ == '__main__':
    app.run(debug=True)
