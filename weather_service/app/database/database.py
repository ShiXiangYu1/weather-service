#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库连接和会话管理模块。
用于创建数据库引擎、会话等数据库相关操作。
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# 加载环境变量
load_dotenv()

# 获取数据库URL（默认为SQLite）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather_data.db")
# 对SQLite URL进行处理，支持异步操作
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    future=True,
)

# 创建会话类
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# 创建Base类，用于创建模型类
Base = declarative_base()

async def get_db() -> Generator:
    """
    获取数据库会话的依赖函数。
    
    Yields:
        Generator: 数据库会话对象
    
    示例:
        @app.get("/users/")
        async def read_users(db: AsyncSession = Depends(get_db)):
            users = await db.execute(select(User))
            return users.scalars().all()
    """
    db = SessionLocal()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close() 