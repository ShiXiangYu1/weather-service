"""
Vercel部署入口文件
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入FastAPI应用
from weather_service.app.main import app 