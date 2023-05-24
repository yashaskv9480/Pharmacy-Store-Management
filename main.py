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
import products
import user
import cart
import admins

# creating a FastAPI object
app = FastAPI()
security = HTTPBasic()

# configuring the static, which serve static
app.mount("/static", StaticFiles(directory="static"), name="static")


# adding the Session Middleware
app.add_middleware(SessionMiddleware, secret_key='MyApp')

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

#constant name for DATABASE_NAME
DATABASE_NAME = "app.db"


app.include_router(admins.router)

app.include_router(products.router)

app.include_router(user.router)

app.include_router(cart.router)





# declaring urls
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})



@app.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)



@app.get("/orders",response_class=HTMLResponse)
def orders(request : Request):
    if not request.session.get('isLogin'):
        return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)

    uid = request.session.get('uid')

    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT *,o.id as oid from USERS u,orders o, products p where u.id=o.uid and o.pid=p.id and o.uid =?",
                [uid])
    orders = cur.fetchall()
    con.close
    return templates.TemplateResponse("/orders.html", {"request": request, "orders": orders})





@app.get("/products", response_class=HTMLResponse)
def products(request: Request):
    con = sqlite3.connect("app.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from products")
    products = cur.fetchall()
    con.close
    return templates.TemplateResponse("/products.html", {"request" : request, "products": products })  
