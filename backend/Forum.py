from typing import List
from backend.Messages import Post, Comment
from backend.User import User

import random

class Forum:
    # Class-level deleted user instance for maintaining post history
    DELETED_USER = User("[deleted]", "deleted@scu.edu", "N/A", 1, None, None, None)

    def __init__(self, course_name: str) -> None:
        self.course_name: str = course_name
        self.forum_id: int = random.randint(1000, 9999)
        self.posts: list[Post] = []
        self.users: List[User] = []
        self.authorized: List[User] = []
        self.restricted: List[User] = []
    
    def addUser(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("user must be a User instance")
        if user not in self.users:
            self.users.append(user)
    
    def removeUser(self, user: User) -> None:
        if user in self.users:
            # Update all posts by this user to use the deleted user
            for post in self.posts:
                if post.poster == user:
                    post.poster = self.DELETED_USER
            # Remove user from users list
            self.users.remove(user)
            # Clean up authorization lists
            if user in self.authorized:
                self.deauthorizeUser(user)
            if user in self.restricted:
                self.unrestrictUser(user)

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
    
    def removePost(self, post: Post) -> None:
        if post in self.posts:
            self.posts.remove(post)
    
    
    def getPosts(self) -> List[Post]:
        return self.posts
    def getUsers(self) -> List[User]:
        return self.users
    def isauthorized(self, user: User) -> bool:
        return user in self.authorized
    def getCourseName(self) -> str:
        return self.course_name
    def getForumID(self) -> int:
        return self.forum_id
    