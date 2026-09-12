from fastapi import APIrouter,HTTPException
from app.models import Note

router=APIrouter()

notes=[{"id":1,"title":"Note 1","content":"This is the first note."},
       {"id":2,"title":"Note 2","content":"This is the second note"}]

@router.get("/notes")
def get_notes():
    return notes
@router.get("\notes\{id}")
def get_note_by_id(id:int):
    for note in notes:
        if note[id]==id:
            return note
        raise HTTPException(status_code=404,detail="Note not found")

@router.post("/notes")
def create_note(note:Note):
    new_note={id:len(notes)+1,"title":note.title,"content":note.content}
    notes.append(new_note)
    return new_note

@router.put("/notes/{id}")
def update_note(id:int,note:Note):
    for note in notes:
        if note["id"]==id:
            note["title"]=note.title
            note["content"]=note.content
            return note
    raise HTTPException(status_code=404,detail="Note not found")

@router.delete("/notes/{id}")
def delete_note(id:int):
    for note in notes:
        if note["id"]==id:
            notes.remove(note)
            return {"message":"Note deleted successfully"}
    raise HTTPException(status_code=404,detail="Note not found")