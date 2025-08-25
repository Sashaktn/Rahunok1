from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'))
    total = Column(Float, nullable=False)
    status = Column(String, default='draft')
    client = relationship('Client')
    items = relationship('InvoiceItem', back_populates='invoice')

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String, default='шт.')
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    invoice = relationship('Invoice', back_populates='items')