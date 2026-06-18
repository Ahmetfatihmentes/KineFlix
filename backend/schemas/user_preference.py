from pydantic import BaseModel, Field


class PreferencesCreate(BaseModel):
    genres: list[str] = Field(min_length=1)


class PreferencesMessage(BaseModel):
    message: str
