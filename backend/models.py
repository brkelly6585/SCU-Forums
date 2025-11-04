from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from .db import Base

# association table for forum <-> users many-to-many
forum_users = Table(
    "forum_users",
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

    posts = relationship("PostModel", back_populates="poster")
    reactions = relationship("ReactionModel", back_populates="user")


class ForumModel(Base):
    __tablename__ = "forums"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)

    posts = relationship("PostModel", back_populates="forum")
    users = relationship("UserModel", secondary=forum_users, backref="forums")


class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    forum_id = Column(Integer, ForeignKey("forums.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    poster = relationship("UserModel", back_populates="posts")
    forum = relationship("ForumModel", back_populates="posts")
    comments = relationship("PostModel")
    reactions = relationship("ReactionModel", back_populates="parent")


class ReactionModel(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    reaction_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    user = relationship("UserModel", back_populates="reactions")
    parent = relationship("PostModel", back_populates="reactions")
