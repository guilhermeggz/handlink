from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Integer, String, Boolean
from handlink.ext.db import db

if TYPE_CHECKING:
    from .role_user import RoleUser

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__= {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    role_associations: Mapped[List["RoleUser"]] = relationship(
        "RoleUser", 
        back_populates="role",
        cascade="all, delete-orphan",
    )
    def __repr__(self) -> str:
        return f"<Role {self.name}>"

