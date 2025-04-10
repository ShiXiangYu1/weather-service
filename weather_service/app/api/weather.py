#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
天气API路由模块。
提供天气查询相关的API接口。
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
import logging
import traceback

from ..database import get_db
from ..models import City, WeatherRecord, QueryHistory
from ..models.schemas import (
    WeatherResponse, WeatherForecastResponse, WeatherForecastDay, 
    QueryHistory as QueryHistorySchema
)
from ..services import (
    weather_service, cached, visualization_service
)
from app.services.weather_service import WeatherService


router = APIRouter(
    prefix="/weather",
    tags=["weather"],
)

# 配置日志
logger = logging.getLogger(__name__)


def get_weather_service():
    """
    依赖注入：获取天气服务实例。
    
    Returns:
        WeatherService: 天气服务实例
    """
    return WeatherService()


@router.get("/current/{city}", response_model=WeatherResponse)
@cached("current_weather_")
async def get_current_weather(
    city: str, 
    db: AsyncSession = Depends(get_db),
    request: Request = None,
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    获取指定城市的当前天气。
    
    Args:
        city: 城市名称
        db: 数据库会话
        request: 请求对象
        weather_service: 天气服务实例
        
    Returns:
        WeatherResponse: 天气数据响应
    """
    client_ip = request.client.host if request else "未知"
    logger.info(f"收到查询当前天气请求: 城市={city}, 客户端IP={client_ip}")
    
    try:
        # 调用天气服务获取数据
        weather_data = await weather_service.get_current_weather(city)
        logger.info(f"成功获取{city}的天气数据")
        
        # 记录查询历史
        query_history = QueryHistory(
            city_name=city,
            query_time=datetime.utcnow(),
            ip_address=client_ip
        )
        db.add(query_history)
        await db.commit()
        
        # 准备响应数据
        current_weather = {
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "wind_speed": weather_data["wind"]["speed"],
            "wind_direction": weather_data["wind"]["deg"],
            "weather_description": weather_data["weather"][0]["description"],
            "weather_icon": weather_data["weather"][0]["icon"]
        }
        
        return {
            "city": weather_data["name"],
            "country": weather_data["sys"]["country"],
            "coordinates": {
                "lat": weather_data["coord"]["lat"],
                "lon": weather_data["coord"]["lon"]
            },
            "current_weather": current_weather,
            "timestamp": datetime.fromtimestamp(weather_data["dt"])
        }
    except HTTPException as e:
        # 记录请求失败
        logger.error(f"获取'{city}'的当前天气数据失败: {e.detail}")
        # 重新抛出异常让FastAPI处理
        raise
    except KeyError as e:
        # 记录键错误
        error_msg = f"处理城市'{city}'的天气数据时发生键错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        # 记录未预期的错误
        error_msg = f"处理城市'{city}'的天气请求时发生未预期错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        tb = traceback.format_exc()
        logger.error(f"异常堆栈: {tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/forecast/{city}", response_model=WeatherForecastResponse)
@cached("forecast_")
async def get_weather_forecast(
    city: str, 
    days: int = Query(5, ge=1, le=5, description="预报天数，最多5天"),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    获取指定城市的天气预报。
    
    Args:
        city: 城市名称
        days: 预报天数，默认5天，最多5天
        db: 数据库会话
        request: 请求对象
        weather_service: 天气服务实例
        
    Returns:
        WeatherForecastResponse: 天气预报响应
    """
    client_ip = request.client.host if request else "未知"
    logger.info(f"收到查询天气预报请求: 城市={city}, 天数={days}, 客户端IP={client_ip}")
    
    try:
        # 调用天气服务获取数据
        forecast_data = await weather_service.get_weather_forecast(city, days)
        
        # 记录查询历史
        query_history = QueryHistory(
            city_name=city,
            query_time=datetime.utcnow(),
            ip_address=client_ip
        )
        db.add(query_history)
        await db.commit()
        
        # 处理预报数据
        forecast_list = forecast_data["list"]
        
        # 按天分组
        daily_forecasts = {}
        for item in forecast_list:
            # 提取日期（只保留年月日）
            date_str = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "min_temp": float('inf'),
                    "max_temp": float('-inf'),
                    "humidity": [],
                    "weather_descriptions": [],
                    "weather_icons": []
                }
            
            daily_forecasts[date_str]["min_temp"] = min(
                daily_forecasts[date_str]["min_temp"], 
                item["main"]["temp_min"]
            )
            daily_forecasts[date_str]["max_temp"] = max(
                daily_forecasts[date_str]["max_temp"], 
                item["main"]["temp_max"]
            )
            daily_forecasts[date_str]["humidity"].append(item["main"]["humidity"])
            daily_forecasts[date_str]["weather_descriptions"].append(
                item["weather"][0]["description"]
            )
            daily_forecasts[date_str]["weather_icons"].append(
                item["weather"][0]["icon"]
            )
        
        # 转换为响应格式
        forecast = []
        for date_str, data in daily_forecasts.items():
            # 选择出现次数最多的天气描述和图标
            from collections import Counter
            descriptions_counter = Counter(data["weather_descriptions"])
            icons_counter = Counter(data["weather_icons"])
            
            forecast.append(
                WeatherForecastDay(
                    date=date_str,
                    min_temp=data["min_temp"],
                    max_temp=data["max_temp"],
                    humidity=sum(data["humidity"]) / len(data["humidity"]),
                    weather_description=descriptions_counter.most_common(1)[0][0],
                    weather_icon=icons_counter.most_common(1)[0][0]
                )
            )
        
        # 按日期排序
        forecast.sort(key=lambda x: x.date)
        
        return {
            "city": forecast_data["city"]["name"],
            "country": forecast_data["city"]["country"],
            "forecast": forecast[:days]  # 限制天数
        }
    except HTTPException as e:
        # 记录请求失败
        logger.error(f"获取'{city}'的天气预报数据失败: {e.detail}")
        # 重新抛出异常让FastAPI处理
        raise
    except KeyError as e:
        # 记录键错误
        error_msg = f"处理城市'{city}'的天气预报数据时发生键错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        # 记录未预期的错误
        error_msg = f"处理城市'{city}'的天气预报请求时发生未预期错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        tb = traceback.format_exc()
        logger.error(f"异常堆栈: {tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/visualization/temperature/{city}")
