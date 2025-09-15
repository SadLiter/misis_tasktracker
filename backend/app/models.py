import enum
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func
from .database import Base

class StatusEnum(str, enum.Enum):
    todo = "ToDo"
    in_progress = "In Progress"
    done = "Done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(Enum(StatusEnum, name="status_enum", native_enum=False), nullable=False, default=StatusEnum.todo)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)