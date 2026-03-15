#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Token Checker v4.1 — Termux Edition
รองรับภาษาไทยอย่างถูกต้อง  (Thai-aware display width)
"""

import sys, os, re, base64, time
from datetime import datetime

# ── ensure UTF-8 stdout ───────────────────────────────────────────
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
os.environ.setdefault('LANG', 'th_TH.UTF-8')

try:
    import requests
except ImportError:
    print("\n[!] ไม่พบ requests\n    pip install requests\n")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════
#  ANSI
# ══════════════════════════════════════════════════════════════════
R  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'
IT = '\033[3m'
UL = '\033[4m'

Rd = '\033[91m'
Gr = '\033[92m'
Ye = '\033[93m'
Bl = '\033[94m'
Mg = '\033[95m'
Cy = '\033[96m'
Wh = '\033[97m'

BGm = '\033[45m'
BGb = '\033[44m'
BGg = '\033[42m'
BGr = '\033[41m'

GRAD = ['\033[95m','\033[94m','\033[96m','\033[94m','\033[95m']
def gradient(text):
    out, i = '', 0
    for ch in text:
        if ch.strip():
            out += GRAD[i % len(GRAD)] + ch; i += 1
        else:
            out += ch
    return out + R

# ══════════════════════════════════════════════════════════════════
#  Thai-aware display width
# ══════════════════════════════════════════════════════════════════
# Thai combining / zero-width characters (ไม่กินพื้นที่แสดงผล)
_THAI_ZERO = frozenset([
    0x0E31,                          # ั  sara a (above)
    *range(0x0E34, 0x0E3B),          # ิ ี ึ ื ุ ู ฺ
    *range(0x0E47, 0x0E4F),          # ็ ่ ้ ๊ ๋ ์ ํ ๎
])

def dw(text: str) -> int:
    """คำนวณความกว้างที่แสดงผลจริงของข้อความ (รองรับ Thai combining chars)"""
    if not text:
        return 0
    # ลบ ANSI escape codes ออกก่อน
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    width = 0
    for ch in clean:
        cp = ord(ch)
        if cp in _THAI_ZERO:
            continue          # zero-width combining
        elif cp > 0x1000:
            width += 1        # CJK / Thai consonants / other unicode = 1
        else:
            width += 1        # ASCII = 1
    return width

def rpad(text: str, width: int, fill=' ') -> str:
    """Right-pad โดยใช้ display width จริง (ไม่ใช้ len)"""
    diff = width - dw(text)
    return text + fill * max(diff, 0)

def lpad(text: str, width: int, fill=' ') -> str:
    """Left-pad โดยใช้ display width จริง"""
    diff = width - dw(text)
    return fill * max(diff, 0) + text

# ══════════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════════
W = 54

def clr(): os.system('clear' if os.name != 'nt' else 'cls')

def pause(msg="กด Enter เพื่อดำเนินการต่อ"):
    input(f"\n  {Ye}>>  {msg} ...{R}")

def hr(ch='─', c=Cy):
    print(f"  {c}{ch*W}{R}")

def title(txt, c=Mg):
    print(f"\n  {c}{BD}{'═'*W}{R}")
    t_pad = rpad(f"  {txt}", W + 2)
    print(f"  {c}{BD}{t_pad}{R}")
    print(f"  {c}{BD}{'═'*W}{R}\n")

def spin(msg, secs=1.2):
    fr = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    t, i = time.time() + secs, 0
    while time.time() < t:
        print(f"\r  {Cy}{fr[i%10]}{R}  {BD}{msg}{R}  ", end='', flush=True)
        time.sleep(0.07); i += 1
    print('\r' + ' '*55 + '\r', end='')

def ok(msg):   print(f"  {Gr}{BD} + {R}  {Gr}{msg}{R}")
def err(msg):  print(f"  {Rd}{BD} - {R}  {Rd}{msg}{R}")
def info(msg): print(f"  {Cy}{BD} i {R}  {msg}")
def warn(msg): print(f"  {Ye}{BD} ! {R}  {Ye}{msg}{R}")

# row แบบ inline — ใช้ dw() แทน len() เพื่อ align ภาษาไทย
def row(icon, label, value, lc=Bl, vc=Wh, col_width=18):
    padded = rpad(label, col_width)
    print(f"  {lc}{icon}{R}  {BD}{lc}{padded}{R}  {vc}{value}{R}")

# ══════════════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════════════
ART = r"""
 ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗
 ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
 ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
 ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
 ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
 ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝

 ████████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗
 ╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║
    ██║   ██║   ██║█████╔╝ █████╗  ██╔██╗ ██║
    ██║   ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║
    ██║   ╚██████╔╝██║  ██╗███████╗██║ ╚████║
    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝
