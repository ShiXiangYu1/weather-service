#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用启动脚本。
使用uvicorn启动FastAPI应用。
"""

import os
import argparse
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def main():
    """
    应用入口函数。
    解析命令行参数并启动应用。
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="天气查询服务启动脚本")
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="服务器主机IP (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="服务器端口 (默认: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="启用热重载 (开发模式)"
    )
    args = parser.parse_args()

    # 启动应用
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main() 