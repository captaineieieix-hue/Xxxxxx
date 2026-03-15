#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, re, base64, time, json
from datetime import datetime

try:
    import requests
except ImportError:
    print("\n[!] ไม่พบ requests  รันคำสั่ง:  pip install requests\n")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════
#  ANSI
# ══════════════════════════════════════════════════════════════════
R  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'

Rd = '\033[91m'
Gr = '\033[92m'
Ye = '\033[93m'
Bl = '\033[94m'
Mg = '\033[95m'
Cy = '\033[96m'
Wh = '\033[97m'

BGb = '\033[44m'
BGc = '\033[46m'
BGm = '\033[45m'

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
#  UI Helpers  (แก้ Thai alignment)
# ══════════════════════════════════════════════════════════════════
W = 54

def clr(): os.system('clear' if os.name != 'nt' else 'cls')

def pause(msg="กด Enter เพื่อดำเนินการต่อ"):
    input(f"\n  {Ye}>>  {msg} ...{R}")

def hr(ch='─', c=Cy):
    print(f"  {c}{ch*W}{R}")

def title(txt, c=Mg):
    print(f"\n  {c}{BD}{'─'*W}{R}")
    print(f"  {c}{BD}  {txt}{R}")
    print(f"  {c}{BD}{'─'*W}{R}\n")

# row แบบ 2 บรรทัด — ไม่มี ljust — ไม่พัง Thai
def row(icon, label, value, lc=Bl, vc=Wh):
    print(f"  {lc}{icon}  {BD}{label}{R}")
    print(f"       {vc}{value}{R}")

# row แบบ 1 บรรทัด — ใช้กับ label ภาษาอังกฤษเท่านั้น
def row1(icon, label, value, lc=Bl, vc=Wh):
    pad = max(20 - len(label), 1)
    print(f"  {lc}{icon}  {BD}{label}{R}{' '*pad}{vc}{value}{R}")

def spin(msg, secs=1.2):
    fr = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    t, i = time.time() + secs, 0
    while time.time() < t:
        print(f"\r  {Cy}{fr[i%10]}{R}  {BD}{msg}...{R}", end='', flush=True)
        time.sleep(0.07); i += 1
    print('\r' + ' '*50 + '\r', end='')

def ok(msg):   print(f"  {Gr}{BD}[+]{R}  {Gr}{msg}{R}")
def err(msg):  print(f"  {Rd}{BD}[-]{R}  {Rd}{msg}{R}")
def info(msg): print(f"  {Cy}{BD}[i]{R}  {msg}{R}")
def warn(msg): print(f"  {Ye}{BD}[!]{R}  {Ye}{msg}{R}")

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
    print(f"  {DM}v4.0  |  Termux Edition  |  No Bot Needed{R}")
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
            'years': age.days//365,
            'months': (age.days%365)//30,
            'days': age.days%30
        }
    except: return None

def mask(t):
    c = clean(t)
    return c[:10]+'·'*18+c[-6:] if len(c)>20 else '·'*len(c)

def _headers(t, bot=False):
    pfx = 'Bot ' if bot else ''
    return {'Authorization': pfx+clean(t), 'Content-Type':'application/json'}

def _get(ep, t, bot=False):
    r = requests.get(
        f'https://discord.com/api/v10{ep}',
        headers=_headers(t, bot), timeout=10)
    return r

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
        return {'ok':False,'why':'No Internet'}
    except Exception as e:
        return {'ok':False,'why':str(e)}

# ── Extra APIs ────────────────────────────────────────────────────
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
#  DISPLAY
# ══════════════════════════════════════════════════════════════════
FLAG_MAP = {
    1:'Staff', 2:'Partner', 4:'HypeSquad Events',
    8:'Bug Hunter Lv1', 64:'HypeSquad Bravery',
    128:'HypeSquad Brilliance', 256:'HypeSquad Balance',
    512:'Early Supporter', 16384:'Bug Hunter Lv2',
    131072:'Verified Bot Dev', 4194304:'Active Dev'
}

