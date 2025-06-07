from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row

app = FastAPI()

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
    


@app.post("/posts", status_code = status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, (post.title, post.content, post.published ))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    cursor.execute(""" select * from posts where id = %s """, (id))
    test_post = cursor.fetchone()
    print(test_post)
   
    return {"here": post}


@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")

    my_posts.pop(index)
    return { Response(status_code=status.HTTP_204_NO_CONTENT)}


@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")
    
    post_dict = post.model_dump()
    print(post_dict)
    post_dict['id'] = id
    my_posts[index] = post_dict
    return{"data": post_dict}