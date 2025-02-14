from fastapi import FastAPI, Request, Form, status, Body, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import uvicorn
from typing import Annotated, Optional
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException
from form import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from models import engine, Article, register_collection, add_articles



STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 設定首頁
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user": user
        })

@app.post("/")
async def search_articles(
    request: Request,
    keyword: str = Form(...),
    ):
    with Session(engine) as session:
        statement = select(Article).where(Article.keyword == keyword)
        existing_articles = session.exec(statement).all()
    if existing_articles:
        articles = existing_articles
        return templates.TemplateResponse("result.html", {
        "request": request,
        "keyword": keyword,
        "articles": articles
        })
    else:
        ptt_count = add_articles()

        with Session(engine) as session:
            existing_links = {article.link for article in session.exec(select(Article)).all()}

        articles_to_insert = [
            Article(**article) for article in articles if article['link'] not in existing_links
        ]

        if articles_to_insert:
            print(articles_to_insert)
            session.add_all(articles_to_insert)
            session.commit()



@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
   return templates.TemplateResponse("login.html", {
        "request": request
        })

@app.post("/login")
async def login_form(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
    ):
    user_data = await register_collection.find_one({"username": username})

    # 避免 NoneType 錯誤
    if not user_data or "password" not in user_data:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "帳號或密碼錯誤"
        })
    
    if check_password_hash(user_data.get("password"), password):
        request.session["user"] = username
        return RedirectResponse(url="/welcome", status_code=302)
        
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "帳號或密碼錯誤"
    })

@app.get("/logout")
def signout(request: Request):
    request.session.pop("user", None)  
    return RedirectResponse(url="/")

@app.get("/register", response_class=HTMLResponse)
async def login_page(request: Request):
   return templates.TemplateResponse("register.html", {
        "request": request
        })

@app.post("/register")
async def register_form(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    gender: str = Form(None),
    age: Optional[int] = Form(None),  # 使用 Optional[int] 因為這是可選的
    country: str = Form(None),
    location: str = Form(None),
    education: str = Form(None),
    ):
    
    password_hash = generate_password_hash(password)

    user_data =  RegisterForm(
        username=username,
        email=email,
        password=password_hash,
        gender=gender,
        age=age,
        country=country,
        location=location,
        education=education,
    )

    # 使用 `dict()` 轉換為可存入 MongoDB 的字典
    new_user = user_data.model_dump()

    result = await register_collection.insert_one(new_user)   

    return RedirectResponse(url="/register_success", status_code=302)

@app.get("/register_success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/welcome")
async def member_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)  
    return templates.TemplateResponse("welcome.html", {
        "request": request, 
        "user": user
        })

@app.get("/dashboard")
async def member_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)  
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user
        })


if __name__ == '__main__':
    uvicorn.run("main:app", reload = True)