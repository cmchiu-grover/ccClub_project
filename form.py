from typing import Optional, Annotated, List
from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from sqlmodel import Field, Session, SQLModel

UserId = Annotated[str, BeforeValidator(str)]

class LoginForm(BaseModel):
    username: str
    password: str

class RegisterForm(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    gender: Optional[str] = Field(None)
    age: Optional[int] = Field(None, ge=0, le=110)  # 限制年齡範圍
    country: Optional[str] = Field(None)
    location: Optional[str] = Field(None)
    education: Optional[str] = Field(None)


class UserCollection(BaseModel):
    """
    A container holding a list of `RegisterForm` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    students: List[RegisterForm]

class UpdateUserForm(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "username": "user001( digitals is unnessasery )",
                "email": "user001@example.com"
            }
        },
    )



# class Article(SQLModel, table=True):
#     __tablename__ = 'articles'

#     # columns
#     id: int = Field(default=None, primary_key=True, autoincrement=True)
#     source: str = Field(max_length=64, index=True, nullable=False)
#     link: str = Field(max_length=255, unique=True, nullable=False)
#     introduction: str | None = Field(default=None, nullable=True)  # 使用 | None 表示可以是空值
#     title: str = Field(max_length=255, unique=True, index=True, nullable=False)
#     author: str | None = Field(default=None, nullable=True)  # 這個欄位是可選的
#     count: int = Field(default=1)  # 預設值為 1

#     def __init__(self, source: str, link: str, title: str, author: str | None, introduction: str | None):
#         self.source = source
#         self.link = link
#         self.title = title
#         self.author = author
#         self.introduction = introduction