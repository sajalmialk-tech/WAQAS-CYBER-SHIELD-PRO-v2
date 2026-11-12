# WAQAS CYBER SHIELD PRO v2.0

English-language defensive security toolkit with 40 utilities for Termux and Linux.

## Files
- `main.py` — all 40 tools and terminal menu
- `requirements.txt` — Python dependency
- `README.md` — setup guide
- `reports/` — generated JSON reports

## Termux setup
```bash
pkg update && pkg upgrade -y
pkg install python git termux-api whois traceroute dnsutils -y
pip install -r requirements.txt
python main.py
```

Install the separate Termux:API Android app from a trusted source. Grant Android permissions for Wi-Fi scan data. Device/Android restrictions may still prevent scan results.

## GitHub clone
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
pip install -r requirements.txt
python main.py
```
Replace the URL and folder name with your own repository details.

## 40 tools
01 Wi-Fi Scanner
02 Wi-Fi Security Analyzer
03 Website Security Overview
04 SSL/TLS Certificate Checker
05 Security Headers Analyzer
06 DNS Analyzer
07 HTTP Status Checker
08 Cookie Security Analyzer
09 HTTPS Redirect Checker
10 JSON Report Generator
11 Limited Common-Port Checker
12 Passive Subdomain Finder
13 WHOIS Lookup
14 IP Information
15 Traceroute Analyzer
16 Suspicious URL Heuristic
17 Phishing URL Indicator Check
18 Robots.txt Analyzer
19 Public Technology Hints
20 Local Password Strength Check
21 Security.txt Checker
22 Sitemap Availability Check
23 Redirect Chain Inspector
24 CORS Header Review
25 HTTP Cache Header Review
26 HTTP Compression Review
27 Mixed Content Reference Check
28 HTML Form Configuration Review
29 External Link Summary
30 Email SPF/DMARC DNS Review
31 MX Record Lookup
32 NS Record Lookup
33 TXT Record Lookup
34 Local Network Information
35 Connectivity Diagnostics
36 File Hash Calculator
37 Local File Permission Review
38 Python Environment Inventory
39 System Tool Availability
40 Security Report Generator

## Limitations and safe use
- Use only on systems and networks you own or have explicit permission to assess.
- Wi-Fi results depend on Termux:API, Android permissions and device support. Encryption assessment uses advertised scan metadata only; it cannot inspect router settings or guarantee a security score.
- The port checker is deliberately limited to ten common TCP ports and is not a vulnerability scanner.
- Subdomain discovery is passive and uses public Certificate Transparency data.
- URL/phishing checks are local heuristics, not a malware reputation service.
- DNS utilities depend on installed system commands and resolver behavior.
- Website checks are passive HTTP/TLS inspections. No exploitation, brute force, deauthentication, stealth or access bypass is included.
- Password checking is local. Use a test password only, never a real account password.
- Reports may contain hostnames and URLs; review before sharing.
- Some tools require optional packages (`whois`, `traceroute`, `dnsutils`).
