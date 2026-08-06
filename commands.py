import json
import base64
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.formatter import format_result, format_error
from utils.security import SecurityManager

class CommandHandlers:
    """معالج أوامر البوت"""
    
    def __init__(self, bot):
        self.bot = bot
        self.security = SecurityManager(bot.config)
    
    async def handle_osint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر OSINT"""
        args = context.args
        if not args:
            await update.message.reply_text(
                "🔍 **استخدام أمر OSINT:**\n"
                "`/osint domain example.com`\n"
                "`/osint email user@example.com`\n"
                "`/osint ip 8.8.8.8`\n\n"
                "📌 اختر نوع المسح:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🌐 Domain", callback_data="osint_domain"),
                        InlineKeyboardButton("📧 Email", callback_data="osint_email"),
                    ],
                    [
                        InlineKeyboardButton("📍 IP", callback_data="osint_ip"),
                        InlineKeyboardButton("🔗 URL", callback_data="osint_url"),
                    ]
                ])
            )
            return
        
        # تنفيذ المسح
        target_type = args[0].lower()
        target = " ".join(args[1:]) if len(args) > 1 else ""
        
        if not target:
            await update.message.reply_text("⚠️ يرجى تحديد الهدف للمسح.")
            return
        
        await update.message.reply_text(f"⏳ جاري مسح {target}...")
        
        try:
            if target_type == "domain":
                result = await self.bot.osint.scan_domain(target)
            elif target_type == "email":
                result = await self.bot.osint.scan_email(target)
            elif target_type == "ip":
                result = await self.bot.osint.scan_ip(target)
            else:
                await update.message.reply_text("⚠️ نوع غير معروف. استخدم: domain, email, أو ip")
                return
            
            # تنسيق النتيجة
            formatted = format_result(result, target_type)
            await update.message.reply_text(formatted, parse_mode="Markdown")
            
            # خيار التصدير
            keyboard = [[
                InlineKeyboardButton("📤 تصدير النتائج", callback_data=f"export_{target_type}_{target}")
            ]]
            await update.message.reply_text(
                "✅ اكتمل المسح!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(format_error(e))
    
    async def handle_payload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج توليد الحمولات"""
        args = context.args
        
        if len(args) < 3:
            await update.message.reply_text(
                "💉 **توليد حمولة:**\n"
                "`/payload powershell 192.168.1.100 4444`\n"
                "`/payload python 10.0.0.1 5555`\n"
                "`/payload bash 172.16.0.1 6666`\n\n"
                "📌 اختر اللغة:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🪟 PowerShell", callback_data="payload_powershell"),
                        InlineKeyboardButton("🐍 Python", callback_data="payload_python"),
                    ],
                    [
                        InlineKeyboardButton("🐧 Bash", callback_data="payload_bash"),
                        InlineKeyboardButton("☕ Java", callback_data="payload_java"),
                    ]
                ])
            )
            return
        
        language = args[0].lower()
        ip = args[1]
        port = args[2]
        
        # التحقق من صحة IP والمنفذ
        if not self.security.validate_ip(ip) or not self.security.validate_port(port):
            await update.message.reply_text("⚠️ IP أو منفذ غير صالح.")
            return
        
        await update.message.reply_text(f"⏳ جاري توليد حمولة {language}...")
        
        try:
            payload = await self.bot.payload.generate(language, ip, port)
            
            # تشفير الحمولة
            encrypted = self.security.encrypt(payload)
            
            # إرسال النتيجة
            message = f"""
💉 **حمولة {language.upper()}**
━━━━━━━━━━━━━━━━━━━━━
**الهدف:** `{ip}:{port}`
**الحجم:** {len(payload)} بايت
**مشفر:** ✅

**الكود:**
```{language}
{payload[:500]}{'...' if len(payload) > 500 else ''}
        # إرسال الملف
        
        with open(f"/tmp/payload_{language}_{ip}_{port}.txt", "w") as f:
            f.write(payload)
        
        await update.message.reply_document(
            document=open(f"/tmp/payload_{language}_{ip}_{port}.txt", "rb"),
            filename=f"payload_{language}.txt",
            caption="📦 حمولة جاهزة للاستخدام"
        )
        
    except Exception as e:
        await update.message.reply_text(format_error(e))

async def handle_stego(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إخفاء البيانات"""
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "🎨 **إخفاء رسالة في صورة:**\n"
            "1. استخدم الأمر: `/stego encode <الرسالة> <المفتاح>`\n"
            "2. ثم أرفق الصورة\n\n"
            "مثال: `/stego encode 'رسالة سرية' مفتاح123`\n\n"
            "أو استخدم الأزرار:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔒 Encode", callback_data="stego_encode"),
                    InlineKeyboardButton("🔓 Decode", callback_data="stego_decode"),
                ]
            ])
        )
        return
    
    action = args[0].lower()
    data = " ".join(args[1:])
    
    context.user_data['stego_action'] = action
    context.user_data['stego_data'] = data
    
    await update.message.reply_text(
        f"📤 الآن أرسل الصورة (PNG أو JPG)\n"
        f"البيانات: `{data}`\n\n"
        "⏳ في انتظار الصورة...",
        parse_mode="Markdown"
    )

