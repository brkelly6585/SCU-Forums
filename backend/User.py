from __future__ import annotations
from typing import List, Optional
from backend.Messages import Post, Comment, Reaction
import random

class User:
    def __init__(self, username: str, email: str, major: str, year: int, posts: Optional[List[Post]], forum: Optional[List[Forum]], reactions: Optional[List[Forum]]) -> None:
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

        self.user_id: int = random.randint(10000, 99999)
        self.username: str = username
        self.email: str = email
        self.major: str = major
        self.year: int = year
        self.posts: List[Post] = posts if posts is not None else []
        self.forum: List[Forum] = forum if forum is not None else []
        self.reactions: List[Reaction] = reactions if reactions is not None else []
    
    def getAccountInfo(self) -> str:
        status = " [DELETED]" if self.is_deleted else ""
        return f"User ID: {self.user_id}, Username: {self.username}{status}, Email: {self.email}, Major: {self.major}, Year: {self.year}"
    
    def getposts(self) -> List[Post]:
        return self.posts
    
    def getforums(self) -> List[Forum]:
        return self.forum
    
    def getreactions(self) -> List[Reaction]:
        return self.reactions
    
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
        if forum not in self.forum:
            self.forum.append(forum)
    
    def removeForum(self, forum: Forum) -> None:
        if forum in self.forum:
            self.forum.remove(forum)
    
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
            forum.posts.append(post)
    
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