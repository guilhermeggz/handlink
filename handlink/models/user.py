from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Integer, String, DateTime, Boolean
from handlink.ext.db import db

if TYPE_CHECKING:
    from .role_user import RoleUser
    from .location import Address
    from .service import Service
    from .appointment import Appointment

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index = True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    cpf: Mapped[Optional[str]] = mapped_column(String(15), unique=True, index=True)
    photo: Mapped[Optional[str]] = mapped_column(String(100))
    password: Mapped[Optional[str]] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    role_associations: Mapped[List['RoleUser']] = relationship(
        'RoleUser',
        back_populates='user',
        cascade='all, delete-orphan',
    )

    addresses: Mapped[List['Address']] = relationship(
        'Address',
        back_populates='user',
        cascade='all, delete-orphan',
    )

    services: Mapped[List['Service']] = relationship(
        'Service',
        back_populates='provider',
        cascade='all, delete-orphan'
    )

    appointments: Mapped[List['Appointment']] = relationship(
        'Appointment',
        back_populates='client',
        cascade='all, delete-orphan'
    )

    @property
    def roles(self):
        return [assoc.role for assoc in self.role_associations if assoc.role]

    def __repr__(self) -> str:
        return f"<User {self.email}>"