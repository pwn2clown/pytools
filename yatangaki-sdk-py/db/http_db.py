from typing import List
from enum import Enum
from pathlib import Path

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import LargeBinary
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import Session, relationship, declarative_base, Mapped, mapped_column

from .db_connection import db_basepath

Base = declarative_base()

def httpdb(project_name: str):
    db_uri = "sqlite:///" + str(db_basepath() / project_name / "logs.db")
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)
    return Session(engine)

class HttpRequest(Base):
    __tablename__ = "http_requests"

    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    path = Column(String)
    method = Column(String)
    authority = Column(String)
    scheme = Column(String)
    headers : Mapped[List["HttpRequestHeader"]] = relationship(back_populates="request")
    query : Mapped[List["HttpRequestQuery"]] = relationship(back_populates="request")
    body = Column(LargeBinary)

    def __repr__(self) -> str:
        return "some http request"

class HttpResponse(Base):
    __tablename__ = "http_responses"

    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    status = Column(Integer)
    headers : Mapped[List["HttpResponseHeader"]] = relationship(back_populates="response")
    body = Column(LargeBinary)

    def __repr__(self) -> str:
        return "some http request"

class HttpRequestQuery(Base):
    __tablename__ = "request_query"

    id = mapped_column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('http_requests.id'))
    request = relationship("HttpRequest", back_populates="query")
    key = Column(String)
    value = Column(String)

    def __repr__(self) -> str:
        return "some http query params"

class HttpRequestHeader(Base):
    __tablename__ = "request_headers"

    id = mapped_column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('http_requests.id'))
    request = relationship("HttpRequest", back_populates="headers")
    key = Column(String)
    value = Column(String)

    def __repr__(self) -> str:
        return "some http request headers"

class HttpResponseHeader(Base):
    __tablename__ = "response_headers"

    id = mapped_column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey('http_responses.id'))
    response = relationship("HttpResponse", back_populates="headers")
    key = Column(String)
    value = Column(String)

    def __repr__(self) -> str:
        return "some http request headers"
