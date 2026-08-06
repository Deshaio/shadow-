#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, BotCommandScopeDefault
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

from config import config
from handlers.commands import CommandHandlers
from handlers.callbacks import CallbackHandlers
from modules.osint import OSINTModule
from modules.payload import PayloadModule
from modules.stego import StegoModule
from modules.scanner import ScannerModule
from utils.logger import setup_logger
from utils.security import SecurityManager

# إعداد التسجيل
logger = setup_logger(__name__)

class ShadowForgeBot:
    """البوت الرئيسي"""
    
    def __init__(self):
        self.config = config
        self.security = SecurityManager(config)
        self.osint = OSINTModule(config)
        self.payload = PayloadModule(config)
        self.stego = StegoModule(config)
        self.scanner = ScannerModule(config)
        self.commands = CommandHandlers(self)
        self.callbacks = CallbackHandlers(self)
        
        self.application = None
        self.start_time = datetime.utcnow()
    
    async def setup_commands(self):
        """إعداد قائمة الأوامر"""
        commands = [
            BotCommand("start", "🚀 تشغيل البوت وعرض القائمة"),
            BotCommand("help", "❓ عرض المساعدة والأوامر المتاحة"),
            BotCommand("osint", "🔍 مسح معلومات عن نطاق أو بريد"),
            BotCommand("payload", "💉 توليد حمولة بلغة معينة"),
            BotCommand("stego", "🎨 إخفاء رسالة في صورة"),
            BotCommand("scan", "🛡️ فحص الثغرات الأمنية"),
            BotCommand("crypto", "🔐 تشفير أو فك تشفير نص"),
            BotCommand("status", "📊 عرض حالة النظام"),
            BotCommand("stats", "📈 إحصائيات استخدام البوت"),
            BotCommand("export", "📤 تصدير النتائج"),
            BotCommand("cancel", "❌ إلغاء العملية الحالية"),
        ]
        await self.application.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    
    def build_keyboard(self) -> InlineKeyboardMarkup:
        """بناء لوحة المفاتيح الرئيسية"""
        keyboard = [
            [
                InlineKeyboardButton("🔍 OSINT", callback_data="menu_osint"),
                InlineKeyboardButton("💉 Payload", callback_data="menu_payload"),
            ],
            [
                InlineKeyboardButton("🎨 Stego", callback_data="menu_stego"),
                InlineKeyboardButton("🛡️ Scan", callback_data="menu_scan"),
            ],
            [
                InlineKeyboardButton("🔐 Crypto", callback_data="menu_crypto"),
                InlineKeyboardButton("📊 Status", callback_data="menu_status"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="menu_help"),
                InlineKeyboardButton("📤 Export", callback_data="menu_export"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        welcome_text = f"""
⚡ **{config.BOT_NAME} v{config.BOT_VERSION}**
━━━━━━━━━━━━━━━━━━━━━

مرحباً {user.first_name}! 👋

أنا بوت متخصص في:
• 🕵️ استطلاع المعلومات (OSINT)
• 💉 توليد الحمولات البرمجية
• 🎨 إخفاء البيانات في الصور
• 🛡️ فحص الثغرات الأمنية
• 🔐 تشفير وفك تشفير النصوص

📌 اختر إحدى الخدمات من الأزرار أدناه.
🛡️ جميع العمليات مشفرة وآمنة.

📖 للمساعدة: /help
━━━━━━━━━━━━━━━━━━━━━
⚡ **جاهز للعمل!**
"""
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.build_keyboard(),
            parse_mode="Markdown"
        )
        
        # تسجيل المستخدم
        logger.info(f"New user: {user.id} - {user.username}")
        
        return ConversationHandler.END
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المساعدة"""
        help_text = """
❓ **دليل استخدام SHADOWFORGE**

📌 **الأوامر الأساسية:**
/start - عرض القائمة الرئيسية
/help - عرض هذه المساعدة
/cancel - إلغاء العملية الحالية

🔍 **خدمات OSINT:**
/osint domain <example.com> - مسح نطاق
/osint email <user@example.com> - بحث بريد
/osint ip <8.8.8.8> - معلومات IP

💉 **توليد الحمولات:**
/payload powershell <IP> <PORT>
/payload python <IP> <PORT>
/payload bash <IP> <PORT>

🎨 **إخفاء البيانات:**
ارسل صورة مع تعليق:
/stego encode <النص> <المفتاح>

🛡️ **فحص الثغرات:**
/scan <URL> - فحص موقع
/scan port <IP> - فحص المنافذ

🔐 **التشفير:**
/crypto encrypt <النص> <المفتاح>
/crypto decrypt <النص المشفر> <المفتاح>

⚠️ **تحذير:** استخدم هذه الأدوات فقط على أنظمتك الخاصة أو بإذن صريح!
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"Update {update} caused error: {context.error}")
        
        error_message = "⚠️ حدث خطأ ما. يرجى المحاولة مرة أخرى."
        if update and update.effective_message:
            await update.effective_message.reply_text(error_message)
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 Starting SHADOWFORGE Bot...")
        
        # إنشاء التطبيق
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        
        # إضافة المعالجات
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # أوامر الخدمات
        self.application.add_handler(CommandHandler("osint", self.commands.handle_osint))
        self.application.add_handler(CommandHandler("payload", self.commands.handle_payload))
        self.application.add_handler(CommandHandler("stego", self.commands.handle_stego))
        self.application.add_handler(CommandHandler("scan", self.commands.handle_scan))
        self.application.add_handler(CommandHandler("crypto", self.commands.handle_crypto))
        self.application.add_handler(CommandHandler("status", self.commands.handle_status))
        self.application.add_handler(CommandHandler("stats", self.commands.handle_stats))
        self.application.add_handler(CommandHandler("export", self.commands.handle_export))
        self.application.add_handler(CommandHandler("cancel", self.commands.handle_cancel))
        
        # معالجات الأزرار
        self.application.add_handler(CallbackQueryHandler(self.callbacks.handle_callback))
        
        # معالجات الملفات
        self.application.add_handler(MessageHandler(
            filters.PHOTO, self.commands.handle_image
        ))
        self.application.add_handler(MessageHandler(
            filters.Document.IMAGE, self.commands.handle_image
        ))
        
        # معالج الأخطاء
        self.application.add_error_handler(self.error_handler)
        
        # إعداد الأوامر
        asyncio.create_task(self.setup_commands())
        
        # تشغيل البوت
        logger.info("✅ Bot is running!")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "inline_query"]
        )

if __name__ == "__main__":
    bot = ShadowForgeBot()
    bot.run()