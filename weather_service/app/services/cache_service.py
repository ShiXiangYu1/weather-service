#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存服务模块。
提供内存缓存功能，缓存天气数据，减少API调用。
"""

import os
import time
import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 缓存过期时间，默认30分钟
CACHE_TTL = int(os.getenv("CACHE_TTL", 1800))


class SimpleCache:
    """
    简单内存缓存类。
    用于存储API响应数据，减少API调用次数。
    """
    
    def __init__(self, ttl: int = CACHE_TTL):
        """
        初始化缓存。
        
        Args:
            ttl: 缓存过期时间（秒），默认30分钟
        """
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据。
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存数据，如果不存在或已过期则返回None
        """
        if key not in self.cache:
            return None
            
        cache_item = self.cache[key]
        if time.time() > cache_item["expires"]:
            # 缓存已过期，删除并返回None
            del self.cache[key]
            return None
            
        return cache_item["data"]
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存数据。
        
        Args:
            key: 缓存键
            data: 缓存数据
            ttl: 缓存过期时间（秒），默认使用全局TTL
        """
        expires = time.time() + (ttl if ttl is not None else self.ttl)
        self.cache[key] = {
            "data": data,
            "expires": expires
        }
    
    def delete(self, key: str) -> None:
        """
        删除缓存数据。
        
        Args:
            key: 缓存键
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """清空所有缓存数据。"""
        self.cache.clear()


# 创建全局缓存实例
cache = SimpleCache()


def cached(key_prefix: str, ttl: Optional[int] = None):
    """
    缓存装饰器，用于缓存函数返回值。
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 缓存过期时间（秒），默认使用全局TTL
        
    Returns:
        Callable: 装饰器函数
    
    使用示例：
        @cached("weather_current_")
        async def get_current_weather(city: str):
            # 函数实现
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存键
            key_parts = [key_prefix]
            # 添加位置参数
            key_parts.extend([str(arg) for arg in args if not callable(arg)])
            # 添加关键字参数
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = "_".join(key_parts)
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # 缓存未命中，调用原函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, result, ttl)
            return result
            
        return wrapper
    return decorator 