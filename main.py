#!/usr/bin/env python3
"""WAQAS CYBER SHIELD PRO v2.0 - defensive security toolkit."""
import os, re, sys, ssl, json, time, socket, shutil, hashlib, platform, subprocess, ipaddress
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen

try:
    import requests
except ImportError:
    requests = None

APP, VERSION = "WAQAS CYBER SHIELD PRO", "2.0"
REPORT_DIR = Path("reports")
HISTORY = []
RESET, CYAN, GREEN, YELLOW, RED, BOLD = "\033[0m", "\033[96m", "\033[92m", "\033[93m", "\033[91m", "\033[1m"

def color(s, col):
    return f"{col}{s}{RESET}" if sys.stdout.isatty() and not os.getenv("NO_COLOR") else str(s)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(color("╔══════════════════════════════════════════════════════════════╗", CYAN))
    print(color("║                  WAQAS CYBER SHIELD PRO                      ║", CYAN+BOLD))
    print(color("║             DEFENSIVE SECURITY TOOLKIT  |  v2.0              ║", CYAN))
    print(color("╚══════════════════════════════════════════════════════════════╝", CYAN))
    print("  40 SECURITY UTILITIES  •  TERMUX / LINUX  •  ENGLISH UI\n")

def section(name):
    print("\n" + color("─"*64 + "\n  " + name.upper() + "\n" + "─"*64, CYAN+BOLD))

def pause():
    input("\nPress Enter to return to menu...")

def out(name, result):
    HISTORY.append({"tool": name, "timestamp_utc": datetime.now(timezone.utc).isoformat(), "result": result})
    section(name)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str) if isinstance(result, (dict,list)) else str(result))

def host_input():
    h = input("Hostname or IP: ").strip()
    if not h or any(x in h for x in "/?# \t"): raise ValueError("Enter a hostname or IP only.")
    return h.strip(".")

def domain_input():
    d = host_input().lower()
    if not re.fullmatch(r"(?=.{1,253}$)[a-z0-9.-]+", d): raise ValueError("Invalid domain.")
    return d

def url_input():
    u = input("Target URL (https://example.com): ").strip()
    if not u: raise ValueError("URL cannot be empty.")
    if "://" not in u: u = "https://" + u
    p = urlparse(u)
    if p.scheme not in ("http","https") or not p.hostname: raise ValueError("Only valid HTTP/HTTPS URLs are supported.")
    return u

def req(url, method="GET", timeout=10, redirects=True):
    headers = {"User-Agent": "WaqasCyberShield/2.0 defensive-audit"}
    if requests: return requests.request(method, url, headers=headers, timeout=timeout, allow_redirects=redirects)
    return urlopen(Request(url, headers=headers, method=method), timeout=timeout)

def headers(r): return dict(r.headers.items())
def status(r): return getattr(r, "status_code", getattr(r, "status", None))
def final_url(r, original): return getattr(r, "url", original)
def body(r, limit=250000):
    t = getattr(r, "text", None)
    return t[:limit] if t is not None else r.read(limit).decode("utf-8","replace")
def run(cmd, timeout=15): return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=timeout)
def resolve(host): return sorted({x[4][0] for x in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})

# 01
def wifi_scan():
    if not shutil.which("termux-wifi-scaninfo"):
        return out("Wi-Fi Scanner", {"status":"Unavailable","hint":"Install Termux:API Android app and `pkg install termux-api`; grant Android permissions."})
    try:
        aps=json.loads(run(["termux-wifi-scaninfo"],15))
        out("Wi-Fi Scanner",[{"ssid":a.get("ssid",""),"bssid":a.get("bssid",""),"frequency_mhz":a.get("frequency_mhz"),"rssi_dbm":a.get("rssi"),"capabilities":a.get("capabilities","Not reported")} for a in aps])
    except Exception as e: out("Wi-Fi Scanner",{"error":str(e),"hint":"Check Android Wi-Fi/Location/Nearby devices permissions."})

