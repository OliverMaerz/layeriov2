from sqlalchemy import Boolean, Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy.orm import Session, sessionmaker

from typing import List

from pydantic import BaseModel, EmailStr


# TODO: move credentials to config file, change pw
SQLALCHEMY_DATABASE_URI = "mysql://layeriou:tnQtS0jKmUpEp2tb9HSVX8gI9PgBwc@localhost/layerio"

class DbSession(Session):
    """Wrapper class for Session"""
    pass


class Auth:
    """Class for authentication (does only return demo user with user_id=1 at this point."""
    @staticmethod
    def get_current_user():
        """Placeholder for future implementation of real authentication"""
        # TODO: add real authentication (token, user/password, oauth2 etc.) possibly as async def get_current_user()
        return 1


@as_declarative()
class Base:
    # Add the __tablename__ attribute to all classes automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(Base):
    """Holds user info like user_id and email, place to add things like user's name, password/token/api key etc."""
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)


# TODO: Add some metadata to db objects like dates for created_on, last_modification as well as a title
# and a description for the share

class Share(Base):
    """Share object is created once for each share."""
    share_id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)


class Selection(Base):
    """Selection object is created for each selection of a sheet and hold sheet name, column, row etc."""
    selection_id = Column(Integer, primary_key=True)
    sheet_name = Column(String(255), nullable=False)
    share_id = Column(Integer, ForeignKey("share.share_id"), nullable=False)
    from_column = Column(String(10))
    from_row = Column(Integer)
    to_column = Column(String(10))
    to_row = Column(Integer)


class User2Share(Base):
    """Many to many relation between User and Share."""
    user2share_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    share_id = Column(Integer, ForeignKey("share.share_id"), nullable=False)


class SharingRequest(BaseModel):
    """Class to hold emails and sharings from API request"""
    emails: List[EmailStr]
    sharings: List[str]


class DbUtil:
    """Class with utility methods for database session etc."""
    def __init__(self):
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URI
            # isolation_level='READ_COMMITTED'
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session_local(self):
        """Get and return db session."""
        return self.SessionLocal()

    def close_session_local(self, request):
        """Close db session"""
        request.state.db.close()

    def create_demo_db(self):
        """Create a db for this demo."""
        # Create DB for demo TODO: replace this all with some schema change management!
        Base.metadata.create_all(bind=self.engine)

        db_session = self.SessionLocal()

        # create a user that will own all shares for this demo TODO: replace with user management, authentication etc.
        dummy_user = db_session.query(User).filter_by(user_id=1).first()
        if not dummy_user:
            dummy_user = User(user_id=1, email="oliver@berlinco.com")
            db_session.add(dummy_user)
            db_session.commit()
            db_session.close()
