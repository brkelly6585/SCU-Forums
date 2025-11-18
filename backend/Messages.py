from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import random

# DB imports
from .db import SessionLocal, init_db
from .models import PostModel, ReactionModel
from .object_registry import register, get as registry_get

# Ensure DB tables exist
init_db()

if TYPE_CHECKING:
    from backend.User import User  # Only imported for type checking

class Post:
    # List of words that are not allowed in posts
    EXPLICIT_CONTENT = ["explicit_word1", "explicit_word2"]  # Need to udate with actual words
    DELETED_MESSAGE = "[deleted]"

    def __new__(cls, *args, **kwargs):
        # Always create a new wrapper, unless it alread exists in db
        return object.__new__(cls)

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

        # If wrapper already has a db_id, skip initialization
        if getattr(self, 'db_id', None) is not None:
            return

        self.message: str = message
        self.title: str = title
        self.id: int = random.randint(1000, 9999)
        self.poster: User = poster
        # use a per-instance list
        self.comments: List['Comment'] = comments if comments is not None else []
        self.reactions: List['Reaction'] = reactions if reactions is not None else []
        # Flag to track if post is deleted. If the poster is already deleted, delete.
        self.is_deleted: bool = getattr(self.poster, "is_deleted", False)
        # Maintain db
        session = SessionLocal()
        poster_id = getattr(self.poster, 'db_id', None)
        post_model = PostModel(poster_id=poster_id, forum_id=None, title=self.title, message=self.message, is_deleted=self.is_deleted, parent_id=None)
        session.add(post_model)
        session.commit()
        session.refresh(post_model)
        self.db_id = post_model.id
        self.created_at = getattr(post_model, 'created_at', None)
        session.close()
        # register wrapper to preserve identity
        register('Post', getattr(self, 'db_id', None), self)

    def add_comment(self, comment: 'Comment') -> None:
        if not isinstance(comment, Comment):
            raise TypeError("comment must be a Comment instance")
        # append only if not already present
        if comment not in self.comments:
            self.comments.append(comment)
        comment.parent = self

    def remove_comment(self, comment: 'Comment') -> None:
        if comment in self.comments:
            # Mark the comment as deleted but keep active
            comment.editmessage(self.DELETED_MESSAGE)
            comment.title = self.DELETED_MESSAGE
            comment.is_deleted = True  # Set deletion flag

    def getposter(self) -> User:
        # Return poster loaded from DB.
        poster_db_id = getattr(self, 'db_id', None)
        # If poster, return them
        if getattr(self.poster, 'db_id', None) is not None:
            return self.poster
        # Otherwise, try to load from db
        session = SessionLocal()
        try:
            from .models import PostModel, UserModel
            if getattr(self, 'db_id', None) is None:
                return self.poster
            post_model = session.get(PostModel, getattr(self, 'db_id', None))
            if post_model is None or post_model.poster is None:
                return self.poster
            from backend.User import User
            return User.from_model(post_model.poster)
        finally:
            session.close()
    
    def getcomments(self) -> List['Comment']:
        # Load comments for this post from DB
        session = SessionLocal()
        try:
            from .models import PostModel
            from backend.Messages import Post
            if getattr(self, 'db_id', None) is None:
                return self.comments
            db_comments = session.query(PostModel).filter(PostModel.parent_id == getattr(self, 'db_id', None)).all()
            # reuse in-memory comment wrappers when possible (likely less necessary now that its in server)
            comments = []
            for db_comment in db_comments:
                found = None
                for c in self.comments:
                    if getattr(c, 'db_id', None) == getattr(db_comment, 'id', None):
                        found = c
                        break
                if found is not None:
                    comments.append(found)
                else:
                    c = Post.from_model(db_comment, session=session)
                    c.parent = self
                    self.comments.append(c)
                    comments.append(c)
            return comments
        finally:
            session.close()
    
    def getreactions(self) -> List['Reaction']:
        # Load reactions for this post from DB
        session = SessionLocal()
        try:
            from .models import ReactionModel
            from backend.Messages import Reaction
            if getattr(self, 'db_id', None) is None:
                return self.reactions
            db_reactions = session.query(ReactionModel).filter(ReactionModel.parent_id == getattr(self, 'db_id', None)).all()
            reactions = []
            for r_model in db_reactions:
                # prefer existing reaction wrappers
                found = None
                for r in self.reactions:
                    if getattr(r, 'db_id', None) == getattr(r_model, 'id', None):
                        found = r
                        break
                if found is not None:
                    found.parent = self
                    reactions.append(found)
                else:
                    r = Reaction.from_model(r_model, session=session)
                    r.parent = self
                    # add to list
                    self.reactions.append(r)
                    reactions.append(r)
            return reactions
        finally:
            session.close()
    
    def editmessage(self, new_message: str) -> None:
        self.message = new_message
    
    def addreaction(self, reaction: 'Reaction') -> None:
        if not isinstance(reaction, Reaction):
            raise TypeError("reaction must be a Reaction instance")
            
        # Check if user already has a reaction of this type
        for existing_reaction in self.reactions:
            if existing_reaction == reaction:
                raise ValueError("User already has this type of reaction on this post")
                
        # attach reaction to this post
        self.reactions.append(reaction)
        reaction.parent = self
        try:
            session = SessionLocal()
            from .models import ReactionModel
            reaction_model = session.get(ReactionModel, getattr(reaction, 'db_id', None))
            if reaction_model is not None:
                reaction_model.parent_id = getattr(self, 'db_id', None)
                session.add(reaction_model)
                session.commit()
        finally:
            try:
                session.close()
            except Exception:
                pass

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, message={self.message!r}, comments={len(self.comments)})"

    @classmethod
    def from_model(cls, post_model, session=None):
        # Build a Post wrapper from a PostModel without creating a duplicate
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True
        try:
            # return existing wrapper if present to preserve identity
            existing = registry_get('Post', getattr(post_model, 'id', None))
            if existing is not None:
                return existing

            p = object.__new__(cls)
            p.message = post_model.message
            p.title = post_model.title
            # Use DB id as wrapper id for stability
            p.id = int(post_model.id)
            
            poster = None
            if post_model.poster is not None:
                from backend.User import User
                poster = User.from_model(post_model.poster)
            p.poster = poster
            p.comments = []
            p.reactions = []
            p.is_deleted = bool(post_model.is_deleted)
            p.db_id = int(post_model.id)
            p.created_at = getattr(post_model, 'created_at', None)
            # get forum relationship id for serialization
            try:
                p.forum_id = getattr(post_model, 'forum_id', None)
            except Exception:
                p.forum_id = None
            p.parent = None
            # register wrapper
            register('Post', p.db_id, p)

            # load comments
            try:
                from .models import PostModel, ReactionModel
                child_models = session.query(PostModel).filter(PostModel.parent_id == p.db_id).all()
                for child_model in child_models:
                    child = Post.from_model(child_model, session=session)
                    child.parent = p
                    p.comments.append(child)

                # load reactions for this post
                reaction_models = session.query(ReactionModel).filter(ReactionModel.parent_id == p.db_id).all()
                for r_model in reaction_models:
                    r = Reaction.from_model(r_model, session=session)
                    r.parent = p
                    p.reactions.append(r)
            except Exception:
                # if any DB access fails here, return the partially populated wrapper
                pass

            return p
        finally:
            if close_session:
                session.close()
    
    @classmethod
    def load_by_id(cls, post_id: int):
        """Load a Post wrapper from the DB by post ID (returns None if not found)."""
        session = SessionLocal()
        try:
            post_model = session.query(PostModel).filter(PostModel.id == post_id).first()
            if post_model is None:
                return None
            return cls.from_model(post_model, session=session)
        finally:
            session.close()


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
        # Update DB to set parent_id for this comment row
        parent.add_comment(self)
        try:
            session = SessionLocal()
            from .models import PostModel
            comment_model = session.get(PostModel, getattr(self, 'db_id', None))
            if comment_model is not None:
                comment_model.parent_id = getattr(parent, 'db_id', None)
                session.add(comment_model)
                session.commit()
        finally:
            try:
                session.close()
            except Exception:
                pass
        
    def remove_comment(self, comment: 'Comment') -> None:
        # Override to mark deleted comments while preserving existance
        if comment in self.comments:
            comment.editmessage(self.DELETED_MESSAGE)
            comment.title = self.DELETED_MESSAGE

    def __repr__(self) -> str:
        parent = getattr(self, 'parent', None)
        parent_id = parent.id if parent is not None else None
        return f"Comment(id={self.id!r}, title={self.title!r}, parent_id={parent_id!r})"

