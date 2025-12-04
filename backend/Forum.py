from typing import List
from backend.Messages import Post, Comment
from backend.User import User

# DB imports
from .db import SessionLocal, init_db
from .models import ForumModel, UserModel, PostModel
from .object_registry import register, get as registry_get

# Service imports
from .forum_services import ForumMembershipService, ForumPostService, ForumRepository

import random

# Ensure DB tables exist
init_db()

class Forum:
    def __new__(cls, *args, **kwargs):
        # Allow kwargs for course name and details
        course_name = kwargs.get('course_name')
        if course_name is None and len(args) > 0:
            course_name = args[0]
        if course_name is None:
            return object.__new__(cls)

        # Check if forum already exists
        forum_model = ForumRepository.find_by_course_name(course_name)
        if forum_model is not None:
            existing = registry_get('Forum', getattr(forum_model, 'id', None))
            if existing is not None:
                return existing
            wrapper = cls.from_model(forum_model)
            return wrapper
        # if not found, create new
        return object.__new__(cls)

    # Class-level deleted user instance for maintaining post history
    DELETED_USER = User("[deleted]", "deleted@scu.edu", "N/A", 1, None, None, None)

    def __init__(self, course_name: str) -> None:
        # Check for existing forum by course_name
        forum_model = ForumRepository.find_by_course_name(course_name)
        if forum_model is not None:
            existing = registry_get('Forum', getattr(forum_model, 'id', None))
            if existing is not None:
                self.__dict__ = existing.__dict__
                return
            wrapper = self.from_model(forum_model)
            self.__dict__ = wrapper.__dict__
            return
        
        self.course_name: str = course_name
        self.forum_id: int = random.randint(1000, 9999)
        self.posts: list[Post] = []
        self.users: List[User] = []
        self.authorized: List[User] = []
        self.restricted: List[User] = []
        
        # Create in database via repository
        forum_model = ForumRepository.create(course_name)
        self.db_id = forum_model.id
        self.created_at = getattr(forum_model, 'created_at', None)
        
        # register wrapper
        register('Forum', getattr(self, 'db_id', None), self)
        
        # Set DELETED_USER on service
        ForumMembershipService.DELETED_USER = self.DELETED_USER

    @classmethod
    def from_model(cls, forum_model, session=None):
        # Build wrapper from model
        existing = registry_get('Forum', getattr(forum_model, 'id', None))
        if existing is not None:
            return existing

        # Build a Forum wrapper from a ForumModel without creating a duplicate
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True
        try:
            f = object.__new__(cls)
            f.course_name = forum_model.course_name
            f.forum_id = int(forum_model.id)
            f.posts = []
            # Load users from the forum_model's users relationship
            from backend.User import User
            f.users = [User.from_model(user_model) for user_model in forum_model.users]
            # Load authorized/restricted user wrappers from relationships
            f.authorized = [User.from_model(user_model) for user_model in getattr(forum_model, 'authorized_users', [])]
            f.restricted = [User.from_model(user_model) for user_model in getattr(forum_model, 'restricted_users', [])]
            f.db_id = int(forum_model.id)
            f.created_at = getattr(forum_model, 'created_at', None)
            # register wrapper
            register('Forum', f.db_id, f)
            return f
        finally:
            if close_session:
                session.close()
    

    # Loaders from DB
    @classmethod
    def load_by_course_name(cls, course_name: str):
        return ForumRepository.load_by_course_name(course_name)
    
    @classmethod
    def load_by_id(cls, course_id: int):
        return ForumRepository.load_by_id(course_id)
    
    @classmethod
    def load_all_forums(cls) -> List['Forum']:
        return ForumRepository.load_all()
    
    # User relation methods
    def addUser(self, user: User) -> None:
        ForumMembershipService.add_user(self, user)
    
    def removeUser(self, user: User) -> None:
        ForumMembershipService.remove_user(self, user)

    def authorizeUser(self, user: User) -> None:
        ForumMembershipService.authorize_user(self, user)
    
    def deauthorizeUser(self, user: User) -> None:
        ForumMembershipService.deauthorize_user(self, user)
    
    def restrictUser(self, user: User) -> None:
        ForumMembershipService.restrict_user(self, user)
    
    def unrestrictUser(self, user: User) -> None:
        ForumMembershipService.unrestrict_user(self, user)
    
    def isauthorized(self, user: User) -> bool:
        return ForumMembershipService.is_authorized(self, user)
    
    def getUsers(self) -> List[User]:
        return ForumMembershipService.get_users(self)
    
    # Post relation methods
    def addPost(self, post: Post) -> None:
        ForumPostService.add_post(self, post)
    
    def getPosts(self) -> List[Post]:
        return ForumPostService.get_posts(self)
    
    # Used for reg tests
    def getCourseName(self) -> str:
        return self.course_name
    
    def removePost(self, post: Post) -> None:
        if post in self.posts:
            self.posts.remove(post)