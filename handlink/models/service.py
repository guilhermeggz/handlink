from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Numeric, ForeignKey, Integer, String, Text, Boolean, DateTime
from handlink.ext.db import db

if TYPE_CHECKING:
    from .user import User
    from .category import Category
    from .location import City
    from .appointment import Appointment

class Service(db.Model):
    __tablename__ = 'services'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), index=True)
    desc: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    provider: Mapped['User'] = relationship(
        'User',
        back_populates='services'
    )

    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='services'
    )

    city: Mapped["City"] = relationship(
        "City",
        back_populates="services"
    )

    appointments: Mapped[List['Appointment']] = relationship(
        'Appointment',
        back_populates='service',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Service {self.name}>'
