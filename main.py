from fastapi import FastAPI, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from db import engine, SessionLocal, Base
from models import Blog

import api
import schemas

app = FastAPI()
Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/blog', status_code=200)
def index(response: Response, db: Session = Depends(get_db)):
    try:
        data = db.query(Blog).all()
    except SQLAlchemyError:
        response.status_code = 500
        data = []

    return api.builder(data, response.status_code)


@app.get('/blog/{id}', status_code=200)
def show(id: int, response: Response, db: Session = Depends(get_db)):
    try:
        data = db.query(Blog).filter(Blog.id == id).one()
    except NoResultFound:
        response.status_code = 404
        data = []

    return api.builder(data, response.status_code)


@app.post('/blog', status_code=201)
def create(request: schemas.Blog, response: Response, db: Session = Depends(get_db)):
    try:
        data = Blog(title=request.title, body=request.body)
        db.add(data)
        db.commit()
        db.refresh(data)
    except SQLAlchemyError:
        response.status_code = 500
        data = []

    return api.builder(data, response.status_code)


@app.patch('/blog/{id}', status_code=200)
def update(id: int, response: Response, request: schemas.Blog, db: Session = Depends(get_db)):
    try:
        data = db.query(Blog).filter(Blog.id == id).one()
        data.title = request.title
        data.body = request.body

        db.commit()
        db.refresh(data)
    except NoResultFound:
        response.status_code = 404
        data = []
    except SQLAlchemyError:
        response.status_code = 500
        data = []

    return api.builder(data, response.status_code)


@app.delete('/blog/{id}', status_code=200)
def delete(id: int, response: Response, db: Session = Depends(get_db)):
    try:
        data = db.query(Blog).filter(Blog.id == id).one()
        db.delete(data)
        db.commit()
    except NoResultFound:
        response.status_code = 404
    except SQLAlchemyError:
        response.status_code = 500

    return api.builder(data=[], code=response.status_code)
