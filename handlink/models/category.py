from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, UniqueConstraint, Integer, String, Text, Boolean
from handlink.ext.db import db

if TYPE_CHECKING:
    from .service import Service

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    desc: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    services: Mapped[List['Service']] = relationship(
        'Service',
        back_populates='category',
    ) 

    def __repr__(self) -> str:
        return f'<Category {self.name}>'