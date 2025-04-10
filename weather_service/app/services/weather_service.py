#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
天气服务模块。
负责与第三方天气API交互，获取天气数据。
"""

import os
import json
import logging
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 天气API配置
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = os.getenv("WEATHER_API_BASE_URL", "https://api.openweathermap.org/data/2.5")

# 中文城市名称映射表
CHINESE_CITY_MAP = {
    "北京": "Beijing,CN",
    "上海": "Shanghai,CN",
    "广州": "Guangzhou,CN",
    "深圳": "Shenzhen,CN",
    "南京": "Nanjing,CN",
    "杭州": "Hangzhou,CN",
    "武汉": "Wuhan,CN",
    "成都": "Chengdu,CN",
    "重庆": "Chongqing,CN",
    "西安": "Xian,CN",
    "天津": "Tianjin,CN",
    "苏州": "Suzhou,CN",
    "厦门": "Xiamen,CN",
    "青岛": "Qingdao,CN",
    "大连": "Dalian,CN",
    "长沙": "Changsha,CN",
    "济南": "Jinan,CN",
    "哈尔滨": "Harbin,CN",
    "沈阳": "Shenyang,CN",
    "香港": "Hong Kong,CN",
    "澳门": "Macau,CN",
    "台北": "Taipei,TW",
    "长春": "Changchun,CN",
    "福州": "Fuzhou,CN",
    "昆明": "Kunming,CN",
    "郑州": "Zhengzhou,CN",
    "石家庄": "Shijiazhuang,CN",
    "太原": "Taiyuan,CN",
    "合肥": "Hefei,CN",
    "南昌": "Nanchang,CN",
    "南宁": "Nanning,CN",
    "兰州": "Lanzhou,CN",
    "贵阳": "Guiyang,CN",
    "海口": "Haikou,CN",
    "银川": "Yinchuan,CN",
    "西宁": "Xining,CN",
    "乌鲁木齐": "Urumqi,CN",
    "拉萨": "Lhasa,CN"
}


class WeatherService:
    """
    天气服务类，用于与第三方天气API交互。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化天气服务。
        
        Args:
            api_key: API密钥，默认从环境变量获取
            base_url: API基础URL，默认从环境变量获取
        """
        self.api_key = api_key or WEATHER_API_KEY
        self.base_url = base_url or WEATHER_API_BASE_URL
        
        if not self.api_key:
            logger.error("未提供天气API密钥")
            raise ValueError("Weather API key is required. Please set WEATHER_API_KEY in .env file.")
        
        logger.info(f"天气服务初始化成功，API基础URL: {self.base_url}")
    
    def _get_city_query(self, city: str) -> str:
        """
        获取城市查询参数，支持中文城市名称。
        
        Args:
            city: 城市名称，可以是中文
            
        Returns:
            str: 用于API查询的城市名称参数
        """
        # 先尝试直接从映射表获取
        if city in CHINESE_CITY_MAP:
            city_query = CHINESE_CITY_MAP[city]
            logger.info(f"将中文城市名'{city}'映射为'{city_query}'")
            return city_query
        
        # 检查是否已经包含国家代码
        if ',' in city:
            logger.info(f"使用带国家代码的城市名: {city}")
            return city
        
        # 对于中文城市名但不在映射表中的，尝试添加中国国家代码
        if any('\u4e00' <= char <= '\u9fff' for char in city):
            city_query = f"{city},CN"
            logger.info(f"未找到中文城市'{city}'的映射，尝试使用'{city_query}'")
            return city_query
        
        # 其他情况直接返回原名称
        logger.info(f"使用原始城市名: {city}")
        return city
    
    async def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        获取指定城市的当前天气。
        
        Args:
            city: 城市名称
            
        Returns:
            Dict[str, Any]: 天气数据字典
            
        Raises:
            HTTPException: 当API请求失败时抛出
        """
        endpoint = f"{self.base_url}/weather"
        city_query = self._get_city_query(city)
        
        params = {
            "q": city_query,
            "appid": self.api_key,
            "units": "metric",  # 使用摄氏度
            "lang": "zh_cn"     # 使用中文返回天气描述
        }
        
        logger.debug(f"请求天气数据: {endpoint} 参数: {params}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"获取天气数据成功: {data}")
                return data
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('message', '')}"
            except:
                error_msg += f" - {e.response.text}"
            
            logger.error(f"天气API请求失败: {error_msg}")
            
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"城市'{city}'未找到")
            elif e.response.status_code == 401:
                raise HTTPException(status_code=401, detail="API密钥无效或已过期")
            raise HTTPException(status_code=e.response.status_code, 
                               detail=f"天气API错误: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"网络请求错误: {str(e)}")
            raise HTTPException(status_code=503, 
                               detail=f"服务不可用。连接天气API时发生错误: {str(e)}")
        except Exception as e:
            logger.error(f"获取天气数据时发生未预期错误: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, 
                               detail=f"处理天气数据时发生错误: {str(e)}")
    
    async def get_weather_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        获取指定城市的天气预报。
        
        Args:
            city: 城市名称
            days: 预报天数，默认5天
            
        Returns:
            Dict[str, Any]: 天气预报数据字典
            
        Raises:
            HTTPException: 当API请求失败时抛出
        """
        endpoint = f"{self.base_url}/forecast"
        city_query = self._get_city_query(city)
        
        params = {
            "q": city_query,
            "appid": self.api_key,
            "units": "metric",  # 使用摄氏度
            "lang": "zh_cn",    # 使用中文返回天气描述
            "cnt": min(days * 8, 40)  # OpenWeatherMap API限制最多5天/3小时预报(每天8个数据点)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"城市'{city}'未找到")
            raise HTTPException(status_code=e.response.status_code, 
                               detail=f"天气API错误: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, 
                               detail=f"服务不可用。连接天气API时发生错误: {str(e)}")
    
    async def search_city(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索城市。
        
        Args:
            query: 城市名称查询字符串
            
        Returns:
            List[Dict[str, Any]]: 匹配的城市列表
            
        Raises:
            HTTPException: 当API请求失败时抛出
        """
        # 如果是中文城市名称，先尝试从映射表中查找
        if query in CHINESE_CITY_MAP:
            city_query = CHINESE_CITY_MAP[query]
        else:
            city_query = query
            
        # OpenWeatherMap API不提供城市搜索功能，这里使用简单的城市匹配
        # 在实际应用中，可以使用其他API或数据库来实现城市搜索
        endpoint = f"{self.base_url}/find"
        params = {
            "q": city_query,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn",
            "limit": 10
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("list", [])
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, 
                               detail=f"天气API错误: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, 
                               detail=f"服务不可用。连接天气API时发生错误: {str(e)}")


# 创建全局服务实例
weather_service = WeatherService() 