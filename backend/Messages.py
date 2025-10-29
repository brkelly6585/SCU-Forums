from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from backend.User import User  # Only imported for type checking

class Post:
    # List of words that are not allowed in posts
    EXPLICIT_CONTENT = ["explicit_word1", "explicit_word2"]  # Need to udate with actual words
    DELETED_MESSAGE = "[deleted]"

    def __init__(self, poster: User, message: str, title: str, comments: Optional[List['Comment']] = None, reactions: Optional[List['Reaction']] = None):
        if poster is None:
            raise TypeError("poster cannot be None")
        if message is None:
            raise TypeError("message cannot be None")
        if title is None:
            raise TypeError("title cannot be None")
        if not message.strip():
            raise ValueError("message cannot be empty")
        if not title.strip():
            raise ValueError("title cannot be empty")
        
        # Check for explicit content
        message_lower = message.lower()
        for word in self.EXPLICIT_CONTENT:
            if word.lower() in message_lower:
                raise ValueError("Post contains inappropriate content")

        self.message: str = message
        self.title: str = title
        self.id: int = random.randint(1000, 9999)
        self.poster: User = poster
        # use a per-instance list
        self.comments: List['Comment'] = comments if comments is not None else []
        self.reactions: List['Reaction'] = reactions if reactions is not None else []
        # Flag to track if post is deleted. If the poster is already deleted, propagate that state.
        self.is_deleted: bool = getattr(self.poster, "is_deleted", False)

    def add_comment(self, comment: 'Comment') -> None:
        if not isinstance(comment, Comment):
            raise TypeError("comment must be a Comment instance")
        # append only if not already present
        if comment not in self.comments:
            self.comments.append(comment)
        comment.parent = self

    def remove_comment(self, comment: 'Comment') -> None:
        if comment in self.comments:
            # Mark the comment as deleted but keep it in the tree
            comment.editmessage(self.DELETED_MESSAGE)
            comment.title = self.DELETED_MESSAGE
            comment.is_deleted = True  # Set deletion flag

    def getposter(self) -> User:
        return self.poster
    
    def getcomments(self) -> List['Comment']:
        return self.comments
    
    def getreactions(self) -> List['Reaction']:
        return self.reactions
    
    def getmessage(self) -> str:
        return self.message

    def editmessage(self, new_message: str) -> None:
        self.message = new_message
    
    def addreaction(self, reaction: 'Reaction') -> None:
        if not isinstance(reaction, Reaction):
            raise TypeError("reaction must be a Reaction instance")
            
        # Check if user already has a reaction of this type
        for existing_reaction in self.reactions:
            if existing_reaction == reaction:
                raise ValueError("User already has this type of reaction on this post")
                
        self.reactions.append(reaction)
    
    def removereaction(self, reaction: 'Reaction') -> None:
        if reaction in self.reactions:
            self.reactions.remove(reaction)

    def addcomment(self, comment: 'Comment') -> None:
        if not isinstance(comment, Comment):
            raise TypeError("comment must be a Comment instance")
        if comment not in self.comments:
            self.comments.append(comment)
        comment.parent = self

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, message={self.message!r}, comments={len(self.comments)})"


class Comment(Post):
    def __init__(self, poster: User, message: str, title: str, parent: Post, comments: Optional[List['Comment']] = None, reactions: Optional[List['Reaction']] = None):
        # A Comment is a specialized Post with a parent Post. Use Post to assign id and store poster/message/title.
        super().__init__(poster=poster, message=message, title=title, comments=comments, reactions=reactions)
        if not isinstance(parent, Post):
            raise TypeError("parent must be a Post instance")
        if isinstance(parent, Comment) and parent.getmessage() == self.DELETED_MESSAGE:
            raise ValueError("Cannot comment on a deleted comment")
        # set parent and register this comment with the parent
        self.parent: Optional[Post] = None
        parent.add_comment(self)
    
    def getparent(self) -> Optional[Post]:
        return self.parent
        
    def remove_comment(self, comment: 'Comment') -> None:
        # Override to mark deleted comments while preserving the tree structure
        if comment in self.comments:
            comment.editmessage(self.DELETED_MESSAGE)
            comment.title = self.DELETED_MESSAGE

    def __repr__(self) -> str:
        parent_id = self.parent.id if self.parent is not None else None
        return f"Comment(id={self.id!r}, title={self.title!r}, parent_id={parent_id!r})"

class Reaction():
    # Define allowed reaction types
    VALID_REACTION_TYPES = ["like", "dislike", "heart", "flag"] # These are temp types

    def __init__(self, reaction_type: str, user: User, parent: Optional[Post] = None):
        if user is None:
            raise TypeError("user cannot be None")
        if reaction_type not in self.VALID_REACTION_TYPES:
            raise ValueError(f"Invalid reaction type. Must be one of: {', '.join(self.VALID_REACTION_TYPES)}")

        self.reaction_type: str = reaction_type
        self.user: User = user
        self.parent: Optional[Post] = parent
    
    def gettype(self) -> str:
        return self.reaction_type

    def getuser(self) -> User:
        return self.user

    def getparent(self) -> Optional[Post]:
        return self.parent

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Reaction):
            return NotImplemented
        # Two reactions are considered equal if they have the same type and user
        return self.reaction_type == other.reaction_type and self.user == other.user

    def __repr__(self) -> str:
        return f"Reaction(type={self.reaction_type!r}, user_id={self.user_id!r})"