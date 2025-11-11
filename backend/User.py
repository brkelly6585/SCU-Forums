from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from backend.Messages import Post, Comment, Reaction
import random

if TYPE_CHECKING:
    from backend.Forum import Forum

# Import DB helpers
from .db import SessionLocal, init_db
from .models import UserModel
from .object_registry import register, get as registry_get

# Ensure DB tables exist
init_db()


class User:
    def __new__(cls, *args, **kwargs):
        # Support varied constructor signatures (subclasses may pass fewer args).
        # Attempt to extract email from kwargs or positional args.
        email = kwargs.get('email')
        if email is None and len(args) > 1:
            email = args[1]
        if email is None:
            return object.__new__(cls)

        # If a DB row exists for this email, return the existing wrapper (singleton behavior)
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.email == email).first()
            if user_model is not None:
                existing = registry_get('User', getattr(user_model, 'id', None))
                if existing is not None:
                    return existing
                # build wrapper from model and return it
                wrapper = cls.from_model(user_model)
                return wrapper
            # not found -> fall through and create a fresh instance
            return object.__new__(cls)
        finally:
            session.close()

    def __init__(self, username: str, email: str, major: str, year: int, posts: Optional[List[Post]], forum: Optional[List[Forum]], reactions: Optional[List[Forum]]) -> None:
        # If this wrapper already has a db_id (created via from_model or returned as existing), skip initialization
        if getattr(self, 'db_id', None) is not None:
            return

        # Validate username
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        self.is_deleted: bool = False  # Flag to track if user is deleted

        # Validate email
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        if not email or "@" not in email or not email.endswith("@scu.edu") or email == "@scu.edu":
            raise ValueError("Email must be a valid scu.edu address")

        # Validate major
        if not major or not isinstance(major, str):
            raise ValueError("Major must be a non-empty string")

        # Validate year
        if not isinstance(year, int):
            raise TypeError("Year must be an integer")
        if year < 1:
            raise ValueError("Year must be positive")

        # Check if user with this email exists in DB
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.email == email).first()
            if user_model is not None:
                # Return existing wrapper (identity preserved)
                existing = registry_get('User', getattr(user_model, 'id', None))
                if existing is not None:
                    # If called as a constructor, replace self with existing
                    self.__dict__ = existing.__dict__
                    return
                # Otherwise, build wrapper from model
                wrapper = self.from_model(user_model)
                self.__dict__ = wrapper.__dict__
                return
        finally:
            session.close()

        self.user_id: int = random.randint(10000, 99999)
        self.username: str = username
        self.email: str = email
        self.major: str = major
        self.year: int = year
        self.posts: List[Post] = posts if posts is not None else []
        self.forum: List[Forum] = forum if forum is not None else []
        self.reactions: List[Reaction] = reactions if reactions is not None else []
        # persist to DB
        session = SessionLocal()
        user_model = UserModel(username=self.username, email=self.email, major=self.major, year=self.year, is_deleted=self.is_deleted)
        session.add(user_model)
        session.commit()
        session.refresh(user_model)
        self.db_id = user_model.id
        session.close()
        # register wrapper to preserve identity when loading from DB
        register('User', getattr(self, 'db_id', None), self)
    
    def getAccountInfo(self) -> str:
        status = " [DELETED]" if self.is_deleted else ""
        return f"User ID: {self.user_id}, Username: {self.username}{status}, Email: {self.email}, Major: {self.major}, Year: {self.year}"
    
    def getposts(self) -> List[Post]:
        # Return posts for this user from the DB (DB is the source of truth).
        session = SessionLocal()
        try:
            from .models import PostModel
            from backend.Messages import Post

            db_posts = session.query(PostModel).filter(PostModel.poster_id == getattr(self, 'db_id', None)).all()
            return [Post.from_model(db_post, session=session) for db_post in db_posts]
        finally:
            session.close()
    
    def getforums(self) -> List[Forum]:
        # Return forums where this user is a member from the DB and sync self.forum.
        session = SessionLocal()
        try:
            from .models import ForumModel
            from backend.Forum import Forum

            db_forums = session.query(ForumModel).filter(ForumModel.users.any(id=getattr(self, 'db_id', None))).all()
            # print(f"[DEBUG] DB query for forums with user db_id={self.db_id}: {[f.id for f in db_forums]}")
            forum_wrappers = []
            for db_forum in db_forums:
                found = None
                for f in self.forum:
                    if getattr(f, 'db_id', None) == getattr(db_forum, 'id', None):
                        found = f
                        break
                if found is not None:
                    forum_wrappers.append(found)
                else:
                    wrapper = Forum.from_model(db_forum, session=session)
                    forum_wrappers.append(wrapper)
            # Sync self.forum to match DB membership
            self.forum = forum_wrappers
            # print(f"[DEBUG] User {self.username} (db_id={self.db_id}) forum wrappers after sync: {[f.db_id for f in self.forum]}")
            return forum_wrappers
        finally:
            session.close()
    
    def getreactions(self) -> List[Reaction]:
        # Return reactions for this user from the DB.
        session = SessionLocal()
        try:
            from .models import ReactionModel
            from backend.Messages import Reaction

            db_reactions = session.query(ReactionModel).filter(ReactionModel.user_id == getattr(self, 'db_id', None)).all()
            return [Reaction.from_model(db_reaction, session=session) for db_reaction in db_reactions]
        finally:
            session.close()

    @classmethod
    def load_by_db_id(cls, db_id: int):
        """Load a User wrapper from the DB by db id (returns None if not found)."""
        session = SessionLocal()
        try:
            user_model = session.get(UserModel, db_id)
            if user_model is None:
                return None
            return cls.from_model(user_model)
        finally:
            session.close()

    @classmethod
    def load_by_id(cls, user_id: int):
        """Alias for load_by_db_id for consistency with other models."""
        return cls.load_by_db_id(user_id)

    @classmethod
    def load_by_username(cls, username: str):
        """Load a User wrapper from the DB by username (returns None if not found)."""
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.username == username).first()
            if user_model is None:
                return None
            return cls.from_model(user_model)
        finally:
            session.close()

    @classmethod
    def load_by_email(cls, email: str):
        """Load a User wrapper from the DB by email (returns None if not found)."""
        session = SessionLocal()
        try:
            user_model = session.query(UserModel).filter(UserModel.email == email).first()
            if user_model is None:
                return None
            return cls.from_model(user_model)
        finally:
            session.close()

    @classmethod
    def from_model(cls, user_model: UserModel):
        # If a wrapper already exists for this DB row, return it to preserve identity.
        existing = registry_get('User', getattr(user_model, 'id', None))
        if existing is not None:
            return existing

        # Create a User wrapper from a DB model without persisting a new DB row.
        u = object.__new__(cls)
        u.is_deleted = bool(user_model.is_deleted)
        u.user_id = int(user_model.id) if user_model.id is not None else random.randint(10000, 99999)
        u.username = user_model.username
        u.email = user_model.email
        u.major = user_model.major
        u.year = int(user_model.year)
        u.posts = []
        u.forum = []
        u.reactions = []
        u.db_id = int(user_model.id)
        # register wrapper
        register('User', u.db_id, u)
        return u
    
    def getreactedposts(self) -> List[Post]:
        reacted_posts = []
        for reaction in self.reactions:
            if reaction.parent is not None and reaction.parent not in reacted_posts:
                reacted_posts.append(reaction.parent)
        return reacted_posts
    
    def addForum(self, forum: Forum) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        # Delegate to Forum.addUser to persist association and keep DB as source of truth
        if forum not in self.forum:
            forum.addUser(self)
    
    def removeForum(self, forum: Forum) -> None:
        # Delegate to Forum.removeUser so DB and wrapper state stay in sync
        if forum in self.forum:
            forum.removeUser(self)
    
    def addPost(self, forum: Forum, post: Post) -> None:
        if self.is_deleted:
            raise ValueError("Cannot add post: user has been deleted")
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if forum not in self.forum:
            raise ValueError("User is not part of the specified forum")
        if post not in self.posts:
            self.posts.append(post)
            # Delegate to forum.addPost to persist forum relation and keep DB in sync
            forum.addPost(post)
    
    def editPost(self, post: Post, new_message: str) -> None:
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if post not in self.posts:
            raise ValueError("User is not the author of the specified post")
        post.editmessage(new_message)
    
    def addComment(self, post: Post, comment: Comment) -> None:
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if not isinstance(comment, Comment):
            raise TypeError("comment must be a Comment instance")
        if post not in self.posts:
            raise ValueError("User is not the author of the specified post")
        post.add_comment(comment)
        if comment not in self.posts:
            self.posts.append(comment)
    
    def addReaction(self, post: Post, reaction_type: str) -> None:
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if post not in self.posts:
            raise ValueError("User is not the author of the specified post")
        # Construct Reaction with the User instance as the `user` parameter.
        reaction = Reaction(reaction_type=reaction_type, user=self, parent=post)
        post.reactions.append(reaction)
        self.reactions.append(reaction)
    

