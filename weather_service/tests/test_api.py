#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由单元测试模块。
测试API路由功能。
"""

import pytest
import json
from unittest import mock
from datetime import datetime
from httpx import AsyncClient
from fastapi import Request, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City, QueryHistory
from app.services.weather_service import weather_service


# 模拟天气API响应数据
MOCK_CURRENT_WEATHER = {
    "coord": {"lon": 116.4074, "lat": 39.9042},
    "weather": [
        {
            "id": 800,
            "main": "Clear",
            "description": "晴天",
            "icon": "01d"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 25.5,
        "feels_like": 26.0,
        "temp_min": 23.0,
        "temp_max": 27.0,
        "pressure": 1013,
        "humidity": 80
    },
    "visibility": 10000,
    "wind": {
        "speed": 5.2,
        "deg": 180
    },
    "clouds": {
        "all": 0
    },
    "dt": 1617260400,
    "sys": {
        "type": 1,
        "id": 9609,
        "country": "CN",
        "sunrise": 1617232210,
        "sunset": 1617277867
    },
    "timezone": 28800,
    "id": 1816670,
    "name": "Beijing",
    "cod": 200
}

MOCK_FORECAST = {
    "cod": "200",
    "message": 0,
    "cnt": 40,
    "list": [
        {
            "dt": 1617260400,
            "main": {
                "temp": 25.5,
                "feels_like": 26.0,
                "temp_min": 23.0,
                "temp_max": 27.0,
                "pressure": 1013,
                "humidity": 80
            },
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "晴天",
                    "icon": "01d"
                }
            ],
            "clouds": {"all": 0},
            "wind": {"speed": 5.2, "deg": 180},
            "visibility": 10000,
            "pop": 0,
            "sys": {"pod": "d"},
            "dt_txt": "2025-04-01 12:00:00"
        },
        # 更多预报数据...
    ],
    "city": {
        "id": 1816670,
        "name": "Beijing",
        "coord": {"lat": 39.9042, "lon": 116.4074},
        "country": "CN",
        "population": 11716620,
        "timezone": 28800,
        "sunrise": 1617232210,
        "sunset": 1617277867
    }
}


@pytest.mark.asyncio
class TestWeatherAPI:
    """天气API测试类。"""
    
    @mock.patch.object(weather_service, "get_current_weather")
    async def test_get_current_weather(self, mock_get_current_weather, async_client, db):
        """
        测试获取当前天气API。
        
        Args:
            mock_get_current_weather: 模拟的天气服务方法
            async_client: 异步HTTP客户端
            db: 数据库会话
        """
        # 设置模拟返回值
        mock_get_current_weather.return_value = MOCK_CURRENT_WEATHER
        
        # 发送请求
        response = await async_client.get("/weather/current/Beijing")
        
        # 断言
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["city"] == "Beijing"
        assert data["country"] == "CN"
        assert data["current_weather"]["temperature"] == 25.5
        assert data["current_weather"]["humidity"] == 80
        assert data["current_weather"]["weather_description"] == "晴天"
        
        # 验证查询历史记录是否保存
        result = await db.execute(
            "SELECT * FROM query_history WHERE city_name = 'Beijing'"
        )
        history = result.fetchone()
        assert history is not None
    
    @mock.patch.object(weather_service, "get_weather_forecast")
    async def test_get_weather_forecast(self, mock_get_forecast, async_client, db):
        """
        测试获取天气预报API。
        
        Args:
            mock_get_forecast: 模拟的天气服务方法
            async_client: 异步HTTP客户端
            db: 数据库会话
        """
        # 设置模拟返回值
        mock_get_forecast.return_value = MOCK_FORECAST
        
        # 发送请求
        response = await async_client.get("/weather/forecast/Beijing?days=3")
        
        # 断言
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["city"] == "Beijing"
        assert data["country"] == "CN"
        assert isinstance(data["forecast"], list)
        
        # 验证查询历史记录是否保存
        result = await db.execute(
            "SELECT * FROM query_history WHERE city_name = 'Beijing'"
        )
        history = result.fetchone()
        assert history is not None
    
    async def test_query_history(self, async_client, db):
        """
        测试查询历史API。
        
        Args:
            async_client: 异步HTTP客户端
            db: 数据库会话
        """
        # 创建测试数据
        for city in ["Beijing", "Shanghai", "Guangzhou"]:
            query_history = QueryHistory(
                city_name=city,
                query_time=datetime.utcnow(),
                ip_address="127.0.0.1"
            )
            db.add(query_history)
        await db.commit()
        
        # 发送请求
        response = await async_client.get("/weather/history?limit=2")
        
        # 断言
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # 限制为2条
        assert "city_name" in data[0]
        assert "query_time" in data[0]
    
    def test_health_check(self, client):
        """
        测试健康检查API。
        
        Args:
            client: 测试客户端
        """
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy" 