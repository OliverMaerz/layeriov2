from fastapi import Depends, FastAPI, HTTPException

from starlette.requests import Request
from starlette.responses import Response

import pcre
import re
import sys

# so it works with docker
sys.path.append('/app')

from layerio.model import User, Share, User2Share, Selection, SharingRequest, DbUtil, Auth, DbSession
from layerio.mastersheet import MasterSheet


# create object to get and destroy db session (and also create demo db)
db_util = DbUtil()

app = FastAPI()

# Create the db for this little demo
db_util.create_demo_db()


# Dependency
def get_db(request: Request):
    return request.state.db

# create master_sheet object from dummy data
master_sheet = MasterSheet.from_dummy_data()

@app.get("/")
def read_root():
    return {"app": "Simple Sheet Manager", "version": "0.2"}


@app.put("/sharings/")
def add_sharing(sharing_request: SharingRequest, db: DbSession = Depends(get_db)):
    # create new share in db
    sh = Share(owner_id=Auth.get_current_user())
    db.add(sh)
    db.flush()

    # loop through emails and link them to share
    for email in sharing_request.emails:
        # check if user (email) already exists or create new one otherwise
        u = db.query(User).filter_by(email=email).first()
        if not u:
            # user does not exist -> create
            u = User(email=email)
            db.add(u)
            db.flush()

        #  many to many
        u2s = User2Share(user_id=u.user_id, share_id=sh.share_id)
        db.add(u2s)
        db.flush()

    # Loop through sharings and check if they match the regex
    for sharing in sharing_request.sharings:
        # Updated regex that allows A1:CCC1234567 and also lower case letters
        regex = pcre.search(
            "^((?>(>?'[\w\s]+')|(>?[\w]+))(?>![a-z,A-Z]{1,3}[0-9]{1,7})?(?>:[a-z,A-Z]{1,3}[0-9]{1,7})?)",
            sharing)
        if (regex is None) or (regex.group() != sharing):
            # selection does not match the regex (no or just partial match) return 404 error
            raise HTTPException(status_code=404,
                                detail="Sheet Selection string is not valid: " + sharing)

        # sharing matches the required format store in db but first split the info into atomic properties
        sheet_name, sheet_range = sharing.split("!", 1) if "!" in sharing else (sharing, None)
        sheet_name = sheet_name.replace("'", "")
        # check the sheet_name if valid
        if not master_sheet.check_sheet(sheet_name):
            # master_sheet object does not have a sheet with this name -> display error
            raise HTTPException(status_code=404,
                                detail="Sheet with name: '{}' does not exist.".format(sheet_name))

        from_range, to_range = sheet_range.split(":", 1) if sheet_range and ":" in sheet_range else (sheet_range, None)
        # logging.warning('debugging to_range: %s', to_range)
        # Split the character part ("A" ...) from the number part ("1" ... )
        from_column, from_row, _ = re.split("(\d+)", from_range) if from_range else (None, None, None)
        to_column, to_row, _ = re.split("(\d+)", to_range) if to_range else (None, None, None)

        sel = Selection(share_id=sh.share_id,
                        sheet_name=sheet_name,
                        from_column=from_column.upper() if from_column else None,
                        from_row=from_row,
                        to_column=to_column.upper() if to_column else None,
                        to_row=to_row)
        db.add(sel)
        db.flush()

    # all done commit transaction
    db.commit()
    return {"success": True,
            "emails": sharing_request.emails,
            "sheet_selections": sharing_request.sharings}


@app.get("/sharings/")
def list_sharings(db: DbSession = Depends(get_db)):
    """List all sharing ids for current user"""
    # query to get all in one join ...
    sh = db.query(Share, Selection, User2Share, User). \
        join(Selection). \
        join(User2Share). \
        join(User). \
        order_by(Share.share_id.desc()). \
        all()
    # logging.warning('debugging: %s', sh)
    return {"sharings": sh}


@app.get("/sharings/id")
def list_sharings(db: DbSession = Depends(get_db)):
    """List all sharing ids for current user"""
    sh = db.query(Share.share_id).filter_by(owner_id=Auth.get_current_user()).all()
    return {"sharings": [r for r, in sh]}


@app.get("/sharings/{share_id}/selections/")
def list_selections(share_id: int, db: DbSession = Depends(get_db)):
    """List selections for given share_id"""
    # join with Share object to check if current user is the really owner, but only return Selection object
    sel = db.query(Selection, Share). \
        with_entities(Selection). \
        filter(Selection.share_id == share_id, Share.owner_id == Auth.get_current_user()). \
        join(Share). \
        all()
    return {"selections": sel}


@app.get("/sharings/{share_id}/users/")
def list_selections(share_id: int, db: DbSession = Depends(get_db)):
    """List users (emails) for given share_id"""
    # join with Share object to check if current user is the really owner, but only return Selection object
    us = db.query(User, User2Share, Share). \
        with_entities(User.email). \
        filter(Share.share_id == share_id, Share.owner_id == Auth.get_current_user()). \
        join(User2Share). \
        join(Share). \
        all()
    return {"users": [r for r, in us]}


@app.middleware("http")
async def handle_db_session(request: Request, call_next):
    """Create the db session and destroy it at the end"""
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = db_util.get_session_local()
        response = await call_next(request)
    finally:
        db_util.close_session_local(request)
    return response




