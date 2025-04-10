#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型包初始化模块。
导出所有数据模型类。
"""

from .weather import City, WeatherRecord, QueryHistory

__all__ = ["City", "WeatherRecord", "QueryHistory"] 