import motor.motor_asyncio
import os
from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()  # 讀取 .env 檔案
MONGODB_URL = os.getenv("MONGODB_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.travelWebDB
register_collection = db.get_collection("travel_web_users")



print("✅ 成功連線到 MongoDB")

MySQL_DB_URL = os.getenv("MySQL_DB_URL")
engine = create_engine(MySQL_DB_URL)

# 初始化資料表
SQLModel.metadata.create_all(engine)

class Article(SQLModel, table=True):
    __tablename__ = 'articles'

    # columns
    id: int = Field(default=None, primary_key=True)
    source: str = Field(max_length=64, index=False, nullable=False)
    link: str = Field(max_length=255, unique=True, nullable=False)
    keyword: str = Field(max_length=255, unique=False, nullable=False)
    introduction: str | None = Field(default=None, nullable=True)  # 使用 | None 表示可以是空值
    title: str = Field(max_length=255, unique=True, index=True, nullable=False)
    author: str | None = Field(default=None, nullable=True)  # 這個欄位是可選的
    count: int = Field(default=1)  # 預設值為 1

    # 防止重複定義資料表
    __table_args__ = {'extend_existing': True}

def add_articles(articles):
    """將文章寫入資料庫，並回傳每項文章來源的數量"""
    try:
        count = 0
        for article in articles:
            count += 1
            with Session(engine) as session:
                statement = select(Article).where(Article.title == article.get('title'))
                existing_article = session.exec(statement).first()
            if existing_article:
                existing_article.count += 1
                print(f"Increment count for existing article: {existing_article.title}")
            else:
                insert_article = Article(
                    source=article.get('source'),
                    link=article.get('link'),
                    title=article.get('title'),
                    author=article.get("author"),
                    introduction=article.get("introduction"),
                    keyword=article.get("keyword")
                )
                with Session(engine) as session:
                    session.add(insert_article)
                    session.commit()
        return count
    except IntegrityError as e:
        print(f"Roll back due to {e}")
    except Exception as e:
        print(f"Unexpected error occured: {e}")