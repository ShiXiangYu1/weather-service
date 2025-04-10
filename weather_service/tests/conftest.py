#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pytest配置文件。
提供测试所需的共享组件和夹具。
"""

import os
import sys
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import FastAPI
from httpx import AsyncClient

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app
from app.models import City, WeatherRecord, QueryHistory


# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_weather_data.db"


# 创建测试数据库引擎和会话工厂
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,
    future=True,
)

TestSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=test_engine, 
    class_=AsyncSession
)


# 数据库会话夹具
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    替代get_db依赖项的异步生成器。
    
    Yields:
        AsyncSession: 数据库会话对象
    """
    db = TestSessionLocal()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


# Override app的依赖项
app.dependency_overrides[get_db] = override_get_db


# 测试客户端夹具
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    提供测试客户端。
    
    Yields:
        TestClient: FastAPI测试客户端
    """
    with TestClient(app) as client:
        yield client


# 异步测试客户端夹具
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    提供异步测试客户端。
    
    Yields:
        AsyncClient: 异步HTTP客户端
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# 数据库夹具
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供测试数据库会话并管理事务。
    
    Yields:
        AsyncSession: 数据库会话对象
    """
    # 创建测试表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 提供数据库会话
    async for session in override_get_db():
        yield session
    
    # 清理
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 夹具：示例城市数据
@pytest.fixture
async def sample_city(db: AsyncSession) -> City:
    """
    提供示例城市数据。
    
    Args:
        db: 数据库会话
        
    Returns:
        City: 示例城市对象
    """
    city = City(
        name="Beijing",
        country="CN",
        latitude=39.9042,
        longitude=116.4074
    )
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city 