def print_decoded(dec):
    title("ข้อมูลจากโทเคน  (Offline Decode)", Cy)
    if dec:
        ok("รูปแบบโทเคน : ถูกต้อง")
        row1('ID','User ID',   dec['uid'], Bl, Wh)
        row ('📅','สร้างบัญชีเมื่อ', dec['created'].strftime('%Y-%m-%d  %H:%M:%S'), Bl, Ye)
        age_str = f"{dec['years']} ปี  {dec['months']} เดือน  {dec['days']} วัน"
        row ('⏱','อายุบัญชี', age_str, Bl, Cy)
    else:
        err("รูปแบบโทเคน : ไม่ถูกต้อง")

def print_online(res, full=False, token=None):
    title("ผลตรวจสอบออนไลน์  (Discord API)", Ye)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌")
        warn(res.get('why','Unknown'))
        return False

    d      = res['data']
    is_bot = res['type']=='Bot Token'
    disc   = d.get('discriminator','0')
    uname  = f"@{d.get('username','?')}" if disc in ('0',None,'') \
             else f"{d.get('username','?')}#{disc}"

    ok("สถานะ : โทเคนใช้งานได้  ✅")
    row1('>>','Token Type', res['type'],  Cy, Wh)
    row1('>>','Username',   uname,        Bl, Wh)
    row1('>>','Account ID', d.get('id','?'), Bl, Wh)

    if is_bot:
        row('>>','ประเภทบัญชี', 'Bot Account  🤖', Cy, Cy)
        pub = 'Public Bot  🌐' if d.get('public_flags') else 'Private Bot  🔒'
        row('>>','สถานะบอท', pub, Cy, Wh)
    else:
        if d.get('email'):
            ep = d['email'].split('@')
            em = ep[0][:2]+'*****@'+ep[1] if len(ep)==2 else '***'
            row('>>','อีเมล', em, Bl, Wh)

        v = d.get('verified',False)
        row('>>','ยืนยันอีเมล',
            '✅ ยืนยันแล้ว' if v else '❌ ยังไม่ยืนยัน', Bl, Gr if v else Rd)

        if 'mfa_enabled' in d:
            m = d['mfa_enabled']
            row('>>','2FA / Two-Factor',
                '✅ เปิดใช้งาน' if m else '❌ ปิดใช้งาน', Bl, Gr if m else Rd)

        nitro_map = {0:'ไม่มี Nitro  🆓',1:'Nitro Classic  💎',
                     2:'Nitro  💎',3:'Nitro Basic  💎'}
        if 'premium_type' in d:
            nt = d['premium_type']
            row('>>','Nitro', nitro_map.get(nt,'?'), Bl, Cy if nt>0 else DM)

        if 'phone' in d:
            ph = d['phone']
            row('>>','เบอร์โทรศัพท์',
                ph if ph else '❌ ไม่ได้ผูกเบอร์', Bl, Ye if ph else Rd)

        if 'locale' in d:
            row1('>>','Locale', d.get('locale','?'), Bl, Wh)

        pf     = d.get('public_flags',0)
        badges = [v for k,v in FLAG_MAP.items() if pf & k]
        if badges:
            row('>>','Badges  🎖', '  |  '.join(badges), Mg, Ye)

    # ── Advanced ─────────────────────────────────────────────────
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
        row('>>','เซิร์ฟเวอร์ที่อยู่', f"{len(guilds)} เซิร์ฟเวอร์", Ye, Ye)
        if own:
            row('>>','เป็นเจ้าของ', f"{own} เซิร์ฟเวอร์  👑", Ye, Cy)
        for g in guilds[:5]:
            tag = '  [Owner]' if g.get('owner') else ''
            print(f"    {DM}• {g.get('name','?')}{tag}{R}")
        if len(guilds)>5:
            print(f"    {DM}  ... และอีก {len(guilds)-5} เซิร์ฟเวอร์{R}")
    else:
        info("ดึงเซิร์ฟเวอร์ไม่ได้ (อาจเป็น Bot Token)")

    if not is_bot:
        # Connections
        print()
        spin("ดึง Linked Accounts", 0.8)
        conns = get_connections(t)
        if conns and isinstance(conns,list):
            row('>>','Linked Accounts', f"{len(conns)} บัญชี  🔗", Bl, Bl)
            for c in conns:
                vf = '✅' if c.get('verified') else '❌'
                print(f"    {DM}• [{c.get('type','?').upper()}] {c.get('name','?')}  {vf}{R}")
        else:
            info("ไม่มี Linked Accounts")

        # Friends
        print()
        spin("ดึงรายชื่อเพื่อน", 0.8)
        rels = get_relationships(t)
        if rels and isinstance(rels,list):
            friends  = [x for x in rels if x.get('type')==1]
            blocked  = [x for x in rels if x.get('type')==2]
            incoming = [x for x in rels if x.get('type')==3]
            row('>>','เพื่อน', f"{len(friends)} คน  👥", Gr, Gr)
            if blocked:
                row('>>','บล็อค', f"{len(blocked)} คน  🚫", Rd, Rd)
            if incoming:
                row('>>','คำขอเพื่อน', f"{len(incoming)} คน  📩", Ye, Ye)
        else:
            info("ดึงรายชื่อเพื่อนไม่ได้")

        # Billing
        print()
        spin("ตรวจสอบ Payment Methods", 0.8)
        bills = get_billing(t)
        if bills and isinstance(bills,list):
            row('>>','Payment Methods', f"{len(bills)} วิธี  💳", Cy, Cy)
            for b in bills:
                btype = {1:'Card',2:'PayPal',3:'Google Pay'}.get(b.get('type',0),'Unknown')
                l4    = b.get('last_4','')
                exp   = f"{b.get('expires_month','?')}/{b.get('expires_year','?')}"
                vld   = '✅' if b.get('invalid') is False else '⚠'
                txt   = f"{btype}  {'****'+l4 if l4 else ''}  exp:{exp}  {vld}"
                print(f"    {DM}• {txt}{R}")
        else:
            info("ไม่มี Payment หรือดึงไม่ได้")

        # Boosts
        print()
        spin("ตรวจสอบ Server Boosts", 0.8)
        boosts = get_boosts(t)
        if boosts and isinstance(boosts,list):
            used   = sum(1 for b in boosts if b.get('premium_guild_subscription'))
            unused = len(boosts)-used
            row('>>','Server Boosts',
                f"รวม {len(boosts)}  |  ใช้แล้ว {used}  |  ว่าง {unused}  🚀", Mg, Mg)
        else:
            info("ไม่มี Server Boosts")

