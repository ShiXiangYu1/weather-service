#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
天气数据模型模块。
定义天气数据和查询历史记录的数据模型。
"""

import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class City(Base):
    """
    城市模型，用于存储城市信息。
    """
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # 关联查询记录
    weather_records = relationship("WeatherRecord", back_populates="city")
    
    def __repr__(self) -> str:
        """返回城市实例的字符串表示"""
        return f"<City {self.name}, {self.country}>"


class WeatherRecord(Base):
    """
    天气记录模型，用于存储天气查询结果。
    """
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    query_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # 天气数据
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    weather_description = Column(String, nullable=True)
    weather_icon = Column(String, nullable=True)
    
    # 扩展天气数据（JSON格式，存储其他可能的天气数据）
    extra_data = Column(JSON, nullable=True)
    
    # 关联城市
    city = relationship("City", back_populates="weather_records")
    
    def __repr__(self) -> str:
        """返回天气记录实例的字符串表示"""
        return (f"<WeatherRecord city_id={self.city_id}, "
                f"query_time={self.query_time}, "
                f"temp={self.temperature}°C>")


class QueryHistory(Base):
    """
    查询历史模型，用于记录用户的查询操作。
    """
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False)
    query_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    
    def __repr__(self) -> str:
        """返回查询历史实例的字符串表示"""
        return f"<QueryHistory city={self.city_name}, time={self.query_time}>" 