class Admin(User):
    def __init__(self, username: str, email: str, major: str, year: int) -> None:
        super().__init__(username, email, major, year, None, None, None)

    def removePost(self, forum: Forum, post: Post) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(post, Post):
            raise TypeError("post must be a Post instance")
        if post in forum.posts:
            # Set the post's is_deleted flag instead of removing it
            post.is_deleted = True
    
    def restrictUser(self, forum: Forum, user: User) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user.is_deleted:
            raise ValueError("Cannot restrict a deleted user")
        if user not in forum.getUsers():
            raise ValueError("User is not a member of this forum")
        forum.restrictUser(user)
    
    def unrestrictUser(self, forum: Forum, user: User) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user.is_deleted:
            raise ValueError("Cannot unrestrict a deleted user")
        forum.unrestrictUser(user)
    
    def authorizeUser(self, forum: Forum, user: User) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user.is_deleted:
            raise ValueError("Cannot authorize a deleted user")
        if user not in forum.getUsers():
            raise ValueError("User is not a member of this forum")
        forum.authorizeUser(user)
    
    def deauthorizeUser(self, forum: Forum, user: User) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user.is_deleted:
            raise ValueError("Cannot deauthorize a deleted user")
        forum.deauthorizeUser(user)

    def deleteUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user.is_deleted:
            raise ValueError("User is already deleted")
        user.is_deleted = True
        # Set all user's posts as deleted
        for post in user.posts:
            post.is_deleted = True

    def undeleteUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if not user.is_deleted:
            raise ValueError("User is not deleted")
        user.is_deleted = False
        # Note: This does not undelete the user's posts as they should remain deleted