# ══════════════════════════════════════════════════════════════════
#  SAVE REPORT
# ══════════════════════════════════════════════════════════════════
def save_report(token, dec, res):
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = os.path.expanduser(f"~/token_report_{ts}.txt")
    lines = [
        "Discord Token Report",
        f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "="*52,
        f"Token  : {mask(token)}",
    ]
    if dec:
        lines += [
            f"User ID     : {dec['uid']}",
            f"Created     : {dec['created'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"Account Age : {dec['years']}y {dec['months']}m {dec['days']}d",
        ]
    if res and res.get('ok'):
        d = res['data']
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        lines += [
            f"Type        : {res['type']}",
            f"Username    : {uname}",
            f"Account ID  : {d.get('id','?')}",
            f"Email       : {d.get('email','N/A')}",
            f"Verified    : {d.get('verified','?')}",
            f"MFA         : {d.get('mfa_enabled','?')}",
            f"Nitro       : {d.get('premium_type','?')}",
            f"Phone       : {d.get('phone','N/A')}",
        ]
    with open(fname,'w',encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return fname

# ══════════════════════════════════════════════════════════════════
#  INPUT
# ══════════════════════════════════════════════════════════════════
def get_tok(prompt="ใส่โทเคน Discord"):
    t = input(f"\n  {BD}{Cy}>>  {prompt}: {R}").strip()
    if not t:
        err("กรุณาใส่โทเคน"); pause("กด Enter เพื่อกลับ"); return None
    return t

# ══════════════════════════════════════════════════════════════════
#  MODES
# ══════════════════════════════════════════════════════════════════
def mode_full():
    banner()
    title("Full Check  —  ตรวจสอบทุกอย่าง", Gr)
    info("API Check + Servers + Friends + Billing + Boosts")
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        err("รูปแบบโทเคนไม่ถูกต้อง")
        print(f"  {Ye}>> {mask(t)}{R}")
        pause("กด Enter เพื่อกลับ"); return
    spin("กำลังตรวจสอบ Discord API", 1.5)
    dec = decode_tok(t)
    res = check_token(t)
    print_decoded(dec)
    valid = print_online(res, full=True, token=t)
    print(f"\n  {Ye}>> Token (masked): {mask(t)}{R}")
    if valid:
        sv = input(f"\n  {BD}{Cy}>> บันทึก Report? (y/n): {R}").strip().lower()
        if sv == 'y':
            f = save_report(t, dec, res)
            ok(f"บันทึกแล้ว: {f}")
    print()
    hr('─', Rd)
    warn("ควร Reset โทเคนทันทีหลังการตรวจสอบ")
    warn("อย่าแชร์โทเคนกับผู้อื่น")
    hr('─', Rd)
    pause()


def mode_offline():
    banner()
    title("Offline Decode  —  ถอดรหัสโทเคน", Ye)
    info("ไม่ใช้อินเทอร์เน็ต  ถอดรหัสจากโทเคนเท่านั้น")
    t = get_tok()
    if not t: return
    spin("ถอดรหัส", 0.7)
    dec = decode_tok(t)
    print_decoded(dec)
    print(f"\n  {Ye}>> Token (masked): {mask(t)}{R}")
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
        row1('>>','Part 1  (User ID)',    f"{len(p[0])} chars", Bl, Wh)
        row1('>>','Part 2  (Timestamp)',  f"{len(p[1])} chars", Bl, Wh)
        row1('>>','Part 3  (HMAC)',       f"{len(p[2])} chars", Bl, Wh)
    else:
        err("รูปแบบโทเคนไม่ถูกต้อง  ❌")
        print(f"\n  {Ye}{BD}รูปแบบที่ถูกต้อง:{R}")
        print(f"  {DM}  xxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxx{R}")
        print(f"  {DM}  Part1(24-28).Part2(6-7).Part3(27-40){R}")
    hr(); pause()


def mode_bulk():
    banner()
    title("Bulk Check  —  เช็คหลายโทเคน", Mg)
    info("ใส่โทเคนทีละบรรทัด  พิมพ์ done หรือ Enter ว่างเพื่อเริ่ม")
    print()
    tokens, i = [], 1
    while True:
        t = input(f"  {Cy}Token {i}: {R}").strip()
        if not t or t.lower()=='done': break
        tokens.append(t); i += 1

    if not tokens: err("ไม่มีโทเคน"); pause(); return

    ok_list, fail_list = [], []
    for idx, t in enumerate(tokens,1):
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
            mfa  = '🔐' if d.get('mfa_enabled') else '  '
            ok(f"VALID  |  {un}  |  {res['type']}  |  Nitro:{nt}  {mfa}")
            ok_list.append({'token':t,'username':un,'type':res['type'],'nitro':nt})
        else:
            err(f"INVALID  |  {res.get('why','?')}"); fail_list.append(t)

    print(); hr('═',Mg)
    print(f"  {BD}สรุปผล{R}   {Gr}Valid: {len(ok_list)}{R}  |  {Rd}Invalid: {len(fail_list)}{R}")
    hr('═',Mg)

    if ok_list:
        sv = input(f"\n  {BD}{Cy}>> บันทึก Valid Tokens? (y/n): {R}").strip().lower()
        if sv == 'y':
            ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
            fname = os.path.expanduser(f"~/bulk_valid_{ts}.txt")
            with open(fname,'w',encoding='utf-8') as f:
                for x in ok_list:
                    f.write(f"{x['token']}  |  {x['username']}  |  {x['type']}  |  Nitro:{x['nitro']}\n")
            ok(f"บันทึกแล้ว: {fname}")
    pause()


def mode_guilds():
    banner()
    title("Guild List  —  ดูรายการเซิร์ฟเวอร์", Ye)
    t = get_tok()
    if not t: return
    if not valid_fmt(t): err("รูปแบบไม่ถูกต้อง"); pause(); return
    spin("ตรวจสอบโทเคน", 1.0)
    res = check_token(t)
    if not res['ok']: err("โทเคนไม่ถูกต้อง"); pause(); return
    is_bot = res['type']=='Bot Token'
    spin("ดึงรายการเซิร์ฟเวอร์", 1.2)
    guilds = get_guilds(t, is_bot)
    if not guilds or not isinstance(guilds,list):
        info("ไม่พบข้อมูลเซิร์ฟเวอร์"); pause(); return
    hr()
    print(f"  {BD}{Ye}พบ {len(guilds)} เซิร์ฟเวอร์{R}\n")
    for idx, g in enumerate(guilds,1):
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
        ("1","Full Check",   "เช็คทุกอย่าง API + Servers + Friends + Billing + Boosts"),
        ("2","Offline",      "ถอดรหัสโทเคน ไม่ใช้อินเทอร์เน็ต"),
        ("3","Format",       "ตรวจรูปแบบโทเคนเท่านั้น"),
        ("4","Bulk Check",   "เช็คหลายโทเคนพร้อมกัน  บันทึกผลได้"),
        ("5","Guild List",   "ดูรายการเซิร์ฟเวอร์ทั้งหมด"),
        ("6","Quick Info",   "ดูข้อมูลบัญชีแบบรวดเร็ว"),
    ]
    for num, name, desc in items:
        print(f"  {Cy}{BD}[{num}]{R}  {BD}{name}{R}")
        print(f"       {DM}{desc}{R}\n")
    hr()
    print(f"  {Gr}{BD}วิธีติดตั้งบน Termux{R}")
    cmds = [
        "pkg update && pkg install python",
        "pip install requests",
        "curl -o ~/Checker_Token.py <GitHub Raw URL>",
        "python ~/Checker_Token.py",
    ]
    for c in cmds:
        print(f"  {DM}  $ {c}{R}")
    hr(); pause()

# ══════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════
MENU = [
    ('1','🌐','Full Check       (Online + Advanced)', Gr),
    ('2','📴','Offline Decode   (ไม่ใช้เน็ต)',        Ye),
    ('3','📋','Format Check     (ตรวจรูปแบบ)',        Cy),
    ('4','📦','Bulk Check       (หลายโทเคน)',         Mg),
    ('5','🏰','Guild List       (รายการเซิร์ฟเวอร์)', Ye),
    ('6','⚡','Quick Info       (ข้อมูลเร็ว)',         Bl),
    ('7','📖','คู่มือการใช้งาน',                       Wh),
    ('0','🚪','ออกจากโปรแกรม',                        Rd),
]
ACTS = {
    '1':mode_full,'2':mode_offline,'3':mode_fmt,
    '4':mode_bulk,'5':mode_guilds,'6':mode_quickinfo,'7':show_help
}

def main():
    while True:
        banner()
        print(f"  {BD}เลือกโหมด{R}\n")
        hr()
        for num, icon, label, col in MENU:
            hl = BGm if num=='1' else ''
            print(f"  {col}{BD}{hl} {num} {R}  {icon}  {col}{label}{R}")
        hr()
        ch = input(f"\n  {BD}>>  เลือก: {R}").strip()
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
