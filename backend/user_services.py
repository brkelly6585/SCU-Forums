from typing import TYPE_CHECKING, Optional
from .db import SessionLocal
from .models import UserModel, PostModel, ReactionModel, ForumModel
from .object_registry import register, get as registry_get

if TYPE_CHECKING:
    from backend.User import User
    from backend.Messages import Post, Reaction
    from backend.Forum import Forum

# Manage User DB methods
class UserRepository:
    
    @staticmethod
    def load_by_db_id(db_id: int) -> Optional['User']:
        # Load wrapper from id
        from backend.User import User
        session = SessionLocal()
        try:
            user_model = session.get(UserModel, db_id)
            if user_model is None:
                return None
            return User.from_model(user_model)
        finally:
            session.close()

    @staticmethod
    def load_by_id(user_id: int) -> Optional['User']:
        # This just supports old calls that used id instead of db
        return UserRepository.load_by_db_id(user_id)

    @staticmethod
    def load_by_username(username: str) -> Optional['User']:
        # Load wrapper from username
        from backend.User import User
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.username == username).first()
            if user_model is None:
                return None
            return User.from_model(user_model)
        finally:
            session.close()

    @staticmethod
    def load_by_email(email: str) -> Optional['User']:
        # Load wrapper from email
        from backend.User import User
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.email == email).first()
            if user_model is None:
                return None
            return User.from_model(user_model)
        finally:
            session.close()
    
    @staticmethod
    def find_by_email(email: str) -> Optional['UserModel']:
        # Get model from email
        session = SessionLocal()
        try:
            return session.query(UserModel).filter(UserModel.email == email).first()
        finally:
            session.close()
    
    @staticmethod
    def create(username: str, email: str, major: str, year: int, is_deleted: bool = False, 
               is_admin: bool = False, first_name: str = '', last_name: str = '') -> 'UserModel':
        # Add user to DB
        session = SessionLocal()
        try:
            user_model = UserModel(
                username=username,
                email=email,
                major=major,
                year=year,
                is_deleted=is_deleted,
                is_admin=is_admin,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user_model)
            session.commit()
            session.refresh(user_model)
            return user_model
        finally:
            session.close()
    
    @staticmethod
    def get_posts(user: 'User') -> list:
        # Return posts for this user from the DB
        from backend.Messages import Post
        session = SessionLocal()
        try:
            db_posts = session.query(PostModel).filter(PostModel.poster_id == getattr(user, 'db_id', None)).all()
            return [Post.from_model(db_post, session=session) for db_post in db_posts]
        finally:
            session.close()
    
    @staticmethod
    def get_forums(user: 'User') -> list:
       # Return forums user is a part of from DB
        from backend.Forum import Forum
        session = SessionLocal()
        try:
            db_forums = session.query(ForumModel).filter(ForumModel.users.any(id=getattr(user, 'db_id', None))).all()
            forum_wrappers = []
            for db_forum in db_forums:
                found = None
                for f in user.forum:
                    if getattr(f, 'db_id', None) == getattr(db_forum, 'id', None):
                        found = f
                        break
                if found is not None:
                    forum_wrappers.append(found)
                else:
                    wrapper = Forum.from_model(db_forum, session=session)
                    forum_wrappers.append(wrapper)
            # Sync user.forum
            user.forum = forum_wrappers
            return forum_wrappers
        finally:
            session.close()
    
    @staticmethod
    def get_reactions(user: 'User') -> list:
        # Return reactions for this user from the DB
        from backend.Messages import Reaction
        session = SessionLocal()
        try:
            db_reactions = session.query(ReactionModel).filter(ReactionModel.user_id == getattr(user, 'db_id', None)).all()
            return [Reaction.from_model(db_reaction, session=session) for db_reaction in db_reactions]
        finally:
            session.close()
