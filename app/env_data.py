import os

from dotenv import load_dotenv

load_dotenv()


# 获取环境变量
def get_env(key):
    return os.getenv(key)
