import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from models import Base, User, Note
from passlib.context import CryptContext


engine = db.create_engine("sqlite:///data.db", echo=True)

metadata_obj = db.MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)
engine.dispose()
session = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




def is_email_available(user_data):
    return session.query(User).filter(User.email == user_data.email).first()


async def get_user_by_username(username) -> User:
    return session.query(User).filter(User.email == username).first()


async def get_post_by_id(id) -> Note:
    return session.query(Note).filter(Note.id == id).first()


def create_user(user_data):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def delete_user(user_data):
    user = session.query(User).filter(User.id == user_data).first()
    posts = get_all_posts(user_data)
    if user is None:
        return False
    else:
        if posts is not None:
            for post in posts:
                session.delete(post)
        session.delete(user)
        session.commit()
        return True


def create_post(post_data):
    post = Note(
        title=post_data.title, content=post_data.content, user_id=post_data.user_id
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

def update_post(post_data):
    # Fetch the post you want to update
    post = session.query(Note).filter(Note.id == post_data.post_id).first()
    print("TITLE", post_data.title)
    if post is None:
        return False
    # # Update fields with new values from post_data
    setattr(post, "title", post_data.title)
    setattr(post, "content", post_data.content)
    # Commit the changes
    session.commit()
    return True
    
def delete_post(postId: int):
    post = session.query(Note).filter(Note.id == postId).first()
    if post is None:
        return False
    else:
        session.delete(post)
        session.commit()
        return True


def get_all_posts(user_id):
    return session.query(Note).filter(Note.user_id == user_id).all()
