#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务包初始化模块。
导出服务类和实例。
"""

from .weather_service import WeatherService, weather_service
from .cache_service import SimpleCache, cache, cached
from .visualization_service import VisualizationService, visualization_service

__all__ = [
    "WeatherService", "weather_service", 
    "SimpleCache", "cache", "cached",
    "VisualizationService", "visualization_service"
] 