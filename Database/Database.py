import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import Models


class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=False)
        Models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)
        self.purge_database()

    def purge_database(self):
        session = self.maker()
        session.query(Models.tag_post).delete()
        session.query(Models.Comment).delete()
        session.query(Models.Post).delete()
        session.query(Models.Tag).delete()
        session.query(Models.Author).delete()
        session.commit()
        session.close()

    def get_or_create_author(self, session, new_author: dict):
        # session = self.maker()
        author = session.query(Models.Author).filter_by(url=new_author["url"]).first()
        if author:
            return author
        else:
            return Models.Author(**new_author)

    def get_or_create_tags(self, session, new_tags: list):
        tags = []
        for tag_data in new_tags:
            tag = session.query(Models.Tag).filter_by(url=tag_data["url"]).first()
            if tag:
                tags.append(tag)
            else:
                tag = Models.Tag(**tag_data)
                session.add(tag)
                tags.append(tag)
        return tags

    def create_comments(self, session, new_comments: list):
        comments = []
        for new_comment in new_comments:
            comment = Models.Comment(
                id=new_comment["comment_id"],
                parent_id=new_comment["parent_id"],
                author=new_comment["author"],
                text=new_comment["text"],
                likes=new_comment["likes"]
            )
            session.add(comment)
            comments.append(comment)
            added_comments = self.create_comments(session, new_comment["replies"])
            comments.extend(added_comments)
        return comments

    def add_post(self, data):
        session = self.maker()
        # comments = self.create_comments(session, data["comments"])
        post = Models.Post(**data["post"], author=self.get_or_create_author(session, data["author"]),
                           tags=self.get_or_create_tags(session, data["tags"]),
                           comments=self.create_comments(session, data["comments"]))

        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
        finally:
            session.close()

    def check_data(self, data):
        """
        Для проверки и информации, выводим только что сохраненную запись на экран
        """
        session = self.maker()
        for post in session.query(Models.Post). \
                filter(Models.Post.title == data["post"]["title"]):
            print("Added to DB:")
            print(post.title, post.author.name, post.url, post.author_id)
            print("Tags:")
            for tag in post.tags:
                print(tag.name, tag.url)
            print("Comments:")
            for comment in post.comments:
                print(f"Parent id: {comment.parent_id} Comment id: {comment.id}\n Автор: {comment.author}\nТекст:{comment.text}")
        session.close()
