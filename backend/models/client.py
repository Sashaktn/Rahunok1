from sqlalchemy import Column, Integer, String
from .base import Base

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)  # ІПН, ЄДРПОУ, ГО, інше, все в одному полі