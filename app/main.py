from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi.responses import JSONResponse
from random import randrange
import psycopg
from psycopg.rows import dict_row
import pprint
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user

models.Base.metadata.create_all(bind= engine) 

app = FastAPI()

while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='Com1par', row_factory= dict_row) # type: ignore
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

app.include_router(post.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my api."}


