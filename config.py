import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # توكن البوت
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    
    # مفاتيح APIs
    SHODAN_KEY: str = os.getenv("SHODAN_KEY", "")
    VIRUSTOTAL_KEY: str = os.getenv("VIRUSTOTAL_KEY", "")
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")
    
    # إعدادات قاعدة البيانات
    DB_URL: str = os.getenv("DB_URL", "sqlite:///shadowforge.db")
    
    # إعدادات Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # إعدادات الأمان
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "ShadowForge2026!")
    ADMIN_IDS: list = [int(id) for id in os.getenv("ADMIN_IDS", "123456789").split(",")]
    
    # حدود الاستخدام
    RATE_LIMIT: int = 30  # طلب لكل دقيقة
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 ميجابايت
    
    # إعدادات البوت
    BOT_NAME: str = "SHADOWFORGE"
    BOT_VERSION: str = "1.0.0"

config = Config()