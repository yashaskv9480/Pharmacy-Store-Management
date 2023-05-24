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
#router.add_middleware(SessionMiddleware, secret_key='MyApp')

# configuring the HTML pages
templates = Jinja2Templates(directory="templates")

#constant name for DATABASE_NAME
DATABASE_NAME = "app.db"

class admins:

    @router.get("/admin/", response_class=HTMLResponse)
    def admin_index(request: Request):
        return templates.TemplateResponse("/admin/index.html", {"request": request})


    @router.post("/admin/", response_class=HTMLResponse)
    def admin_index(request: Request, username: str = Form(...), password: str = Form(...)):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from admin where username =? and password=?", [username, password])
        admin = cur.fetchone()
        if not admin:
            return templates.TemplateResponse("/admin/index.html", {"request": request, "msg": "Invalid Username or Password"})
        else:
            request.session.setdefault("isLogin", True)
            request.session.setdefault('username', admin['username'])
            request.session.setdefault('uid', admin['id'])
            request.session.setdefault('role', admin['role'])
            return RedirectResponse("/admin/dashboard", status_code=status.HTTP_302_FOUND)


    @router.get("/admin/dashboard", response_class=HTMLResponse)
    def dashboard(request: Request):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from products")
        products = cur.fetchall()
        con.close
        return templates.TemplateResponse("/admin/dashboard.html", {"request": request, "items": products})

    @router.get("/promo", response_class=HTMLResponse)
    def promo(request: Request):
        return templates.TemplateResponse("/admin/promo.html", {"request": request})



    @router.get("/admin/products", response_class=HTMLResponse)
    def admin_products(request: Request):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from products")
        products = cur.fetchall()
        con.close
        return templates.TemplateResponse("/admin/products.html", {"request": request, "products": products})


    @router.get("/admin/products/create", response_class=HTMLResponse)
    def admin_products_create(request: Request):
        return templates.TemplateResponse("/admin/products_create.html", {"request": request})


    @router.post("/admin/products/create", response_class=HTMLResponse)
    def admin_products_create(request: Request, pname:str = Form(...), price: str = Form(...), image: str = Form(...), details: str = Form(...), tags: str = Form(...), category:str = Form(...)):
        with sqlite3.connect(DATABASE_NAME) as con:
            cur = con.cursor()
            cur.execute("INSERT into products(name, price, details, image, tags, category) values(?, ?, ?, ?, ?, ?)",
                        (pname, price, details, image, tags, category))
            con.commit()
        return RedirectResponse("/admin/products",status_code=status.HTTP_302_FOUND)


    @router.get("/admin/orders", response_class=HTMLResponse)
    def admin_orders(request: Request):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT *, o.id as oid from users u, products p, orders o where o.uid = u.id and o.pid = p.id")
        orders = cur.fetchall()
        con.close
        return templates.TemplateResponse("/admin/orders.html", {"request": request, "orders": orders})


    @router.get("/admin/logout", response_class=HTMLResponse)
    def admin_logout(request: Request):
        return templates.TemplateResponse("/admin/logout", {"request": request})


    @router.get("/admin/products_edit/{pid}", response_class=HTMLResponse)
    def admin_product_edit(request: Request, pid: int = 0):
        return templates.TemplateResponse("/admin/products_edit.html", {"request": request})


    @router.get("/admin/products_delete/{pid}", response_class=HTMLResponse)
    def admin_product_delete(request: Request, pid: int = 0):
        return RedirectResponse("/admin/products", status_code=status.HTTP_302_FOUND)


    @router.get("/admin/orders", response_class=HTMLResponse)
    def admin_orders(request: Request):
        return templates.TemplateResponse("/admin/orders.html", {"request": request})


    @router.get("/admin/orders_view/{oid}", response_class=HTMLResponse)
    def admin_order_view(request: Request, oid: int = 0):
        return templates.TemplateResponse("/admin/orders_view.html", {"request": request})