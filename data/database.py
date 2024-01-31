

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, ARRAY
from sqlalchemy_mixins import AllFeaturesMixin

from datetime import datetime
from app import db


class BaseModel(db.Model, AllFeaturesMixin):
    __abstract__ = True
    pass



class Book(BaseModel):

    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(primary_key=True,)
    name: Mapped[str] = mapped_column(unique=False)
    path: Mapped[str]
    author: Mapped[str]
    title: Mapped[str]
    timestamp: Mapped[datetime]
    content: Mapped[str]
    thumbnail: Mapped[str]


BaseModel.set_session(db.session)
