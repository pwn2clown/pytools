from typing import List

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import LargeBinary
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import Session, relationship, declarative_base, Mapped, mapped_column

Base = declarative_base()

class TemplatedRequest(Base):
    __tablename__ = "request_templates"

    id = mapped_column(Integer, primary_key=True)
    name = Column(String)
    entries : Mapped[List["TemplateEntry"]] = relationship(back_populates="template")

    def __repr__(self):
        return f"request template {self.request_templates}"

    def to_requests(self, values: dict):
        pass

    def header_insertion_point(self):
        pass

    def body_insertion_point(self):
        pass

class TemplateEntry(Base):
    __tablename__ = "template_entries"

    id = mapped_column(Integer, primary_key=True)
    typehint = Column(String)
    path = Column(String)
    template_id = Column(Integer, ForeignKey('request_templates.id'))
    template = relationship("TemplatedRequest", back_populates="entries")
    
    def __repr__(self):
        return f"template entry {self.path}"

#  class EnvContainer(Base):

#  class TemplateEnvValue(Base):
