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

class cart:

    @router.get("/addtocart", response_class=HTMLResponse)
    async def addtocart(request: Request, pid:int = 1, qty:int = 1):
        uid = request.session.get('uid')
        with sqlite3.connect(DATABASE_NAME, check_same_thread=False) as con:
            cur = con.cursor()
            cur.execute("INSERT into carts(pid, qty, uid) values(?,?,?)",
                        (pid, qty, uid))
            con.commit()
        return RedirectResponse("/cart", status_code=status.HTTP_302_FOUND)


    @router.get("/cart", response_class=HTMLResponse)
    def cart(request: Request):
        if not request.session.get('isLogin'):
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)

        uid = request.session.get('uid')

        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT *,c.id as cid from USERS u,carts c, products p where u.id=c.uid and c.pid=p.id and c.uid =?", [uid])
        items = cur.fetchall()
        total = sum(map(lambda item: int(item['qty']) * int(item['price']), items))
        con.close
        return templates.TemplateResponse("/cart.html", {"request": request, "items": items, "total" :total})


    @router.get("/deletecart/{cid}", response_class=HTMLResponse)
    def delete_cart_item(request: Request, cid: int):
        con = sqlite3.connect(DATABASE_NAME)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("Delete from carts where id =?", [cid])
        con.commit()
        con.close
        return RedirectResponse("/cart", status_code=status.HTTP_302_FOUND)

    @router.get("/confrim", response_class=HTMLResponse)
    def confrim(request: Request,payment_id:str=""):    
        uid = request.session.get('uid')
        with sqlite3.connect(DATABASE_NAME, check_same_thread=False) as con:
            cur = con.cursor()
            print(payment_id)
            cur.execute("SELECT * from carts where uid = ? ",[uid])
            carts = cur.fetchall()
            for cart in carts:
                cur.execute("select * from products where id=?", [cart[1]])
                products = cur.fetchall()
                actual_value = int(products[0][7])
                update_stock_value = actual_value - int(cart[2])
                cur.execute("UPDATE products set stocks = ? where id=?",[update_stock_value, cart[1]])
                now = datetime.now()
                order_time = now.strftime("%d/%m/%Y %H:%M:%S")
                cur.execute("INSERT into orders(pid, qty, uid,status,date) values(?,?,?,?,?)",
                            [cart[1], cart[2], cart[3], "ORDERED", order_time])
            cur.execute("Delete from carts where uid = ? ", [uid])
            con.commit()

        return RedirectResponse("/orders", status_code=status.HTTP_302_FOUND)
