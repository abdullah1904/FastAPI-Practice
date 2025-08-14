from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    questionText = Column(String, nullable=False, index=True)
    
    # Relationship to choices
    choices = relationship(
        "Choice",
        back_populates="question",
        cascade="all, delete-orphan"
    )

class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    choiceText = Column(String, nullable=False, index=True)
    isCorrect = Column(Boolean, default=False, nullable=False)
    questionId = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # Relationship back to question
    question = relationship("Question", back_populates="choices")