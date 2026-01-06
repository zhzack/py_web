from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # 引入 declarative_base
from app.core.config.config import settings  # 建议使用绝对路径 app.

# 1. 创建引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True
)

# 2. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建模型基类 (所有的 ORM 模型如 Vehicle 都要继承这个 Base)
Base = declarative_base()

# 4. 获取数据库会话的依赖项
def get_db():
    db = SessionLocal() # 注意这里：实例化会话，而不是 yield 工厂本身
    try:
        yield db
    finally:
        db.close()