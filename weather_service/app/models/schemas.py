#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据模型映射模块。
定义用于API请求和响应的Pydantic模型。
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CityBase(BaseModel):
    """城市基础模型。"""
    name: str
    country: str
    latitude: float
    longitude: float


class CityCreate(CityBase):
    """创建城市请求模型。"""
    pass


class City(CityBase):
    """城市响应模型。"""
    id: int
    
    class Config:
        orm_mode = True


class WeatherData(BaseModel):
    """天气数据模型。"""
    temperature: float = Field(..., description="温度(摄氏度)")
    humidity: Optional[float] = Field(None, description="湿度(%)")
    pressure: Optional[float] = Field(None, description="气压(hPa)")
    wind_speed: Optional[float] = Field(None, description="风速(m/s)")
    wind_direction: Optional[float] = Field(None, description="风向(度)")
    weather_description: Optional[str] = Field(None, description="天气描述")
    weather_icon: Optional[str] = Field(None, description="天气图标代码")


class WeatherRecordBase(BaseModel):
    """天气记录基础模型。"""
    city_id: int
    query_time: datetime = Field(default_factory=datetime.utcnow)
    temperature: float
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    weather_description: Optional[str] = None
    weather_icon: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class WeatherRecordCreate(WeatherRecordBase):
    """创建天气记录请求模型。"""
    pass


class WeatherRecord(WeatherRecordBase):
    """天气记录响应模型。"""
    id: int
    
    class Config:
        orm_mode = True


class QueryHistoryBase(BaseModel):
    """查询历史基础模型。"""
    city_name: str
    query_time: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None


class QueryHistoryCreate(QueryHistoryBase):
    """创建查询历史请求模型。"""
    pass


class QueryHistory(QueryHistoryBase):
    """查询历史响应模型。"""
    id: int
    
    class Config:
        orm_mode = True


class WeatherResponse(BaseModel):
    """天气查询响应模型。"""
    city: str
    country: str
    coordinates: Dict[str, float]
    current_weather: WeatherData
    timestamp: datetime
    forecast: Optional[List[Dict[str, Any]]] = None


class WeatherForecastDay(BaseModel):
    """天气预报日模型。"""
    date: str
    min_temp: float
    max_temp: float
    humidity: float
    weather_description: str
    weather_icon: str


class WeatherForecastResponse(BaseModel):
    """天气预报响应模型。"""
    city: str
    country: str
    forecast: List[WeatherForecastDay] 