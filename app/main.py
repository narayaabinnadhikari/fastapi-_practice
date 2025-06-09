from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi.responses import JSONResponse
import psycopg.rows
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
import pprint
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind= engine) 

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='Com1par', row_factory= dict_row)
        cursor = conn.cursor()
        print("DB connection was a Success.")
        break
    except Exception as error:
        print("Connection to DB failed.")
        print("Error: ", error)


my_posts = [{"title": "first_post",
    "content": "Title of First",
    "id":1},
    {"title": "second_post",
    "content": "Title of Second",
    "id":2} ]

def find_posts(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
async def root():
    return {"message": "Welcome to my api."}


@app.get("/sqlalchemy")
async def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{"data" :  posts}


@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return{"data" :  posts}
    

@app.post("/posts", status_code = status.HTTP_201_CREATED)
async def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    # this below code way the long way of doing the same.
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return {'post_details' : post}



@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    # intead use first() in above line and do db.delete(post) below.

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")
    post.delete()
    db.commit()
    return  Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
async def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if  post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return{"data": post_query.first()}