from typing import List
from backend.Messages import Post, Comment
from backend.User import User

from .db import SessionLocal, init_db
from .models import ForumModel, UserModel, PostModel
from .object_registry import register, get as registry_get

import random

# Ensure DB tables exist
init_db()

class Forum:
    def __new__(cls, *args, **kwargs):
        # Accept flexible args; extract course_name from kwargs or first positional arg
        course_name = kwargs.get('course_name')
        if course_name is None and len(args) > 0:
            course_name = args[0]
        if course_name is None:
            return object.__new__(cls)

        # If a forum with this course_name exists in DB, return the existing wrapper
        session = SessionLocal()
        try:
            forum_model = session.query(ForumModel).filter(ForumModel.course_name == course_name).first()
            if forum_model is not None:
                existing = registry_get('Forum', getattr(forum_model, 'id', None))
                if existing is not None:
                    return existing
                wrapper = cls.from_model(forum_model, session=session)
                return wrapper
            # not found -> create a fresh instance
            return object.__new__(cls)
        finally:
            session.close()

    # Class-level deleted user instance for maintaining post history
    DELETED_USER = User("[deleted]", "deleted@scu.edu", "N/A", 1, None, None, None)

    def __init__(self, course_name: str) -> None:
        # Check for existing forum by course_name
        session = SessionLocal()
        try:
            forum_model = session.query(ForumModel).filter(ForumModel.course_name == course_name).first()
            if forum_model is not None:
                existing = registry_get('Forum', getattr(forum_model, 'id', None))
                if existing is not None:
                    self.__dict__ = existing.__dict__
                    return
                wrapper = self.from_model(forum_model, session=session)
                self.__dict__ = wrapper.__dict__
                return
        finally:
            session.close()
        self.course_name: str = course_name
        self.forum_id: int = random.randint(1000, 9999)
        self.posts: list[Post] = []
        self.users: List[User] = []
        self.authorized: List[User] = []
        self.restricted: List[User] = []
        # persist forum to DB
        session = SessionLocal()
        forum_model = ForumModel(course_name=self.course_name)
        session.add(forum_model)
        session.commit()
        session.refresh(forum_model)
        self.db_id = forum_model.id
        session.close()
        # register wrapper
        register('Forum', getattr(self, 'db_id', None), self)

    @classmethod
    def from_model(cls, forum_model, session=None):
        # Return existing wrapper if present to preserve identity
        existing = registry_get('Forum', getattr(forum_model, 'id', None))
        if existing is not None:
            return existing

        # Build a Forum wrapper from a ForumModel without creating a duplicate DB row.
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True
        try:
            f = object.__new__(cls)
            f.course_name = forum_model.course_name
            f.forum_id = int(forum_model.id)
            f.posts = []
            f.users = []
            f.authorized = []
            f.restricted = []
            f.db_id = int(forum_model.id)
            # register wrapper
            register('Forum', f.db_id, f)
            return f
        finally:
            if close_session:
                session.close()
    
    @classmethod
    def load_by_course_name(cls, course_name: str):
        """Load a Forum wrapper from the DB by course name (returns None if not found)."""
        session = SessionLocal()
        try:
            forum_model = session.query(ForumModel).filter(ForumModel.course_name == course_name).first()
            if forum_model is None:
                return None
            return cls.from_model(forum_model, session=session)
        finally:
            session.close()
    
    def addUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in self.users:
            self.users.append(user)
            # persist association
            session = SessionLocal()
            forum_model = session.get(ForumModel, self.db_id)
            user_model = session.get(UserModel, getattr(user, 'db_id', None))
            if user_model is None:
                session.close()
                return
            if user_model not in forum_model.users:
                forum_model.users.append(user_model)
                session.add(forum_model)
                session.commit()
                # print(f"[DEBUG] Added user {user.username} (db_id={user.db_id}) to forum {self.course_name} (db_id={self.db_id})")
                # print(f"[DEBUG] ForumModel.users after add: {[u.id for u in forum_model.users]}")
            session.close()
            # ensure user's forum list also reflects membership (in-memory)
            try:
                if getattr(user, 'forum', None) is not None and self not in user.forum:
                    user.forum.append(self)
            except Exception:
                # ignore issues updating in-memory wrapper
                pass
    
    def removeUser(self, user: User) -> None:
        if user in self.users:
            # Update all posts by this user to use the deleted user
            for post in self.posts:
                if post.poster == user:
                    post.poster = self.DELETED_USER
                    # update DB poster id for that post
                    session = SessionLocal()
                    post_model = session.get(PostModel, getattr(post, 'db_id', None))
                    if post_model is not None:
                        post_model.poster_id = getattr(self.DELETED_USER, 'db_id', None)
                        session.add(post_model)
                        session.commit()
                    session.close()
            # Remove user from users list
            self.users.remove(user)
            # Clean up authorization lists
            if user in self.authorized:
                self.deauthorizeUser(user)
            if user in self.restricted:
                self.unrestrictUser(user)
            # remove association in DB
            session = SessionLocal()
            forum_model = session.get(ForumModel, self.db_id)
            user_model = session.get(UserModel, getattr(user, 'db_id', None))
            if user_model in forum_model.users:
                forum_model.users.remove(user_model)
                session.add(forum_model)
                session.commit()
            session.close()
            # remove forum from user's in-memory forum list if present
            try:
                if getattr(user, 'forum', None) is not None and self in user.forum:
                    user.forum.remove(self)
            except Exception:
                pass

    def authorizeUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in self.authorized:
            self.authorized.append(user)
            # Remove from restricted list when authorized
            if user in self.restricted:
                self.unrestrictUser(user)
    
    def deauthorizeUser(self, user: User) -> None:
        if user in self.authorized:
            self.authorized.remove(user)
    
    def restrictUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in self.restricted:
            self.restricted.append(user)
            # Remove from authorized list when restricted
            if user in self.authorized:
                self.deauthorizeUser(user)
    
    def unrestrictUser(self, user: User) -> None:
        if user in self.restricted:
            self.restricted.remove(user)
    
    def addPost(self, post: Post) -> None:
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if post.poster not in self.users:
            raise ValueError("post author must be a member of the forum")
        if post.poster in self.restricted:
            raise ValueError("restricted users cannot add posts")
        if post not in self.posts:
            self.posts.append(post)
            # persist forum relation on post
            session = SessionLocal()
            post_model = session.get(PostModel, getattr(post, 'db_id', None))
            forum_model = session.get(ForumModel, self.db_id)
            if post_model is not None and forum_model is not None:
                post_model.forum_id = forum_model.id
                session.add(post_model)
                session.commit()
            session.close()
    
    def removePost(self, post: Post) -> None:
        if post in self.posts:
            self.posts.remove(post)
            # unlink from DB
            session = SessionLocal()
            post_model = session.get(PostModel, getattr(post, 'db_id', None))
            if post_model is not None:
                post_model.forum_id = None
                session.add(post_model)
                session.commit()
            session.close()
    
    
    def getPosts(self) -> List[Post]:
        # Return posts for this forum from the DB (DB is the source of truth)
        session = SessionLocal()
        try:
            from .models import PostModel
            from backend.Messages import Post

            db_posts = session.query(PostModel).filter(PostModel.forum_id == getattr(self, 'db_id', None)).all()
            return [Post.from_model(db_post, session=session) for db_post in db_posts]
        finally:
            session.close()
    def getUsers(self) -> List[User]:
        # Return forum members from the DB
        session = SessionLocal()
        try:
            from .models import ForumModel
            forum_model = session.get(ForumModel, getattr(self, 'db_id', None))
            if forum_model is None:
                return []
            users = []
            from backend.User import User
            for u_model in forum_model.users:
                users.append(User.from_model(u_model))
            return users
        finally:
            session.close()
    def isauthorized(self, user: User) -> bool:
        return user in self.authorized
    def getCourseName(self) -> str:
        return self.course_name
    def getForumID(self) -> int:
        return self.forum_id
    