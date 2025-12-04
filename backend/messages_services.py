from typing import TYPE_CHECKING, Optional
from .db import SessionLocal
from .models import PostModel, ReactionModel
from .object_registry import register, get as registry_get

if TYPE_CHECKING:
    from backend.Messages import Post, Comment, Reaction
    from backend.User import User

# Manage Post DB methods
class PostRepository:
    
    @staticmethod
    def load_by_id(post_id: int) -> Optional['Post']:
        # Load wrapper from id
        from backend.Messages import Post
        session = SessionLocal()
        try:
            post_model = session.query(PostModel).filter(PostModel.id == post_id).first()
            if post_model is None:
                return None
            return Post.from_model(post_model, session=session)
        finally:
            session.close()
    
    @staticmethod
    def create(poster_id: int, title: str, message: str, is_deleted: bool = False, 
               forum_id: Optional[int] = None, parent_id: Optional[int] = None) -> 'PostModel':
        # Add post to DB
        session = SessionLocal()
        try:
            post_model = PostModel(
                poster_id=poster_id,
                forum_id=forum_id,
                title=title,
                message=message,
                is_deleted=is_deleted,
                parent_id=parent_id
            )
            session.add(post_model)
            session.commit()
            session.refresh(post_model)
            return post_model
        finally:
            session.close()
    
    @staticmethod
    def get_comments(post: 'Post') -> list:
        # Load comments from DB
        from backend.Messages import Post
        session = SessionLocal()
        try:
            if getattr(post, 'db_id', None) is None:
                return post.comments
            db_comments = session.query(PostModel).filter(PostModel.parent_id == getattr(post, 'db_id', None)).all()
            # reuse in-memory comment wrappers when possible
            comments = []
            for db_comment in db_comments:
                found = None
                for c in post.comments:
                    if getattr(c, 'db_id', None) == getattr(db_comment, 'id', None):
                        found = c
                        break
                if found is not None:
                    comments.append(found)
                else:
                    c = Post.from_model(db_comment, session=session)
                    c.parent = post
                    post.comments.append(c)
                    comments.append(c)
            return comments
        finally:
            session.close()
    
    @staticmethod
    def get_reactions(post: 'Post') -> list:
        # Load reactions from DB
        from backend.Messages import Reaction
        session = SessionLocal()
        try:
            if getattr(post, 'db_id', None) is None:
                return post.reactions
            db_reactions = session.query(ReactionModel).filter(ReactionModel.parent_id == getattr(post, 'db_id', None)).all()
            reactions = []
            for r_model in db_reactions:
                # prefer existing reaction wrappers
                found = None
                for r in post.reactions:
                    if getattr(r, 'db_id', None) == getattr(r_model, 'id', None):
                        found = r
                        break
                if found is not None:
                    found.parent = post
                    reactions.append(found)
                else:
                    r = Reaction.from_model(r_model, session=session)
                    r.parent = post
                    # add to list
                    post.reactions.append(r)
                    reactions.append(r)
            return reactions
        finally:
            session.close()
    
    @staticmethod
    def get_poster(post: 'Post') -> 'User':
        # Return poster from DB
        from backend.User import User
        # If poster is available, return them
        if getattr(post.poster, 'db_id', None) is not None:
            return post.poster
        # Otherwise, try to load from db
        session = SessionLocal()
        try:
            if getattr(post, 'db_id', None) is None:
                return post.poster
            post_model = session.get(PostModel, getattr(post, 'db_id', None))
            if post_model is None or post_model.poster is None:
                return post.poster
            return User.from_model(post_model.poster)
        finally:
            session.close()

# Manage Reaction DB methods
class ReactionRepository:
    
    @staticmethod
    def find_by_type_user_parent(reaction_type: str, user_id: int, parent_id: Optional[int]) -> Optional['ReactionModel']:
        # Find a reaction model by type, user, and parent (necessary to make sure its unique)
        session = SessionLocal()
        try:
            return session.query(ReactionModel).filter(
                ReactionModel.reaction_type == reaction_type,
                ReactionModel.user_id == user_id,
                ReactionModel.parent_id == parent_id
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def create(reaction_type: str, user_id: int, parent_id: Optional[int] = None) -> 'ReactionModel':
        # Add reaction to DB
        session = SessionLocal()
        try:
            reaction_model = ReactionModel(
                reaction_type=reaction_type,
                user_id=user_id,
                parent_id=parent_id
            )
            session.add(reaction_model)
            session.commit()
            session.refresh(reaction_model)
            return reaction_model
        finally:
            session.close()
