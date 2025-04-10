"""
Vercel部署入口文件
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 导入FastAPI应用
    from weather_service.app.main import app
    
    # 处理缺少数据可视化依赖
    def replace_visualization_routes():
        """
        替换需要数据可视化库的路由为简化版本
        """
        from fastapi import APIRouter, HTTPException
        
        # 查找并移除可视化相关路由
        for route in list(app.routes):
            if 'visualization' in str(route.path):
                app.routes.remove(route)
        
        # 添加一个简单的替代路由
        @app.get("/weather/visualization/{city}")
        async def visualization_placeholder(city: str):
            return {
                "message": "数据可视化功能在Vercel环境不可用",
                "city": city,
                "suggestion": "请使用本地开发环境体验完整功能"
            }
    
    # 检查是否在Vercel环境
    if os.environ.get("VERCEL") == "1":
        replace_visualization_routes()
        
except ImportError as e:
    # 导入失败时的备用处理
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="天气查询服务(简化版)")
    
    @app.get("/")
    async def root():
        return {"message": "天气查询服务简化版，部分功能不可用"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "environment": "vercel-minimal"} 