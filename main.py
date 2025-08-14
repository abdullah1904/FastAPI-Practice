from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Annotated
from sqlalchemy.orm import Session, joinedload
from database import engine, SessionLocal
import models
import schemas

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

database_dependency = Annotated[Session, Depends(get_database)]


# Global error handler for Pydantic validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0].get("msg", "Invalid input")
    return JSONResponse(status_code=400, content={"error": first_error})


# Global error handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# Routes
@app.get("/questions")
async def read_questions(db: database_dependency):
    return db.query(models.Question).options(joinedload(models.Question.choices)).all()


@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: database_dependency):
    question = (
        db.query(models.Question)
        .options(joinedload(models.Question.choices))
        .filter(models.Question.id == question_id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


@app.post("/questions", status_code=status.HTTP_201_CREATED)
async def create_question(question: schemas.QuestionBase, db: database_dependency):
    db_question = models.Question(questionText=question.questionText)

    for choice in question.choices:
        db_choice = models.Choice(choiceText=choice.choiceText, isCorrect=choice.isCorrect)
        db_question.choices.append(db_choice)

    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@app.put("/questions/{question_id}")
async def update_question(question_id: int, question: schemas.QuestionBase, db: database_dependency):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    db_question.questionText = question.questionText

    for db_choice, new_choice in zip(db_question.choices, question.choices):
        db_choice.choiceText = new_choice.choiceText
        db_choice.isCorrect = new_choice.isCorrect

    db.commit()
    db.refresh(db_question)
    return db_question


@app.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, db: database_dependency):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    db.delete(question)
    db.commit()
    return