# 02
def wifi_security():
    if not shutil.which("termux-wifi-scaninfo"): return out("Wi-Fi Security Analyzer",{"status":"Unavailable","reason":"Termux:API command not found."})
    try:
        aps=json.loads(run(["termux-wifi-scaninfo"],15)); rows=[]
        for a in aps:
            cap=str(a.get("capabilities","")).upper()
            grade="Strong advertised encryption: WPA3" if "WPA3" in cap else "Generally acceptable advertised encryption: WPA2" if "WPA2" in cap else "Weak legacy encryption: WEP" if "WEP" in cap else "Legacy WPA; upgrade recommended" if "WPA" in cap else "Open or unknown; verify router settings"
            rows.append({"ssid":a.get("ssid",""),"capabilities":cap,"assessment":grade})
        out("Wi-Fi Security Analyzer",{"results":rows,"limitation":"Uses Android scan metadata only; cannot inspect router configuration or guarantee a security score."})
    except Exception as e: out("Wi-Fi Security Analyzer",{"error":str(e)})

# 03
def website_scan():
    u=url_input()
    try:
        r=req(u); h=headers(r); keys=["Strict-Transport-Security","Content-Security-Policy","X-Content-Type-Options","X-Frame-Options","Referrer-Policy","Permissions-Policy"]
        out("Website Security Overview",{"requested_url":u,"final_url":final_url(r,u),"status":status(r),"https_final":urlparse(final_url(r,u)).scheme=="https","server":h.get("Server","Not disclosed"),"content_type":h.get("Content-Type","Unknown"),"present_headers":[k for k in keys if k in h],"missing_headers":[k for k in keys if k not in h]})
    except Exception as e: out("Website Security Overview",{"error":str(e)})

# 04
def ssl_check():
    h=host_input()
    try:
        ctx=ssl.create_default_context()
        with socket.create_connection((h,443),timeout=8) as s:
            with ctx.wrap_socket(s,server_hostname=h) as t:
                cert=t.getpeercert()
                out("SSL/TLS Certificate Checker",{"hostname":h,"tls_version":t.version(),"cipher":t.cipher(),"subject":cert.get("subject"),"issuer":cert.get("issuer"),"valid_from":cert.get("notBefore"),"valid_until":cert.get("notAfter"),"trust_validation":"Passed"})
    except Exception as e: out("SSL/TLS Certificate Checker",{"error":str(e)})

# 05
def headers_check():
    u=url_input()
    try:
        h=headers(req(u)); purposes={"Strict-Transport-Security":"Enforces HTTPS","Content-Security-Policy":"Restricts content sources","X-Content-Type-Options":"Helps prevent MIME sniffing","X-Frame-Options":"Controls framing","Referrer-Policy":"Controls referrer data","Permissions-Policy":"Controls browser feature access"}
        out("Security Headers Analyzer",{k:{"present":k in h,"value":h.get(k),"purpose":v} for k,v in purposes.items()})
    except Exception as e: out("Security Headers Analyzer",{"error":str(e)})

# 06
def dns_check():
    h=host_input()
    try: out("DNS Analyzer",{"hostname":h,"addresses":resolve(h),"note":"System resolver lookup, not full DNS enumeration."})
    except Exception as e: out("DNS Analyzer",{"error":str(e)})

# 07
def http_status():
    u=url_input()
    try:
        r=req(u); out("HTTP Status Checker",{"requested":u,"final":final_url(r,u),"status":status(r),"reason":getattr(r,"reason","")})
    except Exception as e: out("HTTP Status Checker",{"error":str(e)})

# 08
def cookie_check():
    u=url_input()
    try:
        r=req(u); raw=r.raw.headers.getlist("Set-Cookie") if requests and hasattr(r.raw.headers,"getlist") else ([headers(r).get("Set-Cookie")] if headers(r).get("Set-Cookie") else [])
        rows=[]
        for x in raw:
            sm=re.search(r";\s*samesite=([^;]+)",x,re.I)
            rows.append({"name":x.split("=",1)[0],"Secure":bool(re.search(r";\s*secure\b",x,re.I)),"HttpOnly":bool(re.search(r";\s*httponly\b",x,re.I)),"SameSite":sm.group(1) if sm else "Missing"})
        out("Cookie Security Analyzer",rows or {"message":"No Set-Cookie header observed."})
    except Exception as e: out("Cookie Security Analyzer",{"error":str(e)})

# 09
def https_check():
    h=host_input(); u="http://"+h
    try:
        r=req(u); f=final_url(r,u); out("HTTPS Redirect Checker",{"initial":u,"final":f,"redirected_to_https":urlparse(f).scheme=="https"})
    except Exception as e: out("HTTPS Redirect Checker",{"error":str(e)})

