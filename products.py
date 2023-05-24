from ast import For
from datetime import datetime
import re
from turtle import st
from fastapi import APIRouter
from fastapi import FastAPI, Request, Cookie
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import starlette.status as status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# creating a FastAPI object
router = APIRouter()
security = HTTPBasic()

# configuring the static, which serve static
router.mount("/static", StaticFiles(directory="static"), name="static")


# adding the Session Middleware
# app.add_middleware(SessionMiddleware, secret_key='MyApp')

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

#constant name for DATABASE_NAME
DATABASE_NAME = "app.db"

class products: 

    @router.get("/shop", response_class=HTMLResponse)
    def shop(request: Request):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from products")
        plants = cur.fetchall()
        con.close
        return templates.TemplateResponse("shop.html", {"request": request, "plants": plants})


    @router.get("/details/{pid}", response_class=HTMLResponse)
    def detail(request: Request, pid: int):
        if not request.session.get('isLogin'):
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)

        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from products where id =?", [pid])
        description = cur.fetchall()
        con.close

        return templates.TemplateResponse("details.html", {"request": request, "pid": pid, "description": description[0]})
