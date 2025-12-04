from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from backend.Messages import Post, Comment, Reaction
import random

if TYPE_CHECKING:
    from backend.Forum import Forum

# DB imports
from .db import SessionLocal, init_db
from .models import UserModel
from .object_registry import register, get as registry_get

# Service imports
from .user_services import UserRepository

# Ensure DB tables exist
init_db()


class User:
    def __new__(cls, *args, **kwargs):
        # Allow kwargs for username and email due to expanded params
        email = kwargs.get('email')
        if email is None and len(args) > 1:
            email = args[1]
        if email is None:
            return object.__new__(cls)

        # If a DB row exists for this email, return it
        user_model = UserRepository.find_by_email(email)
        if user_model is not None:
            existing = registry_get('User', getattr(user_model, 'id', None))
            if existing is not None:
                return existing
            # build wrapper and return it
            wrapper = cls.from_model(user_model)
            return wrapper
        # not found, create new user
        return object.__new__(cls)

    def __init__(self, username: str, email: str, major: str, year: int, posts: Optional[List[Post]], forum: Optional[List[Forum]], reactions: Optional[List[Forum]], is_admin: bool = False, **kwargs) -> None:
        # If this wrapper already has a db_id, skip
        if getattr(self, 'db_id', None) is not None:
            return

        # Validate traits
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        self.is_deleted: bool = False  # Flag to track if user is deleted
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        if not email or "@" not in email or not email.endswith("@scu.edu") or email == "@scu.edu":
            raise ValueError("Email must be a valid scu.edu address")
        if not major or not isinstance(major, str):
            raise ValueError("Major must be a non-empty string")
        if not isinstance(year, int):
            raise TypeError("Year must be an integer")
        if year < 1:
            raise ValueError("Year must be positive")

        # Check if user with this email exists in DB
        user_model = UserRepository.find_by_email(email)
        if user_model is not None:
            existing = registry_get('User', getattr(user_model, 'id', None))
            if existing is not None:
                self.__dict__ = existing.__dict__
                return
            wrapper = self.from_model(user_model)
            self.__dict__ = wrapper.__dict__
            return

        self.user_id: int = random.randint(10000, 99999)
        self.username: str = username
        self.email: str = email
        self.major: str = major
        self.year: int = year
        self.first_name: str = kwargs.get('first_name', '') if isinstance(kwargs.get('first_name', ''), str) else ''
        self.last_name: str = kwargs.get('last_name', '') if isinstance(kwargs.get('last_name', ''), str) else ''
        self.posts: List[Post] = posts if posts is not None else []
        self.forum: List[Forum] = forum if forum is not None else []
        self.reactions: List[Reaction] = reactions if reactions is not None else []
        self.is_admin: bool = bool(is_admin)
        
        # Create in database via repository
        user_model = UserRepository.create(
            username=self.username,
            email=self.email,
            major=self.major,
            year=self.year,
            is_deleted=self.is_deleted,
            is_admin=self.is_admin,
            first_name=self.first_name,
            last_name=self.last_name
        )
        self.db_id = user_model.id
        
        # register wrapper to preserve identity when loading from DB
        register('User', getattr(self, 'db_id', None), self)
    
    # Getters using services
    def getposts(self) -> List[Post]:
        return UserRepository.get_posts(self)
    
    def getforums(self) -> List[Forum]:
        return UserRepository.get_forums(self)
    
    def getreactions(self) -> List[Reaction]:
        return UserRepository.get_reactions(self)

    # Loads from DB in various ways
    @classmethod
    def load_by_db_id(cls, db_id: int):
        return UserRepository.load_by_db_id(db_id)

    @classmethod
    def load_by_id(cls, user_id: int):
        return UserRepository.load_by_id(user_id)

    @classmethod
    def load_by_username(cls, username: str):
        return UserRepository.load_by_username(username)

    @classmethod
    def load_by_email(cls, email: str):
        return UserRepository.load_by_email(email)

    @classmethod
    def from_model(cls, user_model: UserModel):
        # If a wrapper already exists, return
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
        u.first_name = getattr(user_model, 'first_name', '') or ''
        u.last_name = getattr(user_model, 'last_name', '') or ''
        u.posts = []
        u.forum = []
        u.reactions = []
        u.is_admin = bool(getattr(user_model, 'is_admin', False))
        u.db_id = int(user_model.id)
        # register wrapper
        register('User', u.db_id, u)
        return u
    
    # Manage Forum and post relations
    def addForum(self, forum: Forum) -> None:
        from backend.Forum import Forum
        if not isinstance(forum, Forum):
            raise TypeError("forum must be a Forum instance")
        # Use Forum.addUser to keep relation
        if forum not in self.forum:
            forum.addUser(self)
    
    def removeForum(self, forum: Forum) -> None:
        # Use Forum.removeUser so DB and wrapper stay synced
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
            forum.addPost(post)


class Admin(User):
    def __init__(self, username: str, email: str, major: str, year: int) -> None:
        super().__init__(username, email, major, year, None, None, None, is_admin=True)

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