async def handle_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج فحص الثغرات"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "🛡️ **فحص الثغرات الأمنية:**\n"
            "`/scan https://example.com` - فحص موقع\n"
            "`/scan port 8.8.8.8` - فحص المنافذ\n"
            "`/scan vuln 192.168.1.1` - فحص الثغرات\n\n"
            "اختر نوع الفحص:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌐 Website", callback_data="scan_web"),
                    InlineKeyboardButton("🔌 Ports", callback_data="scan_ports"),
                ],
                [
                    InlineKeyboardButton("🛡️ Vuln", callback_data="scan_vuln"),
                    InlineKeyboardButton("📡 Subdomain", callback_data="scan_subdomain"),
                ]
            ])
        )
        return
    
    scan_type = args[0].lower()
    target = " ".join(args[1:]) if len(args) > 1 else ""
    
    if not target:
        await update.message.reply_text("⚠️ يرجى تحديد الهدف.")
        return
    
    await update.message.reply_text(f"🔍 جاري فحص {target}...")
    
    try:
        if scan_type == "web":
            result = await self.bot.scanner.scan_website(target)
        elif scan_type == "port":
            result = await self.bot.scanner.scan_ports(target)
        elif scan_type == "vuln":
            result = await self.bot.scanner.scan_vulnerabilities(target)
        elif scan_type == "subdomain":
            result = await self.bot.scanner.enumerate_subdomains(target)
        else:
            await update.message.reply_text("⚠️ نوع فحص غير معروف.")
            return
        
        formatted = format_result(result, scan_type)
        await update.message.reply_text(formatted, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(format_error(e))

async def handle_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج التشفير"""
    args = context.args
    
    if len(args) < 3:
        await update.message.reply_text(
            "🔐 **التشفير وفك التشفير:**\n"
            "`/crypto encrypt <النص> <المفتاح>`\n"
            "`/crypto decrypt <النص المشفر> <المفتاح>`\n\n"
            "مثال:\n"
            "`/crypto encrypt 'رسالة سرية' مفتاح123`\n"
            "`/crypto decrypt 'U2FsdGVkX1...' مفتاح123`",
            parse_mode="Markdown"
        )
        return
    
    action = args[0].lower()
    text = args[1]
    key = " ".join(args[2:])
    
    try:
        if action == "encrypt":
            result = self.security.encrypt_custom(text, key)
            response = f"🔐 **النص المشفر:**\n`{result}`"
        elif action == "decrypt":
            result = self.security.decrypt_custom(text, key)
            response = f"🔓 **النص الأصلي:**\n`{result}`"
        else:
            await update.message.reply_text("⚠️ استخدم encrypt أو decrypt")
            return
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(format_error(e))

async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة النظام"""
    status = self.bot.get_status()
    
    message = f
    
await update.message.reply_text(message, parse_mode="Markdown")

📊 حالة SHADOWFORGE
━━━━━━━━━━━━━━━━━━━━━
🟢 النظام: {status['system']}
⏱️ مدة التشغيل: {status['uptime']}
👥 المستخدمون النشطون: {status['active_users']}
📝 إجمالي الطلبات: {status['total_requests']}
💾 استخدام الذاكرة: {status['memory_usage']}
📦 الإصدار: {self.bot.config.BOT_VERSION}

🛡️ الخدمات:
• OSINT: {'✅' if status['services']['osint'] else '❌'}
• Payload: {'✅' if status['services']['payload'] else '❌'}
• Stego: {'✅' if status['services']['stego'] else '❌'}
• Scanner: {'✅' if status['services']['scanner'] else '❌'}
━━━━━━━━━━━━━━━━━━━━━
⚡ جميع الخدمات تعمل بكفاءة!
"""
await update.message.reply_text(message, parse_mode="Markdown")

📈 إحصائيات SHADOWFORGE
━━━━━━━━━━━━━━━━━━━━━
📊 أكثر الأوامر استخداماً:
{self._format_stats(stats['top_commands'])}

🌍 أكثر الدول استخداماً:
{self._format_stats(stats['top_countries'])}

📱 أنظمة التشغيل:
{self._format_stats(stats['os_distribution'])}

⏰ أوقات الذروة:
{self._format_stats(stats['peak_hours'])}
━━━━━━━━━━━━━━━━━━━━━
📈 إجمالي المستخدمين: {stats['total_users']}
💬 إجمالي الرسائل: {stats['total_messages']}
"""
async def handle_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تصدير النتائج"""
    if not context.user_data.get('last_result'):
        await update.message.reply_text("⚠️ لا توجد نتائج للتصدير.")
        return
    
    result = context.user_data['last_result']
    filename = f"shadowforge_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(f"/tmp/{filename}", "w") as f:
        json.dump(result, f, indent=2)
    
    await update.message.reply_document(
        document=open(f"/tmp/{filename}", "rb"),
        filename=filename,
        caption="📤 نتائج SHADOWFORGE"
    )

async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء العملية الحالية"""
    context.user_data.clear()
    await update.message.reply_text("❌ تم إلغاء العملية. استخدم /start للعودة.")

@staticmethod
def _format_stats(stats: dict) -> str:
    """تنسيق الإحصائيات"""
    if not stats:
        return "لا توجد بيانات"
    
    lines = []
    for item, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        lines.append(f"• {item}: {count}")
    
    return "\n".join(lines)

async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الصور"""
    if not context.user_data.get('stego_action'):
        await update.message.reply_text("⚠️ استخدم /stego أولاً لتحديد العملية.")
        return
    
    # تحميل الصورة
    photo = await update.message.photo[-1].get_file()
    image_bytes = await photo.download_as_bytearray()
    
    action = context.user_data['stego_action']
    data = context.user_data['stego_data']
    
    await update.message.reply_text("⏳ جاري معالجة الصورة...")
    
    try:
        if action == "encode":
            result = await self.bot.stego.encode_image(image_bytes, data)
            await update.message.reply_photo(
                photo=result,
                caption=f"✅ تم إخفاء الرسالة بنجاح!\nالمفتاح: `{data}`",
                parse_mode="Markdown"
            )
        else:
            result = await self.bot.stego.decode_image(image_bytes, data)
            await update.message.reply_text(
                f"🔓 **الرسالة المستخرجة:**\n`{result}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text(format_error(e))
    
    context.user_data.clear()