from pydantic import BaseModel


# these are used for the pydantic models which format the ollama responses
class Book(BaseModel):
    title: str
    author: str


class Author(BaseModel):
    author: str


class BookCategories(BaseModel):
    categories: list[str]


class BookLanguage(BaseModel):
    is_english: bool
