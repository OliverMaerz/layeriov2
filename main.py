from fastapi import FastAPI, HTTPException
from typing import List  # Set, Dict, Tuple, Optional
from pydantic import BaseModel, EmailStr

from sqlalchemy import Boolean, Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker

from starlette.requests import Request
from starlette.responses import Response

# import re
import pcre

import logging

SQLALCHEMY_DATABASE_URI = "mysql://layeriou:tnQtS0jKmUpEp2tb9HSVX8gI9PgBwc@localhost/layerio"
engine = create_engine(
    SQLALCHEMY_DATABASE_URI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CustomBase:
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)


class Sharing(Base):
    id = Column(Integer, primary_key=True, index=True)
    from_x = Column(Integer, unique=False, index=False)
    from_y = Column(Integer, unique=False, index=False)
    to_x = Column(Integer, unique=False, index=False)
    to_y = Column(Integer, unique=False, index=False)


class User2Sharing(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=False, index=True)
    sharing_id = Column(Integer, ForeignKey("sharing.id"), nullable=False, unique=False, index=True)


Base.metadata.create_all(bind=engine)


# db_session = SessionLocal()

# first_user = db_session.query(User).first()
#  if not first_user:
#    u = User(email="johndoe@example.com", hashed_password="notreallyhashed")
#    db_session.add(u)
#    db_session.commit()

# db_session.close()

class MasterSheet:
    """Class to hold the sheet data and manage the shares."""

    available_sheets = []

    def __init__(self, available_sheets: List[str]):
        self.available_sheets = available_sheets

    @classmethod
    def from_dummy_data(cls):
        """Initialize MasterSheet with dummy data."""
        available_sheets = ["HRReport", "Actuals", "Assumptions", "Dashboard"]
        return cls(available_sheets)

    @classmethod
    def empty(cls):
        """Initialize MasterSheet with empty sheet."""
        available_sheets = []
        return cls(available_sheets)

    @classmethod
    def from_excel(cls):
        """Initialize MasterSheet with data from Excel file."""
        pass

    @classmethod
    def from_csv(cls):
        """Initialize MasterSheet with data from CSV file."""
        pass

    @classmethod
    def from_google_sheet(cls):
        """Initialize MasterSheet with data from Google Sheets."""
        pass

    def check_sheet(self, sheet_name: str):
        """Returns True if sheet_name is valid, False otherwise.

        Keyword arguments:
        sheet_name -- str with name of sheet
        """

        if sheet_name in self.available_sheets:
            return True
        else:
            return False


#  class Sharings(BaseModel):
#     sometext: EmailStr


class Sharings(BaseModel):
    emails: List[EmailStr]
    sheet_selections: List[str]


# class Sharings(BaseModel):
#    sharing: Sharing()
#    email: str

# Dependency
def get_db(request: Request):
    return request.state.db


app = FastAPI()

demo_ms = MasterSheet.from_dummy_data()
empty_ms = MasterSheet.empty()


@app.get("/")
def read_root():
    return {"app": "Simple Sheet Manager", "version": "0.2"}


@app.put("/sharing/")
def add_sharing(sharings: Sharings):
    # check if sharing is valid etc.
    # raise HTTPException(status_code=404, detail="Item not found")
    text = None
    for sheet_selection in sharings.sheet_selections:
        # white space needed to be removed for pattern matching string without single quotes
        # regex = pcre.match("^((?>(>?'[\w\s]+')|(>?[\w]+))(?>![A-Z]{1}[0-9]{1})?(?>:[A-Z]{1}[0-9])?)",
        #                    sheet_selection)

        # Updated regular expression that allows A1:CCC1234567 and also lower case
        regex = pcre.search(
            "^((?>(>?'[\w\s]+')|(>?[\w]+))(?>![a-z,A-Z]{1,3}[0-9]{1,7})?(?>:[a-z,A-Z]{1,3}[0-9]{1,7})?)",
            sheet_selection)
        if (regex is None) or (regex.group() != sheet_selection):
            raise HTTPException(status_code=404,
                                detail="Sheet Selection string is not valid: "+sheet_selection)

        logging.warning('regex results: %s', regex)

    return {"success": True,
            "emails": sharings.emails,
            "sheet_selections": sharings.sheet_selections}


@app.get("/sharings/")
def list_sharings():
    return {"success": True, "sometext": sharings.sometext}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q, "mode": "synchronous"}


@app.get("/a/")
async def read_root():
    return {"Hello": "Asynchronous World"}


@app.get("/a/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    # y = await get_data(x)
    return {"item_id": item_id, "q": q, "mode": "asynchronous"}


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# Sheetnames
# from layer.io
# regex = "^((?>(>?'[\w\s]+')|(>?'[\w\s]+'))(?>![A-Z]{1}[0-9]{1})?(?>:[A-Z]{1}[0-9])?)"

# Files
# regex filter invalid characters windows [\\/:"*?<>|]+
# /^(?!.{256,})(?!(aux|clock\$|con|nul|prn|com[1-9]|lpt[1-9])(?:$|\.))[^ ][ \.\w-$()+=[\];#@~,&amp;']+[^\. ]$/i
