#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由包初始化模块。
导出所有API路由。
"""

from .weather import router as weather_router

__all__ = ["weather_router"] 