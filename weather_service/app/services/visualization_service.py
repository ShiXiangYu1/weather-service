#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据可视化服务模块。
提供天气数据的可视化功能，生成图表。
"""

import os
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题


class VisualizationService:
    """
    数据可视化服务类。
    提供各种天气数据可视化功能。
    """
    
    @staticmethod
    def generate_temperature_chart(forecast_data: List[Dict[str, Any]], 
                                  city: str) -> str:
        """
        生成温度趋势图。
        
        Args:
            forecast_data: 天气预报数据列表
            city: 城市名称
            
        Returns:
            str: Base64编码的图像数据
        """
        # 创建图形和坐标轴
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 提取日期和温度数据
        dates = []
        temps = []
        
        for item in forecast_data:
            date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
            dates.append(date)
            temps.append(item['max_temp'])
        
        # 绘制温度曲线
        ax.plot(dates, temps, 'o-', color='#FF5722', linewidth=2, markersize=8)
        
        # 设置图表标题和标签
        ax.set_title(f'{city}未来天气温度趋势', fontsize=16)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('温度 (°C)', fontsize=12)
        
        # 设置日期格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 美化图表
        plt.tight_layout()
        
        # 将图形转换为Base64编码的数据
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        # 返回Base64编码的图像数据
        return base64.b64encode(image_png).decode('utf-8')
    
    @staticmethod
    def generate_weather_dashboard(forecast_data: List[Dict[str, Any]], 
                                  city: str) -> str:
        """
        生成天气数据仪表板，包含温度、湿度等多个指标。
        
        Args:
            forecast_data: 天气预报数据列表
            city: 城市名称
            
        Returns:
            str: Base64编码的图像数据
        """
        # 创建2x2网格的图表
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # 提取数据
        dates = []
        temps_max = []
        temps_min = []
        humidity = []
        
        for item in forecast_data:
            date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
            dates.append(date)
            temps_max.append(item['max_temp'])
            temps_min.append(item['min_temp'])
            humidity.append(item['humidity'])
        
        # 1. 温度趋势图（左上）
        axs[0, 0].plot(dates, temps_max, 'o-', color='#FF5722', label='最高温度')
        axs[0, 0].plot(dates, temps_min, 'o-', color='#2196F3', label='最低温度')
        axs[0, 0].set_title(f'{city}温度趋势')
        axs[0, 0].set_ylabel('温度 (°C)')
        axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        axs[0, 0].legend()
        axs[0, 0].grid(True, linestyle='--', alpha=0.7)
        
        # 2. 湿度趋势图（右上）
        axs[0, 1].plot(dates, humidity, 'o-', color='#4CAF50')
        axs[0, 1].set_title(f'{city}湿度趋势')
        axs[0, 1].set_ylabel('湿度 (%)')
        axs[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        axs[0, 1].grid(True, linestyle='--', alpha=0.7)
        
        # 3. 温度范围柱状图（左下）
        x = np.arange(len(dates))
        width = 0.35
        date_labels = [d.strftime('%m-%d') for d in dates]
        
        temp_range = axs[1, 0].bar(x, np.array(temps_max) - np.array(temps_min), width,
                                  bottom=temps_min, color='#FF9800')
        axs[1, 0].set_title(f'{city}温度范围')
        axs[1, 0].set_ylabel('温度 (°C)')
        axs[1, 0].set_xticks(x)
        axs[1, 0].set_xticklabels(date_labels)
        axs[1, 0].grid(True, linestyle='--', alpha=0.7)
        
        # 4. 平均温度饼图（右下）
        avg_temp = sum([(max_t + min_t) / 2 for max_t, min_t in zip(temps_max, temps_min)]) / len(temps_max)
        temp_levels = ['寒冷 (<10°C)', '凉爽 (10-20°C)', '温暖 (20-30°C)', '炎热 (>30°C)']
        
        if avg_temp < 10:
            sizes = [100, 0, 0, 0]
            colors = ['#2196F3', '#BBDEFB', '#FFA726', '#FF5722']
        elif avg_temp < 20:
            sizes = [0, 100, 0, 0]
            colors = ['#2196F3', '#BBDEFB', '#FFA726', '#FF5722']
        elif avg_temp < 30:
            sizes = [0, 0, 100, 0]
            colors = ['#2196F3', '#BBDEFB', '#FFA726', '#FF5722']
        else:
            sizes = [0, 0, 0, 100]
            colors = ['#2196F3', '#BBDEFB', '#FFA726', '#FF5722']
        
        axs[1, 1].pie(sizes, labels=temp_levels, colors=colors, autopct='%1.1f%%',
                     shadow=True, startangle=90)
        axs[1, 1].set_title(f'{city}平均温度分布 ({avg_temp:.1f}°C)')
        
        # 调整布局
        plt.tight_layout()
        
        # 将图形转换为Base64编码的数据
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        # 返回Base64编码的图像数据
        return base64.b64encode(image_png).decode('utf-8')


# 创建全局可视化服务实例
visualization_service = VisualizationService() 