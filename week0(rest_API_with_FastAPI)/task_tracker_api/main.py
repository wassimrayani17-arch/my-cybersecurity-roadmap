From fastapi import FastAPI,HTTPException

from pydantic import BaseModel

app= FastAPI()



class Task(BaseModel):

title:str

completed : bool = False



tasks=[{"id":1,"title":"learn fastapi","completed":False},{"id":2,"title":"build task tracker","completed":False},]

@app.get("/tasks")

def get_all_tasks():

return tasks

@app.get("/tasks/{task_id}")

def get_task(task_id:int):

for task in tasks:

if task["id"]==task_id:

return task



raise HTTPException(status_code=404,detail="task not found!!")



@app.post("/tasks")

def create_task(task:Task):

new_id = max(task["id"] for task in tasks) + 1 if tasks else 1

new_task = {"id": new_id, "title": task.title, "completed": task.completed}

tasks.append(new_task)

return new_task



@app.put("/tasks/{task_id}")

def update_task(task_id:int, updated_task:Task):

for task in tasks:

if task["id"]==task.id:

task['title'] = updated_task.title

task['completed'] = updated_task.completed

return task

raise HTTPException(status_code=404,detail="task not found!!")



@app.delete("/tasks/{task_id}")

def delete_task(task_id:int):

for task in tasks:

if task["id"]==task_id:

tasks.remove(task)

return {"message":"task deleted successfully!!"}

raise HTTPException(status_code=404,detail="task not found!!")