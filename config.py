import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # توكن البوت
    BOT_TOKEN: str = os.getenv("8612405152:AAHPYCsDU_Sb0iPkHXz7H70APGd0DH7GM5Y", "8612405152:AAHPYCsDU_Sb0iPkHXz7H70APGd0DH7GM5Y")
    
    # مفاتيح APIs
    SHODAN_KEY: str = os.getenv("P1bcK1jFbmlR5LdZ7XP5hNKIoyUbaccu", "")
    VIRUSTOTAL_KEY: str = os.getenv("2ce8a1e3ac62580f7a47a7baf7c60d4062ebc88b40478572ae32c57af490953e", "")
    HUNTER_API_KEY: str = os.getenv("19b91db1f4743af3e8acaa98a9e29ec1bd96d5c0", "")
    
    # إعدادات قاعدة البيانات
    DB_URL: str = os.getenv("DB_URL", "sqlite:///shadowforge.db")
    
    # إعدادات Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # إعدادات الأمان
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "ShadowForge2026!")
    ADMIN_IDS: list = [int(id) for id in os.getenv("ADMIN_IDS", "6103683921").split(",")]
    
    # حدود الاستخدام
    RATE_LIMIT: int = 30  # طلب لكل دقيقة
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 ميجابايت
    
    # إعدادات البوت
    BOT_NAME: str = "SHADOWFORGE"
    BOT_VERSION: str = "1.0.0"

config = Config()
