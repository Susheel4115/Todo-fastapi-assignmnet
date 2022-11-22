# main.py

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import engine, sessionlocal
import models
from fastapi import FastAPI, Request, Depends, Form, status
# Import Jinja2Templates.
# Create a templates object that you can re-use later.
# Declare a Request parameter in the path operation that will return a template.
# Use the templates you created to render and return a TemplateResponse, passing the request as one of the key-value pairs in the Jinja2 "context".
from fastapi.templating import Jinja2Templates


# FastAPI will use this response_model to: Convert the output data to its type declaration. Validate the data. Add a JSON Schema for the response, in the OpenAPI path operation.

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# mounting the static css file to the main.py to display the output

app.mount("/static", StaticFiles(directory="static"), name="static")

# creating a new session for every instance of db.


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


# route to get all the todo

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).order_by(models.Todo.id.desc())
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

# add todo using post method


@app.post("/add")
async def add(request: Request, task: str = Form(...), db: Session = Depends(get_db)):
    todo = models.Todo(task=task)
    db.add(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

# edit a specific todo item


@app.get("/edit/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "todo": todo})

# checking the todo is complete or not


@app.post("/edit/{todo_id}")
async def add(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(False), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


# deleting a particular todo using db.delete
@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
