from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind= engine) 

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='Com1par', row_factory=dict_row)
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


@app.get("/posts")
async def get_posts():
    cursor.execute(""" SELECT * FROM posts""")
    posts = cursor.fetchall()
    return{"data ": posts }
    
@app.get("/sqlalchemy")
async def test_posts(db: Session = Depends(get_db)):
    return{"Status" :  "Success"}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, (post.title, post.content, post.published ))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute(""" select * from posts where id = %s """, [str(id)])
    # you will run into issue if you only put (str(id)) in above code. You have to put (str(id),) or [str(id)] for the psycopg to properly parse the id. You don't even have to do str, you can just write (id), or [id]. Because psycopg expects a tuple or a list. without comma it won't be a tuple.
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return {"post_details" : post }


@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute(""" delete from posts where id = %s returning * """, (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")

    return  Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    cursor.execute(""" update posts set title = %s, content = %s, published = %s where id = %s returning * """, (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")
    
    
    
    return{"data": updated_post}