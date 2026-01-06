# app/database/base.py

# 导入基类
from app.database.base_class import Base  

# 导入所有模型，确保 SQLAlchemy 能识别到它们
from app.models.vehicle import Vehicle  # 替换成你实际的模型路径
# from app.models.user import User      # 未来如果有用户表也写在这里