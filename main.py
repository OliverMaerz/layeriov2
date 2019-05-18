from fastapi import FastAPI
from typing import List  # Set, Dict, Tuple, Optional
from pydantic import BaseModel, EmailStr


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


class Sharings(BaseModel):
    sometext: EmailStr


# class Sharings(BaseModel):
#    sharing: Sharing()
#    email: str


app = FastAPI()

demo_ms = MasterSheet.from_dummy_data()
empty_ms = MasterSheet.empty()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.put("/sharing/")
def add_sharing(sharings: Sharings):
    return {"success": True, "sometext": sharings.sometext}


@app.put("/sharings/")
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


# Sheetnames
# from layer.io
regex = "^((?>(>?'[\w\s]+')|(>?'[\w\s]+'))(?>![A-Z]{1}[0-9]{1})?(?>:[A-Z]{1}[0-9])?)"


# Files
# regex filter invalid characters windows [\\/:"*?<>|]+
# /^(?!.{256,})(?!(aux|clock\$|con|nul|prn|com[1-9]|lpt[1-9])(?:$|\.))[^ ][ \.\w-$()+=[\];#@~,&amp;']+[^\. ]$/i