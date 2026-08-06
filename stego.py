from PIL import Image
import io
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

class StegoModule:
    """وحدة إخفاء البيانات في الصور"""
    
    def __init__(self, config):
        self.config = config
    
    async def encode_image(self, image_bytes: bytes, message: str, key: str = None) -> bytes:
        """إخفاء رسالة في صورة"""
        # تشفير الرسالة
        if key:
            encrypted = self._encrypt_message(message, key)
        else:
            encrypted = message.encode()
        
        # فتح الصورة
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        pixels = image.load()
        
        # تحويل الرسالة إلى بايت
        msg_bytes = encrypted + b'###'  # علامة النهاية
        msg_bits = ''.join(format(byte, '08b') for byte in msg_bytes)
        
        # إخفاء في البكسلات
        width, height = image.size
        bit_index = 0
        
        for y in range(height):
            for x in range(width):
                if bit_index >= len(msg_bits):
                    break
                r, g, b = pixels[x, y]
                # تعديل البت الأقل أهمية في القناة الحمراء
                r = (r & 0xFE) | int(msg_bits[bit_index])
                pixels[x, y] = (r, g, b)
                bit_index += 1
            if bit_index >= len(msg_bits):
                break
        
        # حفظ الصورة
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
    
    async def decode_image(self, image_bytes: bytes, key: str = None) -> str:
        """استخراج رسالة من صورة"""
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        pixels = image.load()
        
        # استخراج البتات
        bits = []
        width, height = image.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                bits.append(str(r & 1))
        
        # تحويل إلى بايت
        msg_bytes = bytearray()
        for i in range(0, len(bits) - 7, 8):
            byte = ''.join(bits[i:i+8])
            msg_bytes.append(int(byte, 2))
            # التحقق من علامة النهاية
            if msg_bytes[-3:] == b'###':
                msg_bytes = msg_bytes[:-3]
                break
        
        # فك التشفير
        if key and len(msg_bytes) > 0:
            try:
                msg_bytes = self._decrypt_message(bytes(msg_bytes), key)
            except:
                pass
        
        return msg_bytes.decode('utf-8', errors='ignore')
    
    def _encrypt_message(self, message: str, key: str) -> bytes:
        """تشفير الرسالة"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        cipher = AES.new(key_bytes, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
        return cipher.iv + ct_bytes
    
    def _decrypt_message(self, ciphertext: bytes, key: str) -> bytes:
        """فك تشفير الرسالة"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        iv = ciphertext[:16]
        ct = ciphertext[16:]
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt