import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import model, schema

app = FastAPI()

def on_startup():
    if os.getenv("CI") != "true":
        Base.metadata.create_all(bind=engine)


@app.post("/users", response_model=schema.UserResponse)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    new_user = model.User(
        name=user.name,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", response_model=list[schema.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(model.User).all()
    return users


@app.put("/users/{user_id}", response_model=schema.UserResponse)
def update_user(
    user_id: int,
    user: schema.UserUpdate,
    db: Session = Depends(get_db)
):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    db_user.email = user.email

    db.commit()
    db.refresh(db_user)

    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}