"""

def banner():
    clr()
    for line in ART.split('\n'):
        print(gradient(line))
    print(f"  {DM}{'─'*W}{R}")
    ver = rpad("  v4.1  |  Termux Edition  |  Thai Support", W)
    print(f"  {DM}{ver}{R}")
    print(f"  {DM}{'─'*W}{R}\n")

# ══════════════════════════════════════════════════════════════════
#  TOKEN CORE
# ══════════════════════════════════════════════════════════════════
def clean(t): return t.replace('Bot ','').strip()

def valid_fmt(t):
    return bool(re.match(r'^[\w-]{24,28}\.[\w-]{6,7}\.[\w-]{27,40}$', clean(t)))

def decode_tok(t):
    try:
        p = clean(t).split('.')
        if len(p) != 3: return None
        uid = base64.b64decode(p[0]+'='*(-len(p[0])%4)).decode('utf-8','ignore')
        tb  = base64.b64decode(p[1]+'='*(-len(p[1])%4))
        ms  = int.from_bytes(tb,'big') + 1420070400000
        ca  = datetime.fromtimestamp(ms/1000)
        age = datetime.now() - ca
        return {
            'uid': uid, 'created': ca,
            'years':  age.days // 365,
            'months': (age.days % 365) // 30,
            'days':   age.days % 30,
        }
    except: return None

def mask(t):
    c = clean(t)
    return c[:10]+'·'*18+c[-6:] if len(c)>20 else '·'*len(c)

def _get(ep, t, bot=False):
    pfx = 'Bot ' if bot else ''
    h   = {'Authorization': pfx+clean(t), 'Content-Type':'application/json'}
    return requests.get(f'https://discord.com/api/v10{ep}', headers=h, timeout=10)

def check_token(t):
    try:
        r = _get('/users/@me', t)
        if r.status_code == 200:
            return {'ok':True,'type':'User Token','data':r.json()}
        r2 = _get('/users/@me', t, bot=True)
        if r2.status_code == 200:
            return {'ok':True,'type':'Bot Token','data':r2.json()}
        return {'ok':False,'why':f'HTTP {r.status_code}'}
    except requests.Timeout:
        return {'ok':False,'why':'Timeout — ตรวจสอบเน็ต'}
    except requests.ConnectionError:
        return {'ok':False,'why':'ไม่มีอินเทอร์เน็ต'}
    except Exception as e:
        return {'ok':False,'why':str(e)}

def get_guilds(t, bot=False):
    try:
        r = _get('/users/@me/guilds', t, bot)
        return r.json() if r.status_code==200 else []
    except: return []

def get_connections(t):
    try:
        r = _get('/users/@me/connections', t)
        return r.json() if r.status_code==200 else []
    except: return []

def get_billing(t):
    try:
        r = _get('/users/@me/billing/payment-sources', t)
        return r.json() if r.status_code==200 else []
    except: return []

def get_boosts(t):
    try:
        r = _get('/users/@me/guilds/premium/subscription-slots', t)
        return r.json() if r.status_code==200 else []
    except: return []

def get_relationships(t):
    try:
        r = _get('/users/@me/relationships', t)
        return r.json() if r.status_code==200 else []
    except: return []

# ══════════════════════════════════════════════════════════════════
#  DISPLAY RESULT
# ══════════════════════════════════════════════════════════════════
FLAG_MAP = {
    1:'Staff', 2:'Partner', 4:'HypeSquad Events',
    8:'Bug Hunter Lv1', 64:'Bravery', 128:'Brilliance',
    256:'Balance', 512:'Early Supporter',
    16384:'Bug Hunter Lv2', 131072:'Verified Bot Dev',
    4194304:'Active Dev',
}

CW = 16   # column width สำหรับ label (display width)

def print_decoded(dec):
    title("ข้อมูลจากโทเคน  (Offline Decode)", Cy)
    if dec:
        ok("รูปแบบโทเคน : ถูกต้อง")
        print()
        row('ID', 'User ID',        dec['uid'],  Bl, Wh, CW)
        row('📅', 'สร้างบัญชีเมื่อ', dec['created'].strftime('%Y-%m-%d  %H:%M:%S'), Bl, Ye, CW)
        age = f"{dec['years']} ปี  {dec['months']} เดือน  {dec['days']} วัน"
        row('⏱', 'อายุบัญชี',      age,          Bl, Cy, CW)
    else:
        err("รูปแบบโทเคน : ไม่ถูกต้อง")

def print_online(res, full=False, token=None):
    title("ผลการตรวจสอบออนไลน์  (Discord API)", Ye)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌")
        warn(res.get('why','Unknown error'))
        return False

    d      = res['data']
    is_bot = res['type'] == 'Bot Token'
    disc   = d.get('discriminator','0')
    uname  = f"@{d.get('username','?')}" if disc in ('0',None,'') \
             else f"{d.get('username','?')}#{disc}"

    ok("สถานะ : โทเคนใช้งานได้  ✅")
    print()
    row('>>', 'Token Type', res['type'],       Cy, Wh, CW)
    row('👤', 'Username',   uname,             Bl, Wh, CW)
    row('ID', 'Account ID', d.get('id','?'),   Bl, Wh, CW)

    if is_bot:
        row('🤖', 'ประเภทบัญชี', 'Bot Account', Cy, Cy, CW)
        pub = 'Public  🌐' if d.get('public_flags') else 'Private  🔒'
        row('🌐', 'สถานะบอท',   pub,            Cy, Wh, CW)
    else:
        if d.get('email'):
            ep = d['email'].split('@')
            em = ep[0][:2]+'*****@'+ep[1] if len(ep)==2 else '***'
            row('📧', 'อีเมล', em, Bl, Wh, CW)

        v = d.get('verified', False)
        row('✉', 'ยืนยันอีเมล',
            '✅ ยืนยันแล้ว' if v else '❌ ยังไม่ยืนยัน',
            Bl, Gr if v else Rd, CW)

        if 'mfa_enabled' in d:
            m = d['mfa_enabled']
            row('🔐', '2FA / Two-Factor',
                '✅ เปิดใช้งาน' if m else '❌ ปิดใช้งาน',
                Bl, Gr if m else Rd, CW)

        nitro_map = {
            0: 'ไม่มี Nitro  🆓',
            1: 'Nitro Classic  💎',
            2: 'Nitro  💎',
            3: 'Nitro Basic  💎',
        }
        if 'premium_type' in d:
            nt = d['premium_type']
            row('💠', 'Nitro',
                nitro_map.get(nt, '?'),
                Bl, Cy if nt > 0 else DM, CW)

        if 'phone' in d:
            ph = d['phone']
            row('📱', 'เบอร์โทรศัพท์',
                ph if ph else '❌ ยังไม่ผูกเบอร์',
                Bl, Ye if ph else Rd, CW)

        if 'locale' in d:
            row('🌍', 'Locale', d.get('locale','?'), Bl, Wh, CW)

        pf     = d.get('public_flags', 0)
        badges = [v for k,v in FLAG_MAP.items() if pf & k]
        if badges:
            row('🎖', 'Badges', '  '.join(badges), Mg, Ye, CW)

    if full and token:
        print()
        title("ข้อมูลเพิ่มเติม  (Advanced)", Mg)
        _show_advanced(token, is_bot)

    return True

def _show_advanced(t, is_bot):
    # Guilds
    spin("ดึงรายการเซิร์ฟเวอร์", 1.0)
    guilds = get_guilds(t, is_bot)
    if guilds and isinstance(guilds, list):
        own = sum(1 for g in guilds if g.get('owner'))
        row('🏰', 'เซิร์ฟเวอร์',   f"{len(guilds)} แห่ง", Ye, Ye, CW)
        if own:
            row('👑', 'เป็นเจ้าของ', f"{own} แห่ง",       Ye, Cy, CW)
        for g in guilds[:5]:
            tag = '  [Owner]' if g.get('owner') else ''
            print(f"    {DM}• {g.get('name','?')}{tag}{R}")
        if len(guilds) > 5:
            print(f"    {DM}  ... และอีก {len(guilds)-5} เซิร์ฟเวอร์{R}")
    else:
        info("ดึงข้อมูลเซิร์ฟเวอร์ไม่ได้")

    if not is_bot:
        # Connections
        print()
        spin("ดึง Linked Accounts", 0.8)
        conns = get_connections(t)
        if conns and isinstance(conns, list):
            row('🔗', 'Linked Accounts', f"{len(conns)} บัญชี", Bl, Bl, CW)
            for c in conns:
                vf = '✅' if c.get('verified') else '❌'
                print(f"    {DM}• [{c.get('type','?').upper()}] {c.get('name','?')}  {vf}{R}")
        else:
            info("ไม่มี Linked Accounts")

        # Friends
        print()
        spin("ดึงรายชื่อเพื่อน", 0.8)
        rels = get_relationships(t)
        if rels and isinstance(rels, list):
            friends  = [x for x in rels if x.get('type')==1]
            blocked  = [x for x in rels if x.get('type')==2]
            incoming = [x for x in rels if x.get('type')==3]
            row('👥', 'เพื่อน',        f"{len(friends)} คน",  Gr, Gr, CW)
            if blocked:
                row('🚫', 'บล็อค',    f"{len(blocked)} คน",  Rd, Rd, CW)
            if incoming:
                row('📩', 'คำขอเพื่อน', f"{len(incoming)} คน", Ye, Ye, CW)
        else:
            info("ดึงรายชื่อเพื่อนไม่ได้")

        # Billing
        print()
        spin("ตรวจสอบ Payment Methods", 0.8)
        bills = get_billing(t)
        if bills and isinstance(bills, list):
            row('💳', 'Payment Methods', f"{len(bills)} รายการ", Cy, Cy, CW)
            for b in bills:
                btype = {1:'Card',2:'PayPal',3:'Google Pay'}.get(b.get('type',0),'Unknown')
                l4    = b.get('last_4','')
                exp   = f"{b.get('expires_month','?')}/{b.get('expires_year','?')}"
                vld   = '✅' if b.get('invalid') is False else '⚠'
                print(f"    {DM}• {btype}  {'****'+l4 if l4 else ''}  {exp}  {vld}{R}")
        else:
            info("ไม่มี Payment หรือดึงไม่ได้")

        # Boosts
        print()
        spin("ตรวจสอบ Server Boosts", 0.8)
        boosts = get_boosts(t)
        if boosts and isinstance(boosts, list):
            used   = sum(1 for b in boosts if b.get('premium_guild_subscription'))
            unused = len(boosts) - used
            row('🚀', 'Server Boosts',
                f"รวม {len(boosts)}  ใช้แล้ว {used}  ว่าง {unused}",
                Mg, Mg, CW)
        else:
            info("ไม่มี Server Boosts")

# ══════════════════════════════════════════════════════════════════
#  SAVE REPORT
# ══════════════════════════════════════════════════════════════════
def save_report(token, dec, res):
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = os.path.expanduser(f"~/token_report_{ts}.txt")
    lines = [
        "═"*52,
        "  Discord Token Report",
        f"  วันที่ : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "═"*52,
        f"  Token  : {mask(token)}",
    ]
    if dec:
        lines += [
            f"  User ID     : {dec['uid']}",
            f"  สร้างเมื่อ  : {dec['created'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"  อายุบัญชี   : {dec['years']}y {dec['months']}m {dec['days']}d",
        ]
    if res and res.get('ok'):
        d     = res['data']
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        lines += [
            f"  Type        : {res['type']}",
            f"  Username    : {uname}",
            f"  ID          : {d.get('id','?')}",
            f"  Email       : {d.get('email','N/A')}",
            f"  Verified    : {d.get('verified','?')}",
            f"  MFA         : {d.get('mfa_enabled','?')}",
            f"  Nitro       : {d.get('premium_type','?')}",
            f"  Phone       : {d.get('phone','N/A')}",
        ]
    lines.append("═"*52)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return fname

# ══════════════════════════════════════════════════════════════════
#  INPUT HELPER
# ══════════════════════════════════════════════════════════════════
def get_tok(prompt="ใส่โทเคน Discord"):
    try:
        t = input(f"\n  {BD}{Cy}>>  {prompt}: {R}").strip()
    except EOFError:
        return None
    if not t:
        err("กรุณาใส่โทเคน"); pause("กด Enter เพื่อกลับ"); return None
    return t

# ══════════════════════════════════════════════════════════════════
#  MODES
# ══════════════════════════════════════════════════════════════════
def mode_full():
    banner()
    title("Full Check  —  ตรวจสอบทั้งหมด", Gr)
    info("API + Servers + Friends + Billing + Boosts + Badges")
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        err("รูปแบบโทเคนไม่ถูกต้อง")
        print(f"\n  {Ye}{mask(t)}{R}")
        pause("กด Enter เพื่อกลับ"); return

    spin("กำลังตรวจสอบ Discord API", 1.5)
    dec = decode_tok(t)
    res = check_token(t)

    print_decoded(dec)
    valid = print_online(res, full=True, token=t)

    print(f"\n  {Ye}>> Token: {mask(t)}{R}")

    if valid:
        sv = input(f"\n  {BD}{Cy}>>  บันทึก Report? (y/n): {R}").strip().lower()
        if sv == 'y':
            f = save_report(t, dec, res)
            ok(f"บันทึกแล้วที่: {f}")

    print()
    hr('─', Rd)
    warn("ควร Reset โทเคนทันทีหลังการตรวจสอบ")
    warn("อย่าแชร์โทเคนกับผู้อื่น")
    hr('─', Rd)
    pause()


def mode_offline():
    banner()
    title("Offline Decode  —  ถอดรหัสโทเคน", Ye)
    info("ไม่ใช้อินเทอร์เน็ต  ถอดรหัสข้อมูลจากโทเคนเท่านั้น")
    t = get_tok()
    if not t: return
    spin("ถอดรหัส", 0.7)
    dec = decode_tok(t)
    print_decoded(dec)
    print(f"\n  {Ye}>> Token: {mask(t)}{R}")
    pause()


def mode_fmt():
    banner()
    title("Format Check  —  ตรวจรูปแบบโทเคน", Cy)
    t = get_tok("ใส่โทเคน")
    if not t: return
    is_ok = valid_fmt(t)
    print(); hr()
    if is_ok:
        ok("รูปแบบโทเคนถูกต้อง  ✅")
        p = clean(t).split('.')
        print(f"\n  {Cy}{BD}โครงสร้าง:{R}")
        row('>>', 'Part 1  User ID',    f"{len(p[0])} chars", Bl, Wh, CW)
        row('>>', 'Part 2  Timestamp',  f"{len(p[1])} chars", Bl, Wh, CW)
        row('>>', 'Part 3  HMAC',       f"{len(p[2])} chars", Bl, Wh, CW)
    else:
        err("รูปแบบโทเคนไม่ถูกต้อง  ❌")
        print(f"\n  {Ye}{BD}รูปแบบที่ถูกต้อง:{R}")
        print(f"  {DM}  xxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxx{R}")
        print(f"  {DM}  24-28  .  6-7  .  27-40  chars{R}")
    hr(); pause()


def mode_bulk():
    banner()
    title("Bulk Check  —  เช็คหลายโทเคน", Mg)
    info("ใส่โทเคนทีละบรรทัด  พิมพ์ done หรือ Enter ว่างเพื่อเริ่ม")
    print()
    tokens, i = [], 1
    while True:
        try:
            t = input(f"  {Cy}Token {i}: {R}").strip()
        except EOFError:
            break
        if not t or t.lower() == 'done': break
        tokens.append(t); i += 1

    if not tokens: err("ไม่มีโทเคน"); pause(); return

    ok_list, fail_list = [], []
    for idx, t in enumerate(tokens, 1):
        hr('·', DM)
        print(f"  {BD}[{idx}/{len(tokens)}]{R}  {mask(t)}")
        if not valid_fmt(t):
            err("รูปแบบไม่ถูกต้อง"); fail_list.append(t); continue
        spin("เช็ค", 0.9)
        res = check_token(t)
        if res['ok']:
            d    = res['data']
            disc = d.get('discriminator','0')
            un   = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                   else f"{d.get('username','?')}#{disc}"
            nt   = {0:'Free',1:'Classic',2:'Nitro',3:'Basic'}.get(d.get('premium_type',0),'?')
            mfa  = '🔐' if d.get('mfa_enabled') else ''
            ok(f"VALID  {un}  |  {res['type']}  |  {nt}  {mfa}")
            ok_list.append({'token':t,'username':un,'type':res['type'],'nitro':nt})
        else:
            err(f"INVALID  |  {res.get('why','?')}"); fail_list.append(t)

    print(); hr('═', Mg)
    print(f"\n  {BD}สรุปผล{R}   {Gr}✅ Valid: {len(ok_list)}{R}   {Rd}❌ Invalid: {len(fail_list)}{R}\n")
    hr('═', Mg)

    if ok_list:
        sv = input(f"\n  {BD}{Cy}>>  บันทึก Valid Tokens? (y/n): {R}").strip().lower()
        if sv == 'y':
            ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
            fname = os.path.expanduser(f"~/bulk_valid_{ts}.txt")
            with open(fname,'w',encoding='utf-8') as f:
                for x in ok_list:
                    f.write(f"{x['token']}  |  {x['username']}  |  {x['type']}  |  {x['nitro']}\n")
            ok(f"บันทึกแล้วที่: {fname}")
    pause()


def mode_guilds():
    banner()
    title("Guild List  —  รายการเซิร์ฟเวอร์", Ye)
    t = get_tok()
    if not t: return
    if not valid_fmt(t): err("รูปแบบไม่ถูกต้อง"); pause(); return
    spin("ตรวจสอบโทเคน", 1.0)
    res = check_token(t)
    if not res['ok']: err("โทเคนไม่ถูกต้อง"); pause(); return
    spin("ดึงรายการเซิร์ฟเวอร์", 1.2)
    guilds = get_guilds(t, res['type']=='Bot Token')
    if not guilds or not isinstance(guilds, list):
        info("ไม่พบข้อมูลเซิร์ฟเวอร์"); pause(); return
    hr()
    print(f"\n  {BD}{Ye}พบ {len(guilds)} เซิร์ฟเวอร์{R}\n")
    for idx, g in enumerate(guilds, 1):
        own = f"  {Cy}[Owner]{R}" if g.get('owner') else ''
        print(f"  {DM}{idx:>3}.{R}  {BD}{g.get('name','?')}{R}{own}")
        print(f"       {DM}ID: {g.get('id','?')}{R}")
    hr(); pause()


def mode_quickinfo():
    banner()
    title("Quick Info  —  ข้อมูลบัญชีเร็ว", Bl)
    t = get_tok()
    if not t: return
    spin("ดึงข้อมูล", 1.0)
    dec = decode_tok(t)
    res = check_token(t)
    print_decoded(dec)
    print_online(res, full=False)
    pause()


def show_help():
    banner()
    title("คู่มือการใช้งาน", Cy)
    items = [
        ('1','Full Check',   'เช็คทุกอย่าง API + Servers + Friends + Billing'),
        ('2','Offline',      'ถอดรหัสโทเคน ไม่ใช้อินเทอร์เน็ต'),
        ('3','Format',       'ตรวจรูปแบบโทเคนเท่านั้น'),
        ('4','Bulk Check',   'เช็คหลายโทเคนพร้อมกัน  บันทึกผลได้'),
        ('5','Guild List',   'ดูรายการเซิร์ฟเวอร์ทั้งหมด'),
        ('6','Quick Info',   'ดูข้อมูลบัญชีแบบรวดเร็ว'),
    ]
    for num, name, desc in items:
        print(f"  {Cy}{BD}[{num}]{R}  {BD}{name}{R}")
        print(f"       {DM}{desc}{R}\n")
    hr()
    print(f"  {Gr}{BD}วิธีติดตั้งบน Termux{R}")
    for c in [
        "pkg update && pkg install python",
        "pip install requests",
        "curl -o ~/Checker_Token.py <URL>",
        "python ~/Checker_Token.py",
    ]:
        print(f"  {DM}  $ {c}{R}")
    hr(); pause()

# ══════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════
MENU = [
    ('1','🌐', 'Full Check       (Online + Advanced)', Gr),
    ('2','📴', 'Offline Decode   (ไม่ใช้เน็ต)',        Ye),
    ('3','📋', 'Format Check     (ตรวจรูปแบบ)',        Cy),
    ('4','📦', 'Bulk Check       (หลายโทเคน)',         Mg),
    ('5','🏰', 'Guild List       (รายการเซิร์ฟเวอร์)', Ye),
    ('6','⚡', 'Quick Info       (ข้อมูลเร็ว)',         Bl),
    ('7','📖', 'คู่มือการใช้งาน',                       Wh),
    ('0','🚪', 'ออกจากโปรแกรม',                        Rd),
]
ACTS = {
    '1':mode_full,'2':mode_offline,'3':mode_fmt,
    '4':mode_bulk,'5':mode_guilds,'6':mode_quickinfo,'7':show_help,
}

def main():
    while True:
        banner()
        print(f"  {BD}เลือกโหมด{R}\n")
        hr()
        for num, icon, label, col in MENU:
            hl = BGm if num == '1' else ''
            print(f"  {col}{BD}{hl} {num} {R}  {icon}  {col}{label}{R}")
        hr()
        try:
            ch = input(f"\n  {BD}>>  เลือก (0-7): {R}").strip()
        except EOFError:
            break
        if ch == '0':
            clr()
            print(f"\n  {Gr}>>  ขอบคุณที่ใช้งาน  See you!{R}\n")
            break
        elif ch in ACTS:
            ACTS[ch]()
        else:
            err("กรุณาเลือก 0-7")
            time.sleep(0.8)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Ye}>>  Ctrl+C — ออกจากโปรแกรม{R}\n")
    except Exception as e:
        print(f"\n  {Rd}>>  Error: {e}{R}\n")
