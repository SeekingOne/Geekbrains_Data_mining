from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class Author(Base, UrlMixin):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)


class Post(Base, UrlMixin):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    image_url = Column(String(250), nullable=False, unique=False)
    date = Column(Date, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=True)
    author = relationship("Author", backref="posts")
    tags = relationship("Tag", secondary=tag_post, back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    author = Column(String(150), nullable=False)
    text = Column(String(250), nullable=False, unique=False)
    likes = Column(Integer, nullable=False, unique=False)
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=True)
    parent_post = relationship("Post", back_populates="comments")


class Tag(Base, UrlMixin):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    posts = relationship(Post, secondary=tag_post, back_populates="tags")