# 10 / 40
def report():
    REPORT_DIR.mkdir(exist_ok=True); p=REPORT_DIR/("report-"+datetime.now().strftime("%Y%m%d-%H%M%S")+".json")
    p.write_text(json.dumps({"application":APP,"version":VERSION,"generated_utc":datetime.now(timezone.utc).isoformat(),"results":HISTORY},indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    out("Security Report Generator",{"saved_to":str(p),"records":len(HISTORY)})

# 11 - Limited ports only, authorization gate
def port_check():
    h=host_input()
    if input("Confirm you own this host or have explicit permission (yes/no): ").lower()!="yes": return out("Limited Port Checker",{"status":"Cancelled"})
    ports=[21,22,25,53,80,110,143,443,445,8080]; rows=[]
    for p in ports:
        s=socket.socket(); s.settimeout(.5)
        try: s.connect((h,p)); state="open"
        except OSError: state="closed_or_filtered"
        finally: s.close()
        rows.append({"port":p,"state":state})
    out("Limited Common-Port Checker",{"host":h,"results":rows,"note":"Ten common TCP ports only; not a vulnerability scan."})

# 12 passive CT
def subdomains():
    d=domain_input()
    try:
        r=req("https://crt.sh/?q=%25."+d+"&output=json",timeout=15)
        data=r.json() if requests else json.loads(body(r))
        names=sorted({n.strip().lower() for row in data for n in row.get("name_value","").splitlines() if n.strip().lower()==d or n.strip().lower().endswith("."+d)})
        out("Passive Subdomain Finder",{"domain":d,"subdomains":names[:150],"source":"Public Certificate Transparency records","note":"Passive data can be stale or incomplete."})
    except Exception as e: out("Passive Subdomain Finder",{"error":str(e)})

# 13
def whois():
    d=domain_input()
    if not shutil.which("whois"): return out("WHOIS Lookup",{"error":"Install with: pkg install whois"})
    try: out("WHOIS Lookup",run(["whois",d],18)[:8000])
    except Exception as e: out("WHOIS Lookup",{"error":str(e)})

# 14
def ip_info():
    h=host_input()
    try: out("IP Information",{"input":h,"addresses":[{"ip":x,"type":"private" if ipaddress.ip_address(x).is_private else "public","version":ipaddress.ip_address(x).version} for x in resolve(h)],"note":"No person-level geolocation or tracking."})
    except Exception as e: out("IP Information",{"error":str(e)})

# 15
def traceroute():
    h=host_input()
    if platform.system().lower()=="windows": cmd=["tracert","-h","12","-w","1000",h]
    elif shutil.which("traceroute"): cmd=["traceroute","-m","12","-w","1",h]
    elif shutil.which("tracepath"): cmd=["tracepath","-m","12",h]
    else: return out("Traceroute",{"error":"Install traceroute: pkg install traceroute"})
    try: out("Traceroute Analyzer",run(cmd,30)[:8000])
    except Exception as e: out("Traceroute Analyzer",{"error":str(e)})

# 16
def suspicious_url():
    u=url_input(); p=urlparse(u); h=p.hostname or ""; flags=[]
    if p.scheme!="https": flags.append("No HTTPS")
    if len(u)>180: flags.append("Unusually long URL")
    if "@" in p.netloc: flags.append("@ in URL authority")
    try: ipaddress.ip_address(h); flags.append("IP address used as hostname")
    except ValueError: pass
    if h.count("-")>=3: flags.append("Multiple hyphens in hostname")
    out("Suspicious URL Heuristic",{"url":u,"indicators":flags,"note":"Heuristic only; no malware database is queried."})

# 17
def phishing_check():
    u=url_input(); p=urlparse(u); h=p.hostname or ""; terms=["login","verify","secure","account","update","wallet","password"]; found=[x for x in terms if x in (h+p.path).lower()]; flags=[]
    if p.scheme!="https": flags.append("No HTTPS")
    if "@" in p.netloc: flags.append("@ in authority")
    if h.startswith("xn--") or ".xn--" in h: flags.append("Punycode hostname")
    if len(found)>=2: flags.append("Multiple sensitive keywords")
    if len(h.split("."))>5: flags.append("Many subdomain levels")
    out("Phishing URL Indicator Check",{"url":u,"indicators":flags,"keywords":found,"note":"Indicators are not proof of phishing."})

# 18
def robots():
    u=url_input(); p=urlparse(u); target=f"{p.scheme}://{p.netloc}/robots.txt"
    try:
        r=req(target); out("Robots.txt Analyzer",{"url":target,"status":status(r),"content":body(r,5000),"note":"robots.txt is not access control."})
    except Exception as e: out("Robots.txt Analyzer",{"error":str(e)})

# 19
def tech():
    u=url_input()
    try:
        r=req(u); h=headers(r); b=body(r).lower(); hints=[f"{k}: {h[k]}" for k in ("Server","X-Powered-By","X-Generator") if h.get(k)]
        for x in ("wp-content","drupal.settings","joomla!","shopify","next.js","__next_data__","laravel"):
            if x in b: hints.append("HTML marker: "+x)
        out("Public Technology Hints",{"url":final_url(r,u),"hints":hints,"note":"Approximate public fingerprinting only."})
    except Exception as e: out("Public Technology Hints",{"error":str(e)})

# 20
def password_strength():
    pw=input("Enter a TEST password only (not transmitted or saved): ")
    checks={"12+ characters":len(pw)>=12,"lowercase":bool(re.search("[a-z]",pw)),"uppercase":bool(re.search("[A-Z]",pw)),"number":bool(re.search("[0-9]",pw)),"symbol":bool(re.search("[^A-Za-z0-9]",pw))}
    score=sum(checks.values()); rating="Strong pattern" if score==5 and len(pw)>=14 else "Moderate pattern" if score>=4 and len(pw)>=10 else "Weak pattern"
    out("Local Password Strength Check",{"rating":rating,"checks":checks,"advice":"Use a unique long passphrase for each account. Never enter a real account password."}); del pw

# 21
def security_txt():
    u=url_input(); p=urlparse(u); t=f"{p.scheme}://{p.netloc}/.well-known/security.txt"
    try: r=req(t); out("Security.txt Checker",{"url":t,"status":status(r),"content":body(r,4000)})
    except Exception as e: out("Security.txt Checker",{"error":str(e)})

# 22
def sitemap():
    u=url_input(); p=urlparse(u); t=f"{p.scheme}://{p.netloc}/sitemap.xml"
    try:
        r=req(t); b=body(r,3000); out("Sitemap Availability",{"url":t,"status":status(r),"xml_detected":"<urlset" in b.lower() or "<sitemapindex" in b.lower(),"preview":b[:1500]})
    except Exception as e: out("Sitemap Availability",{"error":str(e)})

# 23
def redirects():
    u=url_input()
    try:
        r=req(u); chain=[]
        if requests:
            for x in r.history: chain.append({"status":x.status_code,"from":x.url,"location":x.headers.get("Location")})
        chain.append({"final_status":status(r),"final_url":final_url(r,u)})
        out("Redirect Chain Inspector",{"chain":chain,"redirect_count":max(0,len(chain)-1)})
    except Exception as e: out("Redirect Chain Inspector",{"error":str(e)})

# 24
def cors():
    u=url_input()
    try:
        h=headers(req(u)); out("CORS Header Review",{"allow_origin":h.get("Access-Control-Allow-Origin","Not present"),"allow_credentials":h.get("Access-Control-Allow-Credentials","Not present"),"allow_methods":h.get("Access-Control-Allow-Methods","Not present"),"note":"Passive header review only."})
    except Exception as e: out("CORS Header Review",{"error":str(e)})

# 25
def cache_headers():
    u=url_input()
    try:
        h=headers(req(u)); out("HTTP Cache Header Review",{k:h.get(k,"Not present") for k in ["Cache-Control","Pragma","Expires","ETag","Last-Modified","Vary"]})
    except Exception as e: out("HTTP Cache Header Review",{"error":str(e)})

# 26
def compression():
    u=url_input()
    try:
        h=headers(req(u)); out("HTTP Compression Review",{"Content-Encoding":h.get("Content-Encoding","Not reported"),"Vary":h.get("Vary","Not present"),"note":"Header review only; no performance benchmark."})
    except Exception as e: out("HTTP Compression Review",{"error":str(e)})

# 27
def mixed_content():
    u=url_input()
    try:
        r=req(u); b=body(r); found=sorted(set(re.findall(r"""(?:src|href)\s*=\s*["'](http://[^"']+)""",b,re.I)))
        out("Mixed Content Reference Check",{"page":final_url(r,u),"http_resource_references":found[:60],"count":len(found),"note":"Static HTML inspection; dynamic resources may be missed."})
    except Exception as e: out("Mixed Content Reference Check",{"error":str(e)})

# 28
def forms():
    u=url_input()
    try:
        r=req(u); b=body(r); tags=re.findall(r"<form\b[^>]*>",b,re.I); rows=[]
        for tag in tags[:40]:
            a=re.search(r"""action\s*=\s*["']([^"']*)""",tag,re.I); m=re.search(r"""method\s*=\s*["']([^"']*)""",tag,re.I)
            rows.append({"action":a.group(1) if a else "(same page/default)","method":m.group(1).upper() if m else "GET (default)"})
        out("HTML Form Configuration Review",{"page":final_url(r,u),"forms_found":len(tags),"forms":rows,"page_uses_https":urlparse(final_url(r,u)).scheme=="https","note":"Static HTML review; JavaScript forms may be missed."})
    except Exception as e: out("HTML Form Configuration Review",{"error":str(e)})

# 29
def external_links():
    u=url_input(); host=urlparse(u).hostname
    try:
        r=req(u); b=body(r); links=re.findall(r"""href\s*=\s*["']([^"'#]+)""",b,re.I); final=final_url(r,u)
        ext=sorted({urljoin(final,x) for x in links if urlparse(urljoin(final,x)).hostname not in (None,host)})
        out("External Link Summary",{"page":final,"external_count":len(ext),"examples":ext[:40],"note":"Static HTML links only."})
    except Exception as e: out("External Link Summary",{"error":str(e)})

# 30
def spf_dmarc():
    d=domain_input(); data={}
    for label,name in [("SPF",d),("DMARC","_dmarc."+d)]:
        try: data[label]=run(["nslookup","-type=TXT",name],10)[:3000]
        except Exception as e: data[label]=f"Lookup unavailable: {e}"
    out("Email SPF/DMARC DNS Review",{"domain":d,"records":data,"note":"Resolver output varies; verify with your DNS provider."})

# 31
def mx():
    d=domain_input()
    try: out("MX Record Lookup",run(["nslookup","-type=MX",d],10)[:5000])
    except Exception as e: out("MX Record Lookup",{"error":str(e),"hint":"Install dnsutils/bind-tools."})

# 32
def ns():
    d=domain_input()
    try: out("NS Record Lookup",run(["nslookup","-type=NS",d],10)[:5000])
    except Exception as e: out("NS Record Lookup",{"error":str(e)})

# 33
def txt():
    d=domain_input()
    try: out("TXT Record Lookup",run(["nslookup","-type=TXT",d],10)[:5000])
    except Exception as e: out("TXT Record Lookup",{"error":str(e)})

# 34
def local_network():
    data={"hostname":socket.gethostname(),"platform":platform.platform(),"python":sys.version.split()[0]}
    try: data["resolved_local_addresses"]=resolve(socket.gethostname())
    except Exception as e: data["lookup_error"]=str(e)
    out("Local Network Information",data)

# 35
def connectivity():
    rows=[]
    for h,p in [("1.1.1.1",443),("8.8.8.8",53),("example.com",443)]:
        try:
            with socket.create_connection((h,p),timeout=3): rows.append({"target":f"{h}:{p}","reachable":True})
        except Exception as e: rows.append({"target":f"{h}:{p}","reachable":False,"reason":str(e)})
    out("Connectivity Diagnostics",rows)

# 36
def file_hash():
    p=Path(input("File path: ").strip()).expanduser()
    if not p.is_file(): return out("File Hash Calculator",{"error":"File not found."})
    hs={"sha256":hashlib.sha256(),"sha1":hashlib.sha1(),"md5":hashlib.md5()}
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            for h in hs.values(): h.update(block)
    out("File Hash Calculator",{"file":str(p),"size_bytes":p.stat().st_size,"hashes":{k:v.hexdigest() for k,v in hs.items()},"note":"Prefer SHA-256; MD5/SHA-1 are legacy compatibility hashes."})

# 37
def file_permissions():
    p=Path(input("File or directory path: ").strip()).expanduser()
    if not p.exists(): return out("Local File Permission Review",{"error":"Path does not exist."})
    m=p.stat().st_mode
    out("Local File Permission Review",{"path":str(p),"is_file":p.is_file(),"is_directory":p.is_dir(),"mode_octal":oct(m&0o777),"owner_write":bool(m&0o200),"group_write":bool(m&0o020),"other_write":bool(m&0o002),"other_read":bool(m&0o004)})

# 38
def python_inventory():
    pkgs={}
    try:
        import importlib.metadata as md
        for d in md.distributions():
            n=d.metadata.get("Name")
            if n: pkgs[n]=d.version
    except Exception as e: pkgs["inventory_error"]=str(e)
    out("Python Environment Inventory",{"python":sys.version,"platform":platform.platform(),"package_count":len(pkgs),"packages":dict(sorted(pkgs.items())),"note":"Inventory only; not a vulnerability audit."})

# 39
def tool_availability():
    names=["python","git","whois","traceroute","tracepath","nslookup","termux-wifi-scaninfo"]
    out("System Tool Availability",{n:shutil.which(n) or "Not installed" for n in names})

TOOLS=[
("01","Wi-Fi Scanner",wifi_scan),("02","Wi-Fi Security Analyzer",wifi_security),("03","Website Security Overview",website_scan),("04","SSL/TLS Certificate Checker",ssl_check),("05","Security Headers Analyzer",headers_check),("06","DNS Analyzer",dns_check),("07","HTTP Status Checker",http_status),("08","Cookie Security Analyzer",cookie_check),("09","HTTPS Redirect Checker",https_check),("10","JSON Report Generator",report),
("11","Limited Common-Port Checker",port_check),("12","Passive Subdomain Finder",subdomains),("13","WHOIS Lookup",whois),("14","IP Information",ip_info),("15","Traceroute Analyzer",traceroute),("16","Suspicious URL Heuristic",suspicious_url),("17","Phishing URL Indicator Check",phishing_check),("18","Robots.txt Analyzer",robots),("19","Public Technology Hints",tech),("20","Local Password Strength Check",password_strength),
("21","Security.txt Checker",security_txt),("22","Sitemap Availability Check",sitemap),("23","Redirect Chain Inspector",redirects),("24","CORS Header Review",cors),("25","HTTP Cache Header Review",cache_headers),("26","HTTP Compression Review",compression),("27","Mixed Content Reference Check",mixed_content),("28","HTML Form Configuration Review",forms),("29","External Link Summary",external_links),("30","Email SPF/DMARC DNS Review",spf_dmarc),
("31","MX Record Lookup",mx),("32","NS Record Lookup",ns),("33","TXT Record Lookup",txt),("34","Local Network Information",local_network),("35","Connectivity Diagnostics",connectivity),("36","File Hash Calculator",file_hash),("37","Local File Permission Review",file_permissions),("38","Python Environment Inventory",python_inventory),("39","System Tool Availability",tool_availability),("40","Security Report Generator",report)]

def main():
    REPORT_DIR.mkdir(exist_ok=True)
    while True:
        clear(); banner()
        groups=[("CORE WI-FI / WEBSITE TOOLS",TOOLS[:10]),("NETWORK / DOMAIN TOOLS",TOOLS[10:20]),("ADDITIONAL DEFENSIVE UTILITIES",TOOLS[20:])]
        for title,items in groups:
            print(color("\n"+title,GREEN+BOLD))
            for n,name,_ in items: print(f"  [{n}] {name}")
        print(color("\n  [00] Exit",YELLOW+BOLD))
        choice=input(color("\nSelect a tool (00-40): ",CYAN)).strip().zfill(2)
        if choice in ("00","0"): print(color("Thank you for using WAQAS CYBER SHIELD PRO.",GREEN)); break
        item=next((x for x in TOOLS if x[0]==choice),None)
        if not item: print(color("Invalid selection.",RED)); time.sleep(1); continue
        try: item[2](); pause()
        except KeyboardInterrupt: print(color("\nCancelled.",YELLOW)); pause()
        except Exception as e: print(color(f"\nTool error: {e}",RED)); pause()

if __name__=="__main__": main()
