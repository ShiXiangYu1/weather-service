#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用主入口模块。
配置并启动FastAPI应用。
"""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from .api import weather_router
from .database import get_db, Base, engine

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="天气查询服务",
    description="提供城市天气查询、历史记录保存和数据可视化功能的API服务",
    version="0.1.0",
)

# 添加路由
app.include_router(weather_router)

# 配置静态文件
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置模板
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件。
    创建数据库表。
    """
    try:
        # 创建所有表
        async with engine.begin() as conn:
            # 如果需要清除所有表，取消注释下一行
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件。
    关闭数据库连接。
    """
    try:
        await engine.dispose()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    应用根路由，返回HTML页面。
    
    Args:
        request: 请求对象
        
    Returns:
        HTMLResponse: HTML响应
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    健康检查接口。
    
    Returns:
        dict: 状态信息
    """
    return {"status": "healthy", "message": "Service is running"}


# 错误处理
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器。
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: 错误响应
    """
    logger.error(f"Uncaught exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"}
    ) 