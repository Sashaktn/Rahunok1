from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Waybill(Base):
    __tablename__ = 'waybills'
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'))
    total = Column(Float, nullable=False)
    status = Column(String, default='created')
    client = relationship('Client')
    invoice = relationship('Invoice')
    __table_args__ = (UniqueConstraint('invoice_id', name='_invoice_id_uc'),)
