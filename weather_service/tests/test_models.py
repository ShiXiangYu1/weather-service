#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据模型单元测试模块。
测试数据库模型的功能和关系。
"""

import pytest
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City, WeatherRecord, QueryHistory


class TestCityModel:
    """城市模型测试类。"""
    
    @pytest.mark.asyncio
    async def test_create_city(self, db: AsyncSession):
        """
        测试创建城市记录。
        
        Args:
            db: 数据库会话
        """
        # 创建城市
        city = City(
            name="Shanghai",
            country="CN",
            latitude=31.2304,
            longitude=121.4737
        )
        db.add(city)
        await db.commit()
        
        # 查询城市
        result = await db.execute(select(City).where(City.name == "Shanghai"))
        db_city = result.scalars().first()
        
        # 断言
        assert db_city is not None
        assert db_city.name == "Shanghai"
        assert db_city.country == "CN"
        assert db_city.latitude == 31.2304
        assert db_city.longitude == 121.4737
    
    @pytest.mark.asyncio
    async def test_city_repr(self, sample_city: City):
        """
        测试城市模型的__repr__方法。
        
        Args:
            sample_city: 示例城市对象
        """
        # 断言
        assert repr(sample_city) == "<City Beijing, CN>"


class TestWeatherRecordModel:
    """天气记录模型测试类。"""
    
    @pytest.mark.asyncio
    async def test_create_weather_record(self, sample_city: City, db: AsyncSession):
        """
        测试创建天气记录。
        
        Args:
            sample_city: 示例城市对象
            db: 数据库会话
        """
        # 创建天气记录
        weather_record = WeatherRecord(
            city_id=sample_city.id,
            temperature=25.5,
            humidity=80.0,
            pressure=1013.0,
            wind_speed=5.2,
            wind_direction=180.0,
            weather_description="晴天",
            weather_icon="01d",
            extra_data={"feels_like": 26.0}
        )
        db.add(weather_record)
        await db.commit()
        
        # 查询天气记录
        result = await db.execute(
            select(WeatherRecord).where(WeatherRecord.city_id == sample_city.id)
        )
        db_record = result.scalars().first()
        
        # 断言
        assert db_record is not None
        assert db_record.temperature == 25.5
        assert db_record.humidity == 80.0
        assert db_record.pressure == 1013.0
        assert db_record.wind_speed == 5.2
        assert db_record.wind_direction == 180.0
        assert db_record.weather_description == "晴天"
        assert db_record.weather_icon == "01d"
        assert db_record.extra_data["feels_like"] == 26.0
    
    @pytest.mark.asyncio
    async def test_weather_record_relationship(self, sample_city: City, db: AsyncSession):
        """
        测试天气记录与城市的关系。
        
        Args:
            sample_city: 示例城市对象
            db: 数据库会话
        """
        # 创建天气记录
        weather_record = WeatherRecord(
            city_id=sample_city.id,
            temperature=25.5,
            humidity=80.0
        )
        db.add(weather_record)
        await db.commit()
        await db.refresh(weather_record)
        
        # 查询天气记录和关联的城市
        result = await db.execute(
            select(WeatherRecord).where(WeatherRecord.city_id == sample_city.id)
        )
        db_record = result.scalars().first()
        
        # 断言
        assert db_record is not None
        assert db_record.city.id == sample_city.id
        assert db_record.city.name == "Beijing"
    
    @pytest.mark.asyncio
    async def test_weather_record_repr(self, sample_city: City, db: AsyncSession):
        """
        测试天气记录模型的__repr__方法。
        
        Args:
            sample_city: 示例城市对象
            db: 数据库会话
        """
        # 创建天气记录
        weather_record = WeatherRecord(
            city_id=sample_city.id,
            temperature=25.5,
            query_time=datetime.datetime(2025, 4, 1, 12, 0, 0)
        )
        db.add(weather_record)
        await db.commit()
        await db.refresh(weather_record)
        
        # 断言
        expected_repr = f"<WeatherRecord city_id={sample_city.id}, query_time=2025-04-01 12:00:00, temp=25.5°C>"
        assert repr(weather_record) == expected_repr


class TestQueryHistoryModel:
    """查询历史模型测试类。"""
    
    @pytest.mark.asyncio
    async def test_create_query_history(self, db: AsyncSession):
        """
        测试创建查询历史记录。
        
        Args:
            db: 数据库会话
        """
        # 创建查询历史
        query_time = datetime.datetime(2025, 4, 1, 12, 0, 0)
        query_history = QueryHistory(
            city_name="Guangzhou",
            query_time=query_time,
            ip_address="127.0.0.1"
        )
        db.add(query_history)
        await db.commit()
        
        # 查询历史记录
        result = await db.execute(
            select(QueryHistory).where(QueryHistory.city_name == "Guangzhou")
        )
        db_history = result.scalars().first()
        
        # 断言
        assert db_history is not None
        assert db_history.city_name == "Guangzhou"
        assert db_history.query_time == query_time
        assert db_history.ip_address == "127.0.0.1"
    
    @pytest.mark.asyncio
    async def test_query_history_repr(self, db: AsyncSession):
        """
        测试查询历史模型的__repr__方法。
        
        Args:
            db: 数据库会话
        """
        # 创建查询历史
        query_time = datetime.datetime(2025, 4, 1, 12, 0, 0)
        query_history = QueryHistory(
            city_name="Shenzhen",
            query_time=query_time
        )
        db.add(query_history)
        await db.commit()
        await db.refresh(query_history)
        
        # 断言
        expected_repr = f"<QueryHistory city=Shenzhen, time=2025-04-01 12:00:00>"
        assert repr(query_history) == expected_repr 