from typing import TYPE_CHECKING, List, Optional
from .db import SessionLocal
from .models import ForumModel, UserModel, PostModel
from .object_registry import register, get as registry_get

if TYPE_CHECKING:
    from backend.User import User
    from backend.Forum import Forum
    from backend.Messages import Post




# Support class for Forum to handle DB
class ForumRepository:
    
    @staticmethod
    def load_by_course_name(course_name: str) -> Optional['Forum']:
        # Load Forum from DB by name
        from backend.Forum import Forum
        session = SessionLocal()
        try:
            forum_model = session.query(ForumModel).filter(ForumModel.course_name == course_name).first()
            if forum_model is None:
                return None
            return Forum.from_model(forum_model, session=session)
        finally:
            session.close()
    
    @staticmethod
    def load_by_id(course_id: int) -> Optional['Forum']:
        # Load Forum from DB by ID
        from backend.Forum import Forum
        session = SessionLocal()
        try:
            forum_model = session.query(ForumModel).filter(ForumModel.id == course_id).first()
            if forum_model is None:
                return None
            return Forum.from_model(forum_model, session=session)
        finally:
            session.close()
    
    @staticmethod
    def load_all() -> List['Forum']:
        # Load all Forum wrappers from the DB
        from backend.Forum import Forum
        session = SessionLocal()
        try:
            forum_models = session.query(ForumModel).all()
            forums = []
            for forum_model in forum_models:
                forums.append(Forum.from_model(forum_model, session=session))
            return forums
        finally:
            session.close()
    
    @staticmethod
    def save(forum: 'Forum') -> None:
        # update the DB with forum info
        session = SessionLocal()
        try:
            forum_model = session.get(ForumModel, forum.db_id)
            if forum_model is not None:
                forum_model.course_name = forum.course_name
                session.add(forum_model)
                session.commit()
        finally:
            session.close()
    
    @staticmethod
    def create(course_name: str) -> 'ForumModel':
        # Create a new forum in the database
        session = SessionLocal()
        try:
            forum_model = ForumModel(course_name=course_name)
            session.add(forum_model)
            session.commit()
            session.refresh(forum_model)
            return forum_model
        finally:
            session.close()
    
    @staticmethod
    def find_by_course_name(course_name: str) -> Optional['ForumModel']:
        # Find a forum model by course name
        session = SessionLocal()
        try:
            return session.query(ForumModel).filter(ForumModel.course_name == course_name).first()
        finally:
            session.close()






