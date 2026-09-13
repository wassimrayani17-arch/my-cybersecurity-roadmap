from fastapi import APIRouter, HTTPException
from app.models import Task,CommentCreate
from app.db import get_connection

router = APIRouter()




@router.get("/tasks")
def get_all_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, completed FROM tasks;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "completed": bool(r[2])} for r in rows]


@router.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, completed FROM tasks WHERE id = %s;", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": row[0], "title": row[1], "completed": bool(row[2])}



@router.post("/tasks")
def create_task(task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, completed) VALUES (%s, %s);",
        (task.title, task.completed),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "title": task.title, "completed": task.completed}



@router.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("update tasks set title=%s,completed=%s where id=%s;",(updated_task.title,updated_task.completed,task_id),)
    if cur.rowcount==0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404,detail="task not found!!")
    conn.commit()
    cur.close()
    conn.close()
    return{"id":task_id,"title":updated_task.title,"completed":updated_task.completed}
    

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Task {task_id} deleted"}

@router.post("/tasks/{task_id}/comments")
def create_comment(task_id: int, comment: CommentCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO comments (task_id, body) VALUES (%s, %s);",
            (task_id, comment.body),
        )
        new_id = cur.lastrowid
        conn.commit()
    except Exception:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Task not found or invalid foreign key")
    cur.close()
    conn.close()
    return {"id": new_id, "task_id": task_id, "body": comment.body}

@router.get("/tasks/{task_id}/comments")
def get_comments_for_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, task_id, body FROM comments WHERE task_id = %s;",
        (task_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "task_id": r[1], "body": r[2]} for r in rows]