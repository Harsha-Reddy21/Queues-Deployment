
from database import Base

from sqlalchemy import Column, Integer, String, Float


class Restaurant(Base):

    __tablename__='restaurants'

    id=Column(Integer, primary_key=True, index=True)
    name=Column(Integer,index=True)
    cuisine=Column(String, index=True)
    rating=Column(Float,default=0.0)




    