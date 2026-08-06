
---

### 4. `handlers/callbacks.py` - معالج الأزرار
```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class CallbackHandlers:
    """معالج الأزرار التفاعلية"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الضغط على الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # قوائم الخدمات
        if data.startswith("menu_"):
            await self.show_service_menu(query, data)
        
        # OSINT
        elif data.startswith("osint_"):
            await self.handle_osint_callback(query, data)
        
        # Payload
        elif data.startswith("payload_"):
            await self.handle_payload_callback(query, data)
        
        # Stego
        elif data.startswith("stego_"):
            await self.handle_stego_callback(query, data)
        
        # Scanner
        elif data.startswith("scan_"):
            await self.handle_scan_callback(query, data)
        
        # Export
        elif data.startswith("export_"):
            await self.handle_export_callback(query, data)
        
        # Help
        elif data == "menu_help":
            await self.show_help(query)
    
    async def show_service_menu(self, query, data):
        """عرض قائمة الخدمة المحددة"""
        service = data.replace("menu_", "")
        
        menus = {
            "osint": {
                "title": "🔍 **خدمات OSINT**",
                "buttons": [
                    [InlineKeyboardButton("🌐 Domain", callback_data="osint_domain")],
                    [InlineKeyboardButton("📧 Email", callback_data="osint_email")],
                    [InlineKeyboardButton("📍 IP", callback_data="osint_ip")],
                    [InlineKeyboardButton("🔗 URL", callback_data="osint_url")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu_main")]
                ]
            },
            "payload": {
                "title": "💉 **توليد الحمولات**",
                "buttons": [
                    [InlineKeyboardButton("🪟 PowerShell", callback_data="payload_powershell")],
                    [InlineKeyboardButton("🐍 Python", callback_data="payload_python")],
                    [InlineKeyboardButton("🐧 Bash", callback_data="payload_bash")],
                    [InlineKeyboardButton("☕ Java", callback_data="payload_java")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu_main")]
                ]
            },
            "stego": {
                "title": "🎨 **إخفاء البيانات**",
                "buttons": [
                    [InlineKeyboardButton("🔒 Encode", callback_data="stego_encode")],
                    [InlineKeyboardButton("🔓 Decode", callback_data="stego_decode")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu_main")]
                ]
            },
            "scan": {
                "title": "🛡️ **فحص الثغرات**",
                "buttons": [
                    [InlineKeyboardButton("🌐 Website", callback_data="scan_web")],
                    [InlineKeyboardButton("🔌 Ports", callback_data="scan_ports")],
                    [InlineKeyboardButton("🛡️ Vuln", callback_data="scan_vuln")],
                    [InlineKeyboardButton("📡 Subdomain", callback_data="scan_subdomain")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu_main")]
                ]
            }
        }
        
        if service in menus:
            await query.edit_message_text(
                menus[service]["title"],
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(menus[service]["buttons"])
            )
        elif service == "main":
            await query.edit_message_text(
                "⚡ **القائمة الرئيسية**\nاختر خدمة:",
                parse_mode="Markdown",
                reply_markup=self.bot.build_keyboard()
            )
        elif service == "status":
            await self.bot.commands.handle_status(
                query.message, None
            )
        elif service == "help":
            await self.show_help(query)
        elif service == "export":
            await self.handle_export_callback(query, data)
    
    async def handle_osint_callback(self, query, data):
        """معالج أزرار OSINT"""
        scan_type = data.replace("osint_", "")
        
        await query.edit_message_text(
            f"🔍 **مسح {scan_type.upper()}**\n\n"
            f"أرسل الهدف للمسح:\n"
            f"مثال: `example.com`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_osint")]
            ])
        )
        
        # تخزين نوع المسح في session
        query.message._context.user_data['osint_type'] = scan_type
    
    async def handle_payload_callback(self, query, data):
        """معالج أزرار الحمولات"""
        language = data.replace("payload_", "")
        
        await query.edit_message_text(
            f"💉 **توليد حمولة {language.upper()}**\n\n"
            f"أرسل الهدف والمنفذ:\n"
            f"مثال: `192.168.1.100 4444`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_payload")]
            ])
        )
        
        query.message._context.user_data['payload_language'] = language
    
    async def handle_stego_callback(self, query, data):
        """معالج أزرار التخفي"""
        action = data.replace("stego_", "")
        
        await query.edit_message_text(
            f"{'🔒' if action == 'encode' else '🔓'} **{action.upper()}**\n\n"
            f"أرسل {'الرسالة والمفتاح' if action == 'encode' else 'الصورة والمفتاح'}:\n"
            f"مثال: `رسالة سرية مفتاح123`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_stego")]
            ])
        )
        
        query.message._context.user_data['stego_action'] = action
    
    async def handle_scan_callback(self, query, data):
        """معالج أزرار الفحص"""
        scan_type = data.replace("scan_", "")
        
        await query.edit_message_text(
            f"🛡️ **فحص {scan_type.upper()}**\n\n"
            f"أرسل الهدف:\n"
            f"مثال: `{'https://example.com' if scan_type == 'web' else '8.8.8.8'}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_scan")]
            ])
        )
        
        query.message._context.user_data['scan_type'] = scan_type
    
    async def handle_export_callback(self, query, data):
        """معالج تصدير النتائج"""
        parts = data.split("_")
        if len(parts) >= 2:
            await self.bot.commands.handle_export(query.message, None)
    
    async def show_help(self, query):
        """عرض المساعدة"""
        help_text = """
❓ **دليل استخدام SHADOWFORGE**

📌 **الأوامر الأساسية:**
• /start - القائمة الرئيسية
• /help - هذه المساعدة
• /cancel - إلغاء العملية

🔍 **خدمات OSINT:**
• مسح النطاقات، البريد الإلكتروني، IPs

💉 **توليد الحمولات:**
• PowerShell, Python, Bash, Java

🎨 **إخفاء البيانات:**
• إخفاء واستخراج رسائل من الصور

🛡️ **فحص الثغرات:**
• فحص المواقع، المنافذ، الثغرات

🔐 **التشفير:**
• تشفير وفك تشفير النصوص

⚠️ **تحذير أمني:**
استخدم الأدوات فقط على أنظمتك الخاصة!
"""
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_main")]
            ])
        )