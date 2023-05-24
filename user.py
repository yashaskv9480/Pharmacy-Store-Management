from ast import For
from datetime import datetime
import re
from turtle import st
from fastapi import APIRouter
from fastapi import FastAPI, Request, Cookie
from fastapi.params import Form
from fastapi import HTTPException
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
#router.add_middleware(SessionMiddleware, secret_key='MyApp')

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

#constant name for DATABASE_NAME
DATABASE_NAME = "app.db"

class user:

    @router.get("/register",response_class=HTMLResponse)
    def register(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})


    @router.post("/register", response_class=HTMLResponse)
    def do_register(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...),
                    address: str = Form(...), phone: str = Form(...)):
        with sqlite3.connect(DATABASE_NAME) as con:
            cur = con.cursor()
            cur.execute("INSERT into users(username, password, email, address, phone) values(?,?,?,?,?)",
                        (username, password, email, address, phone))
            con.commit()
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


    @router.get("/login",response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})


    @router.post("/login", response_class=HTMLResponse)
    def do_login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from users where username =? and password=?", [username, password])
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Wrong Login id or password.Contact Admin")
            return templates.TemplateResponse("/login.html", {"request": request, "msg": "Invalid Username or Password"})    
        else:
            request.session.setdefault("isLogin", True)
            request.session.setdefault('username', user['username'])
            request.session.setdefault('uid', user['id'])
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)