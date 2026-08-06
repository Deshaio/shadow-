import aiohttp
import asyncio
from typing import Dict, Any, Optional
import dns.resolver
import whois
import socket
import requests
from bs4 import BeautifulSoup

class OSINTModule:
    """وحدة استطلاع المعلومات"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def scan_domain(self, domain: str) -> Dict[str, Any]:
        """مسح نطاق"""
        result = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        try:
            # Whois
            w = whois.whois(domain)
            result["data"]["whois"] = {
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "expiration_date": str(w.expiration_date),
                "name_servers": w.name_servers
            }
            
            # DNS
            dns_result = {}
            for record in ['A', 'MX', 'CNAME', 'TXT', 'NS']:
                try:
                    answers = dns.resolver.resolve(domain, record)
                    dns_result[record] = [str(r) for r in answers]
                except:
                    dns_result[record] = []
            result["data"]["dns"] = dns_result
            
            # Subdomains
            subdomains = await self.enumerate_subdomains(domain)
            result["data"]["subdomains"] = subdomains[:20]
            
            # Shodan
            if self.config.SHODAN_KEY:
                from shodan import Shodan
                api = Shodan(self.config.SHODAN_KEY)
                try:
                    info = api.host(domain)
                    result["data"]["shodan"] = {
                        "ports": info.get('ports', []),
                        "services": info.get('data', [])[:5]
                    }
                except:
                    pass
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def scan_email(self, email: str) -> Dict[str, Any]:
        """البحث عن معلومات بريد إلكتروني"""
        result = {
            "email": email,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        try:
            # Hunter.io
            if self.config.HUNTER_API_KEY:
                url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={self.config.HUNTER_API_KEY}"
                async with await self.get_session() as session:
                    async with session.get(url) as response:
                        data = await response.json()
                        if data.get('data'):
                            result["data"]["hunter"] = {
                                "status": data['data'].get('status'),
                                "score": data['data'].get('score'),
                                "sources": data['data'].get('sources', [])[:5]
                            }
            
            # LeakCheck
            url = f"https://leakcheck.io/api/public?check={email}"
            async with await self.get_session() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get('success'):
                        result["data"]["leaks"] = data.get('found', 0)
            
            # Domain from email
            domain = email.split('@')[-1]
            result["data"]["domain_info"] = await self.scan_domain(domain)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def scan_ip(self, ip: str) -> Dict[str, Any]:
        """معلومات عن IP"""
        result = {
            "ip": ip,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        try:
            # GeoIP
            url = f"http://ip-api.com/json/{ip}"
            async with await self.get_session() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get('status') == 'success':
                        result["data"]["geo"] = {
                            "country": data.get('country'),
                            "city": data.get('city'),
                            "region": data.get('regionName'),
                            "isp": data.get('isp'),
                            "org": data.get('org')
                        }
            
            # Shodan
            if self.config.SHODAN_KEY:
                from shodan import Shodan
                api = Shodan(self.config.SHODAN_KEY)
                try:
                    info = api.host(ip)
                    result["data"]["shodan"] = {
                        "ports": info.get('ports', []),
                        "vulns": info.get('vulns', []),
                        "services": info.get('data', [])[:5]
                    }
                except:
                    pass
            
            # VirusTotal
            if self.config.VIRUSTOTAL_KEY:
                url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
                headers = {"x-apikey": self.config.VIRUSTOTAL_KEY}
                async with await self.get_session() as session:
                    async with session.get(url, headers=headers) as response:
                        data = await response.json()
                        if data.get('data'):
                            stats = data['data']['attributes'].get('last_analysis_stats', {})
                            result["data"]["virustotal"] = stats
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def enumerate_subdomains(self, domain: str) -> list:
        """تعداد النطاقات الفرعية"""
        subdomains = set()
        
        # قائمة النطاقات الشائعة
        common = ['www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp',
                  'pop', 'ns1', 'webdisk', 'ns2', 'cpanel', 'whm', 'autodiscover',
                  'autoconfig', 'm', 'imap', 'test', 'dns', 'api', 'blog']
        
        for sub in common:
            try:
                full = f"{sub}.{domain}"
                dns.resolver.resolve(full, 'A')
                subdomains.add(full)
            except:
                pass
        
        return list(subdomains)