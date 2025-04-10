#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存服务单元测试模块。
测试缓存服务功能。
"""

import pytest
import asyncio
import time
from app.services.cache_service import SimpleCache, cached


class TestSimpleCache:
    """简单缓存类测试。"""
    
    def test_cache_set_get(self):
        """测试缓存的设置和获取功能。"""
        # 创建缓存
        cache = SimpleCache(ttl=60)
        
        # 设置缓存
        cache.set("test_key", "test_value")
        
        # 获取缓存
        value = cache.get("test_key")
        
        # 断言
        assert value == "test_value"
    
    def test_cache_expiration(self):
        """测试缓存过期功能。"""
        # 创建缓存（TTL=1秒）
        cache = SimpleCache(ttl=1)
        
        # 设置缓存
        cache.set("test_key", "test_value")
        
        # 立即获取（未过期）
        value = cache.get("test_key")
        assert value == "test_value"
        
        # 等待缓存过期
        time.sleep(1.5)
        
        # 再次获取（已过期）
        value = cache.get("test_key")
        assert value is None
    
    def test_cache_custom_ttl(self):
        """测试自定义TTL功能。"""
        # 创建缓存（默认TTL=60秒）
        cache = SimpleCache(ttl=60)
        
        # 设置缓存，自定义TTL=1秒
        cache.set("test_key", "test_value", ttl=1)
        
        # 立即获取（未过期）
        value = cache.get("test_key")
        assert value == "test_value"
        
        # 等待缓存过期
        time.sleep(1.5)
        
        # 再次获取（已过期）
        value = cache.get("test_key")
        assert value is None
    
    def test_cache_delete(self):
        """测试缓存删除功能。"""
        # 创建缓存
        cache = SimpleCache()
        
        # 设置缓存
        cache.set("test_key1", "test_value1")
        cache.set("test_key2", "test_value2")
        
        # 删除单个缓存
        cache.delete("test_key1")
        
        # 断言
        assert cache.get("test_key1") is None
        assert cache.get("test_key2") == "test_value2"
    
    def test_cache_clear(self):
        """测试缓存清空功能。"""
        # 创建缓存
        cache = SimpleCache()
        
        # 设置多个缓存
        cache.set("test_key1", "test_value1")
        cache.set("test_key2", "test_value2")
        
        # 清空所有缓存
        cache.clear()
        
        # 断言
        assert cache.get("test_key1") is None
        assert cache.get("test_key2") is None


class TestCachedDecorator:
    """缓存装饰器测试。"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """测试缓存装饰器功能。"""
        # 测试计数器
        counter = 0
        
        # 定义测试函数
        @cached("test_")
        async def test_function(param):
            nonlocal counter
            counter += 1
            return f"result_{param}"
        
        # 首次调用，应该执行函数并缓存结果
        result1 = await test_function("abc")
        assert result1 == "result_abc"
        assert counter == 1
        
        # 再次调用相同参数，应该从缓存获取，不执行函数
        result2 = await test_function("abc")
        assert result2 == "result_abc"
        assert counter == 1  # 计数器未增加，说明函数未执行
        
        # 调用不同参数，应该执行函数
        result3 = await test_function("def")
        assert result3 == "result_def"
        assert counter == 2
    
    @pytest.mark.asyncio
    async def test_cached_with_multiple_args(self):
        """测试带有多个参数的缓存装饰器。"""
        # 测试计数器
        counter = 0
        
        # 定义测试函数
        @cached("multi_")
        async def test_function(arg1, arg2, kwarg1=None):
            nonlocal counter
            counter += 1
            return f"result_{arg1}_{arg2}_{kwarg1}"
        
        # 首次调用
        result1 = await test_function("a", "b", kwarg1="c")
        assert result1 == "result_a_b_c"
        assert counter == 1
        
        # 相同参数再次调用
        result2 = await test_function("a", "b", kwarg1="c")
        assert result2 == "result_a_b_c"
        assert counter == 1  # 从缓存获取，计数器未增加
        
        # 不同参数调用
        result3 = await test_function("a", "b", kwarg1="d")
        assert result3 == "result_a_b_d"
        assert counter == 2
        
        result4 = await test_function("x", "y")
        assert result4 == "result_x_y_None"
        assert counter == 3 