class Reaction():
    # Define allowed reaction types
    VALID_REACTION_TYPES = ["like", "dislike", "heart", "flag"] # These are temp types

    def __new__(cls, *args, **kwargs):
        # Support flexible args/kwargs
        reaction_type = kwargs.get('reaction_type') if 'reaction_type' in kwargs else (args[0] if len(args) > 0 else None)
        user = kwargs.get('user') if 'user' in kwargs else (args[1] if len(args) > 1 else None)
        parent = kwargs.get('parent') if 'parent' in kwargs else (args[2] if len(args) > 2 else None)
        if reaction_type is None or user is None:
            return object.__new__(cls)

        # Prevent duplicate: return existing wrapper if a matching reaction exists
        session = SessionLocal()
        try:
            user_id = getattr(user, 'db_id', None)
            parent_id = getattr(parent, 'db_id', None) if parent is not None else None
            reaction_model = session.query(ReactionModel).filter(
                ReactionModel.reaction_type == reaction_type,
                ReactionModel.user_id == user_id,
                ReactionModel.parent_id == parent_id
            ).first()
            if reaction_model is not None:
                existing = registry_get('Reaction', getattr(reaction_model, 'id', None))
                if existing is not None:
                    return existing
                wrapper = cls.from_model(reaction_model, session=session)
                return wrapper
            # not found create a new one
            return object.__new__(cls)
        finally:
            session.close()

    def __init__(self, reaction_type: str, user: User, parent: Optional[Post] = None):
        if user is None:
            raise TypeError("user cannot be None")
        if reaction_type not in self.VALID_REACTION_TYPES:
            raise ValueError(f"Invalid reaction type. Must be one of: {', '.join(self.VALID_REACTION_TYPES)}")

        # If wrapper already has db_id, skip
        if getattr(self, 'db_id', None) is not None:
            return

        self.reaction_type: str = reaction_type
        self.user: User = user
        self.parent: Optional[Post] = parent
        # persist reaction to DB
        session = SessionLocal()
        user_id = getattr(self.user, 'db_id', None)
        parent_id = getattr(self.parent, 'db_id', None)
        reaction_model = ReactionModel(reaction_type=self.reaction_type, user_id=user_id, parent_id=parent_id)
        session.add(reaction_model)
        session.commit()
        session.refresh(reaction_model)
        self.db_id = reaction_model.id
        session.close()
        # register wrapper to preserve identity
        register('Reaction', getattr(self, 'db_id', None), self)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Reaction):
            return NotImplemented
        # Two reactions are considered equal if they have the same type and user
        return self.reaction_type == other.reaction_type and self.user == other.user

    def __repr__(self) -> str:
        user_id = getattr(self.user, 'db_id', None)
        return f"Reaction(type={self.reaction_type!r}, user_id={user_id!r})"

    @classmethod
    def from_model(cls, reaction_model, session=None):
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True
        try:
            # reuse existing wrapper if present
            existing = registry_get('Reaction', getattr(reaction_model, 'id', None))
            if existing is not None:
                return existing

            r = object.__new__(cls)
            r.reaction_type = reaction_model.reaction_type
            # Build user wrapper if available
            user = None
            if reaction_model.user is not None:
                from backend.User import User
                user = User.from_model(reaction_model.user)
            r.user = user
            r.parent = None
            r.db_id = int(reaction_model.id)
            # register wrapper
            register('Reaction', r.db_id, r)
            return r
        finally:
            if close_session:
                session.close()