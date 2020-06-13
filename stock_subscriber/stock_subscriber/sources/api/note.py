from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.schemas import User, NoteIn, NoteUpdate
from stock_subscriber.sources.utils import get_db
from sqlalchemy.orm import Session
from stock_subscriber.sources import crud
from stock_subscriber.sources.account_utils import get_current_user
from stock_subscriber.sources.subscription import curr_timezone
import datetime

router = APIRouter()

@router.get("/note/{note_id}")
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_note(db, id=note_id, user_id=current_user.id)

@router.get("/note")
def get_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_notes(db, user_id=current_user.id)


@router.post("/note")
def post_note(
    note_in: NoteIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):  
    note_in.user_id = current_user.id
    note_in.date = datetime.datetime.now(tz=curr_timezone)
    return crud.create_note(db, note_in=note_in)

@router.put("/note/{note_id}")
def put_note(
    note_id: int,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db, id=note_id, user_id=current_user.id)
    if note:
        note = crud.update_note(db, db_obj=note, note_in=note_in)
        return note
    return False

@router.delete("/note/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db, id=note_id, user_id=current_user.id)
    if note:
        crud.delete_note(db, note_id=note_id)
        return True


@router.get("/import_json")
def import_json(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import json
    with open('/stock_subscriber/import.json', 'rb') as f:
        json = json.load(f)
    data = json[2]['data']
    for row in data:
        try:
            note_in = NoteIn(user_id=current_user.id, title=row['title'], content=row['content'], date=datetime.datetime.strptime(row['date'], '%Y-%m-%d'), categories=[])
            crud.create_note(db, note_in=note_in)
        except:
            continue
