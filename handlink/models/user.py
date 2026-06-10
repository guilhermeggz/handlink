from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func, Integer, String, DateTime, Boolean, select
from sqlalchemy.ext.hybrid import hybrid_property
from handlink.ext.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from handlink.models.role_user import RoleUser, ProviderStatus
from handlink.models.role import Role

if TYPE_CHECKING:
    from .role_user import RoleUser
    from .location import Address
    from .service import Service
    from .appointment import Appointment
    from .category import Category

provider_categories = db.Table(
    'provider_categories',
    db.Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index = True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    cpf: Mapped[Optional[str]] = mapped_column(String(15), unique=True, index=True)

    cnpj: Mapped[Optional[str]] = mapped_column(String(18), unique=True, index=True)

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

    worked_categories: Mapped[List['Category']] = relationship(
        'Category',
        secondary=provider_categories,
        backref='providers'
    )

    @property
    def roles(self):
        return [assoc.role for assoc in self.role_associations if assoc.role]

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

# 1. Comportamento em Python (Objetos instanciados em memória)
    @hybrid_property
    def provider_status(self) -> Optional[str]:
        """Busca o status do usuário na associação de provider (em memória)."""
        if self.role_associations:
            for assoc in self.role_associations:
                if assoc.role and assoc.role.name == 'provider':
                    return assoc.provider_status
        return None

    # 2. Comportamento em SQL (Tradutor de Queries para o Banco de Dados)
    @provider_status.expression
    def provider_status(cls):
        return (
            select(RoleUser.provider_status)
            .join(Role, Role.id == RoleUser.role_id)
            .where(
                RoleUser.user_id == cls.id,
                Role.name == 'provider'
            )
            .correlate(cls)
            .as_scalar()
        )