@cached("viz_temp_")
async def get_temperature_chart(
    city: str,
    days: int = Query(5, ge=1, le=5, description="预报天数，最多5天"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定城市的温度趋势图。
    
    Args:
        city: 城市名称
        days: 预报天数，默认5天，最多5天
        db: 数据库会话
        
    Returns:
        Dict: 包含Base64编码图像的响应
    """
    try:
        # 获取天气预报数据
        forecast_data = await weather_service.get_weather_forecast(city, days)
        
        # 处理预报数据
        forecast_list = forecast_data["list"]
        
        # 按天分组
        daily_forecasts = {}
        for item in forecast_list:
            # 提取日期（只保留年月日）
            date_str = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "min_temp": float('inf'),
                    "max_temp": float('-inf'),
                    "humidity": [],
                }
            
            daily_forecasts[date_str]["min_temp"] = min(
                daily_forecasts[date_str]["min_temp"], 
                item["main"]["temp_min"]
            )
            daily_forecasts[date_str]["max_temp"] = max(
                daily_forecasts[date_str]["max_temp"], 
                item["main"]["temp_max"]
            )
            daily_forecasts[date_str]["humidity"].append(item["main"]["humidity"])
        
        # 转换为可视化服务需要的格式
        viz_data = []
        for date_str, data in daily_forecasts.items():
            viz_data.append({
                "date": date_str,
                "min_temp": data["min_temp"],
                "max_temp": data["max_temp"],
                "humidity": sum(data["humidity"]) / len(data["humidity"])
            })
        
        # 按日期排序
        viz_data.sort(key=lambda x: x["date"])
        
        # 生成图表
        chart_data = visualization_service.generate_temperature_chart(
            viz_data[:days], forecast_data["city"]["name"]
        )
        
        return {
            "city": forecast_data["city"]["name"],
            "country": forecast_data["city"]["country"],
            "chart": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成温度趋势图失败: {str(e)}")


@router.get("/visualization/dashboard/{city}")
@cached("viz_dashboard_")
async def get_weather_dashboard(
    city: str,
    days: int = Query(5, ge=1, le=5, description="预报天数，最多5天"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定城市的天气仪表板。
    
    Args:
        city: 城市名称
        days: 预报天数，默认5天，最多5天
        db: 数据库会话
        
    Returns:
        Dict: 包含Base64编码图像的响应
    """
    try:
        # 获取天气预报数据
        forecast_data = await weather_service.get_weather_forecast(city, days)
        
        # 处理预报数据
        forecast_list = forecast_data["list"]
        
        # 按天分组
        daily_forecasts = {}
        for item in forecast_list:
            # 提取日期（只保留年月日）
            date_str = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "min_temp": float('inf'),
                    "max_temp": float('-inf'),
                    "humidity": [],
                }
            
            daily_forecasts[date_str]["min_temp"] = min(
                daily_forecasts[date_str]["min_temp"], 
                item["main"]["temp_min"]
            )
            daily_forecasts[date_str]["max_temp"] = max(
                daily_forecasts[date_str]["max_temp"], 
                item["main"]["temp_max"]
            )
            daily_forecasts[date_str]["humidity"].append(item["main"]["humidity"])
        
        # 转换为可视化服务需要的格式
        viz_data = []
        for date_str, data in daily_forecasts.items():
            viz_data.append({
                "date": date_str,
                "min_temp": data["min_temp"],
                "max_temp": data["max_temp"],
                "humidity": sum(data["humidity"]) / len(data["humidity"])
            })
        
        # 按日期排序
        viz_data.sort(key=lambda x: x["date"])
        
        # 生成图表
        dashboard_data = visualization_service.generate_weather_dashboard(
            viz_data[:days], forecast_data["city"]["name"]
        )
        
        return {
            "city": forecast_data["city"]["name"],
            "country": forecast_data["city"]["country"],
            "dashboard": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成天气仪表板失败: {str(e)}")


@router.get("/history", response_model=List[QueryHistorySchema])
async def get_query_history(
    limit: int = Query(10, ge=1, le=100, description="查询历史记录数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取天气查询历史记录。
    
    Args:
        limit: 历史记录数量限制，默认10条，最多100条
        db: 数据库会话
        
    Returns:
        List[QueryHistorySchema]: 查询历史记录列表
    """
    try:
        # 查询历史记录
        result = await db.execute(
            select(QueryHistory)
            .order_by(QueryHistory.query_time.desc())
            .limit(limit)
        )
        
        query_history = result.scalars().all()
        return query_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取查询历史记录失败: {str(e)}") 