# Support class for managing User and Forum relations
class ForumMembershipService:
    
    # Class-level deleted user instance for maintaining post history
    DELETED_USER = None
    
    @staticmethod
    def add_user(forum: 'Forum', user: 'User') -> None:
        # Adds a user to forum
        from backend.User import User
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in forum.users:
            forum.users.append(user)
            # persist association
            session = SessionLocal()
            try:
                forum_model = session.get(ForumModel, forum.db_id)
                user_model = session.get(UserModel, getattr(user, 'db_id', None))
                if user_model is None:
                    return
                if user_model not in forum_model.users:
                    forum_model.users.append(user_model)
                    session.add(forum_model)
                    session.commit()
            finally:
                session.close()
            # ensure user's forum list also reflects membership
            try:
                if getattr(user, 'forum', None) is not None and forum not in user.forum:
                    user.forum.append(forum)
            except Exception:
                pass
    
    @staticmethod
    def remove_user(forum: 'Forum', user: 'User') -> None:
        # Removes a user and updates relations
        if user not in forum.users:
            return
            
        # Update all posts by this user to use the deleted user
        for post in forum.posts:
            if post.poster == user:
                post.poster = ForumMembershipService.DELETED_USER
                # update DB poster id for that post
                session = SessionLocal()
                try:
                    post_model = session.get(PostModel, getattr(post, 'db_id', None))
                    if post_model is not None:
                        post_model.poster_id = getattr(ForumMembershipService.DELETED_USER, 'db_id', None)
                        session.add(post_model)
                        session.commit()
                finally:
                    session.close()
        
        # Remove user from users list
        forum.users.remove(user)
        
        # Clean up authorization lists
        if user in forum.authorized:
            ForumMembershipService.deauthorize_user(forum, user)
        if user in forum.restricted:
            ForumMembershipService.unrestrict_user(forum, user)
        
        # remove association in DB
        session = SessionLocal()
        try:
            forum_model = session.get(ForumModel, forum.db_id)
            user_model = session.get(UserModel, getattr(user, 'db_id', None))
            if user_model in forum_model.users:
                forum_model.users.remove(user_model)
                session.add(forum_model)
                session.commit()
        finally:
            session.close()
        
        # remove forum from user's in-memory forum list if present
        try:
            if getattr(user, 'forum', None) is not None and forum in user.forum:
                user.forum.remove(forum)
        except Exception:
            pass
    
    @staticmethod
    def authorize_user(forum: 'Forum', user: 'User') -> None:
        # Grant user authorization privileges
        from backend.User import User
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in forum.users:
            raise ValueError("User is not a member of this forum")
        if user not in forum.authorized:
            # update db relationships
            session = SessionLocal()
            try:
                forum_model = session.get(ForumModel, forum.db_id)
                user_model = session.get(UserModel, getattr(user, 'db_id', None))
                if forum_model is not None and user_model is not None and user_model not in getattr(forum_model, 'authorized_users', []):
                    forum_model.authorized_users.append(user_model)
                    session.add(forum_model)
                    session.commit()
            finally:
                session.close()
            forum.authorized.append(user)
            if user in forum.restricted:
                ForumMembershipService.unrestrict_user(forum, user)
    
    @staticmethod
    def deauthorize_user(forum: 'Forum', user: 'User') -> None:
        # Remove user auth privelege
        if user not in forum.authorized:
            return
        # update db relationships
        session = SessionLocal()
        try:
            forum_model = session.get(ForumModel, forum.db_id)
            user_model = session.get(UserModel, getattr(user, 'db_id', None))
            if forum_model is not None and user_model is not None and user_model in getattr(forum_model, 'authorized_users', []):
                forum_model.authorized_users.remove(user_model)
                session.add(forum_model)
                session.commit()
        finally:
            session.close()
        forum.authorized.remove(user)
    
    @staticmethod
    def restrict_user(forum: 'Forum', user: 'User') -> None:
        # Restrict user in forum
        from backend.User import User
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in forum.users:
            raise ValueError("User is not a member of this forum")
        if user not in forum.restricted:
            # update db relationships
            session = SessionLocal()
            try:
                forum_model = session.get(ForumModel, forum.db_id)
                user_model = session.get(UserModel, getattr(user, 'db_id', None))
                if forum_model is not None and user_model is not None and user_model not in getattr(forum_model, 'restricted_users', []):
                    forum_model.restricted_users.append(user_model)
                    session.add(forum_model)
                    session.commit()
            finally:
                session.close()
            forum.restricted.append(user)
            if user in forum.authorized:
                ForumMembershipService.deauthorize_user(forum, user)
    
    @staticmethod
    def unrestrict_user(forum: 'Forum', user: 'User') -> None:
        # lift restriction from user in forum
        if user not in forum.restricted:
            return
        # update db relationships
        session = SessionLocal()
        try:
            forum_model = session.get(ForumModel, forum.db_id)
            user_model = session.get(UserModel, getattr(user, 'db_id', None))
            if forum_model is not None and user_model is not None and user_model in getattr(forum_model, 'restricted_users', []):
                forum_model.restricted_users.remove(user_model)
                session.add(forum_model)
                session.commit()
        finally:
            session.close()
        forum.restricted.remove(user)
    
    @staticmethod
    def is_authorized(forum: 'Forum', user: 'User') -> bool:
        # Check privilege
        return user in forum.authorized
    
    @staticmethod
    def get_users(forum: 'Forum') -> list:
        # Get the users in a forum
        from backend.User import User
        session = SessionLocal()
        try:
            forum_model = session.get(ForumModel, getattr(forum, 'db_id', None))
            if forum_model is None:
                return []
            users = []
            for u_model in forum_model.users:
                users.append(User.from_model(u_model))
            return users
        finally:
            session.close()




# Support class for managing Post and Forum relations
class ForumPostService:
    
    @staticmethod
    def add_post(forum: 'Forum', post: 'Post') -> None:
        # Add a post to a forum w/ validation
        from backend.Messages import Post
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        
        # Check membership by db_id instead of object identity
        user_ids = [u.db_id for u in forum.users]
        if post.poster.db_id not in user_ids:
            raise ValueError("post author must be a member of the forum")
        
        # Check if user is restricted
        restricted_ids = [u.db_id for u in forum.restricted]
        if post.poster.db_id in restricted_ids:
            raise ValueError("restricted users cannot add posts")
        
        if post not in forum.posts:
            forum.posts.append(post)
            # persist forum relation on post
            session = SessionLocal()
            try:
                post_model = session.get(PostModel, getattr(post, 'db_id', None))
                forum_model = session.get(ForumModel, forum.db_id)
                if post_model is not None and forum_model is not None:
                    post_model.forum_id = forum_model.id
                    session.add(post_model)
                    session.commit()
                    # mirror relation on wrapper so serialization exposes forum_id
                    try:
                        post.forum_id = forum_model.id
                    except Exception:
                        pass
            finally:
                session.close()
    
    @staticmethod
    def get_posts(forum: 'Forum') -> List['Post']:
        # Get posts from forum
        from backend.Messages import Post
        session = SessionLocal()
        try:
            db_posts = session.query(PostModel).filter(PostModel.forum_id == getattr(forum, 'db_id', None)).all()
            return [Post.from_model(db_post, session=session) for db_post in db_posts]
        finally:
            session.close()
