from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Integer, ForeignKey, String, DateTime
from handlink.ext.db import db

if TYPE_CHECKING:
    from .user import User
    from .service import Service

class Appointment(db.Model):
    __tablename__ = 'appointments'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'), nullable=False, index=True)

    # Status: Pendente, Confirmado, Cancelado, Finalizado
    status: Mapped[Optional[str]] = mapped_column(String(15), nullable=False, default='Pendente')

    appointment_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    client: Mapped['User'] = relationship(
        'User',
        back_populates='appointments',
    )

    service: Mapped['Service'] = relationship(
        'Service',
        back_populates='appointments'
    )
    
    def __repr__(self) -> str:
        return f"<Appointment client_id={self.client_id} service_id={self.service_id}>"