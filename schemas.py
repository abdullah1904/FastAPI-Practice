from pydantic import BaseModel, Field, field_validator
from typing import List

class ChoiceBase(BaseModel):
    choiceText: str = Field(..., min_length=1, max_length=255)
    isCorrect: bool

class QuestionBase(BaseModel):
    questionText: str = Field(..., min_length=5, max_length=500)
    choices: List[ChoiceBase] = Field(..., min_items=2, max_items=2)

    @field_validator("choices")
    def at_least_one_correct(cls, v):
        if not any(choice.isCorrect for choice in v):
            raise ValueError("At least one choice must be marked as correct")
        return v
