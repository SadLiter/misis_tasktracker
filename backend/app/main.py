from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Task, StatusEnum

# Создаём таблицы при старте (для простоты)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="МИСиС TaskTracker")

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/tasks")
def create_task(
    title: str = Form(...),
    description: str = Form(""),
    due_date: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if not title.strip():
        return RedirectResponse("/", status_code=303)
    due = None
    if due_date:
        try:
            due = datetime.fromisoformat(due_date)
        except ValueError:
            due = None
    task = Task(title=title.strip(), description=description.strip(), due_date=due)
    db.add(task)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status == StatusEnum.todo:
        task.status = StatusEnum.in_progress
    elif task.status == StatusEnum.in_progress:
        task.status = StatusEnum.done
    else:
        task.status = StatusEnum.todo
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/tasks/{task_id}/delete")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()
    return RedirectResponse("/", status_code=303)