from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Table, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .db import Base

# Standard table for users in forums
forum_users = Table(
    "forum_users",
    Base.metadata,
    Column("forum_id", Integer, ForeignKey("forums.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# table for authorized Users
forum_authorized = Table(
    "forum_authorized",
    Base.metadata,
    Column("forum_id", Integer, ForeignKey("forums.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# table for restricted Users
forum_restricted = Table(
    "forum_restricted",
    Base.metadata,
    Column("forum_id", Integer, ForeignKey("forums.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    major = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    posts = relationship("PostModel", back_populates="poster")
    reactions = relationship("ReactionModel", back_populates="user")


class ForumModel(Base):
    __tablename__ = "forums"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    posts = relationship("PostModel", back_populates="forum")
    users = relationship("UserModel", secondary=forum_users, backref="forums")
    authorized_users = relationship("UserModel", secondary=forum_authorized, backref="authorized_forums")
    restricted_users = relationship("UserModel", secondary=forum_restricted, backref="restricted_forums")


class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    forum_id = Column(Integer, ForeignKey("forums.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    poster = relationship("UserModel", back_populates="posts")
    forum = relationship("ForumModel", back_populates="posts")
    comments = relationship("PostModel")
    reactions = relationship("ReactionModel", back_populates="parent")

    @hybrid_property
    def forum_name(self):
        return self.forum.course_name if self.forum else None


class ReactionModel(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    reaction_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    user = relationship("UserModel", back_populates="reactions")
    parent = relationship("PostModel", back_populates="reactions")
