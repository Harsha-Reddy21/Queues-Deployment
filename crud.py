from sqlalchemy.orm import Session
import models, schemas


def create_restaurant(db:Session, restaurant:schemas.RestaurantCreate):
    db_rest=models.Restaurant(**restaurant.dict())
    db.add(db_rest)
    db.commit(db_rest)
    return db_rest


def get_restaurants(db:Session,skip:int=0, limit:int=10):
    return db.query(models.Restaurant).offset(skip).limit(limit).all()