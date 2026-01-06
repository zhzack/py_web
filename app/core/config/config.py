from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Union, Any

class Settings(BaseSettings):
    # --- 基础配置 ---
    PROJECT_NAME: str = "Vehicle Management System"
    VERSION: str = "1.0.0"
    # 新增 DEBUG 字段，匹配你 .env 中的 DEBUG=True
    DEBUG: bool = Field(default=False)
    
    # --- 数据库配置 ---
    # 使用 Field 可以在 .env 缺失时提供默认值，避免程序崩溃
    MYSQL_SERVER: str = Field(default="127.0.0.1")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str
    MYSQL_DB: str

    # --- 跨域设置 ---
    BACKEND_CORS_ORIGINS: Union[List[str], str] = []

    # 自动解析跨域字符串为列表
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    model_config = SettingsConfigDict(
        # 建议写绝对路径或确保 .env 在根目录
        env_file=".env",           
        env_file_encoding="utf-8", 
        case_sensitive=True,       
        extra="ignore"             
    )

settings = Settings()