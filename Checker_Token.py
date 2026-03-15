#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════╗
║   Discord Token Checker  v5.1  —  Termux Edition    ║
║   Advanced Scanner  •  Thai Support  •  No Bot      ║
╚══════════════════════════════════════════════════════╝
"""

import sys, os, re, base64, time, json
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

try:
    import requests
except ImportError:
    print("\n  [!]  ไม่พบ requests\n       pip install requests\n")
    sys.exit(1)

# ╔══════════════════════════════════════════════════════╗
# ║  ANSI Color Palette                                  ║
# ╚══════════════════════════════════════════════════════╝
R   = '\033[0m'
BD  = '\033[1m'
DM  = '\033[2m'
IT  = '\033[3m'
UL  = '\033[4m'
BL  = '\033[5m'   # blink (not all terminals)

Bk  = '\033[30m'
Rd  = '\033[91m'
Gr  = '\033[92m'
Ye  = '\033[93m'
Bl  = '\033[94m'
Mg  = '\033[95m'
Cy  = '\033[96m'
Wh  = '\033[97m'

BGk = '\033[40m'
BGr = '\033[41m'
BGg = '\033[42m'
BGy = '\033[43m'
BGb = '\033[44m'
BGm = '\033[45m'
BGc = '\033[46m'
BGw = '\033[47m'

# Gradient palettes
_GRAD_MAIN  = ['\033[95m','\033[94m','\033[96m','\033[94m','\033[95m']
_GRAD_FIRE  = ['\033[91m','\033[93m','\033[92m','\033[93m','\033[91m']
_GRAD_ICE   = ['\033[96m','\033[94m','\033[97m','\033[94m','\033[96m']
_GRAD_GOLD  = ['\033[93m','\033[97m','\033[93m','\033[97m','\033[93m']

def _grad(text, palette=None):
    p = palette or _GRAD_MAIN
    out, i = '', 0
    for ch in text:
        if ch.strip():
            out += p[i % len(p)] + ch; i += 1
        else:
            out += ch
    return out + R

# ╔══════════════════════════════════════════════════════╗
# ║  UI Constants                                        ║
# ╚══════════════════════════════════════════════════════╝
W  = 52   # content width
BW = W+4  # box width

def clr(): os.system('clear' if os.name != 'nt' else 'cls')

def _inp(prompt):
    try: return input(prompt).strip()
    except EOFError: return ''

def pause(msg="กด Enter เพื่อดำเนินการต่อ"):
    _inp(f"\n  {DM}{'─'*W}{R}\n  {Ye}  {msg}{R}\n  {DM}{'─'*W}{R}\n")

def blank(): print()

# ── Dividers ──────────────────────────────────────────
def hr(ch='─', c=DM):
    print(f"  {c}{ch*W}{R}")

def hr_thick(c=Cy):
    print(f"  {c}{'═'*W}{R}")

def hr_dot(c=DM):
    print(f"  {c}{'·'*W}{R}")

# ── Box drawing ───────────────────────────────────────
def box_top(c=Cy, ch='─'):
    print(f"  {c}╭{'─'*W}╮{R}")

def box_bot(c=Cy):
    print(f"  {c}╰{'─'*W}╯{R}")

def box_row(text, c=Cy, tc=Wh, pad=1):
    inner  = W - pad*2
    line   = text[:inner] if len(text) > inner else text
    spaces = inner - len(line)
    print(f"  {c}│{R}{' '*pad}{tc}{line}{R}{' '*spaces}{' '*pad}{c}│{R}")

def box_row_raw(content, c=Cy):
    """ใช้กับ content ที่มี ANSI แล้ว — ไม่ตัด"""
    print(f"  {c}│{R}  {content}  {c}│{R}")

# ── Fancy Title ───────────────────────────────────────
def title(txt, c=Mg, icon=''):
    blank()
    print(f"  {c}╔{'═'*W}╗{R}")
    label = f"  {icon+'  ' if icon else ''}{txt}"
    pad   = W - len(label)
    print(f"  {c}║{R}{BD}{c}{label}{' '*max(pad,1)}{R}{c}║{R}")
    print(f"  {c}╚{'═'*W}╝{R}")
    blank()

# ── Section header ────────────────────────────────────
def section(txt, c=Bl, icon='▸'):
    blank()
    inner = f" {icon} {txt} "
    bar   = '─' * max(W - len(inner) - 2, 4)
    print(f"  {c}{BD}┌─{inner}{'─'*len(bar)}┐{R}")

def section_end(c=Bl):
    print(f"  {c}{'─'*W}{R}")

# ── Status messages ───────────────────────────────────
def ok(msg):
    print(f"  {BGg}{Bk}{BD} ✔ {R}  {Gr}{BD}{msg}{R}")

def err(msg):
    print(f"  {BGr}{Wh}{BD} ✘ {R}  {Rd}{BD}{msg}{R}")

def info(msg):
    print(f"  {BGb}{Wh}{BD} i {R}  {Bl}{msg}{R}")

def warn(msg):
    print(f"  {BGy}{Bk}{BD} ! {R}  {Ye}{msg}{R}")

def found(msg):
    print(f"  {BGm}{Wh}{BD} * {R}  {Mg}{BD}{msg}{R}")

def tag_ok(txt):   return f"{BGg}{Bk}{BD} {txt} {R}"
def tag_err(txt):  return f"{BGr}{Wh}{BD} {txt} {R}"
def tag_info(txt): return f"{BGb}{Wh}{BD} {txt} {R}"
def tag_dim(txt):  return f"{BGk}{DM} {txt} {R}"

# ── Data rows (Thai-safe 2-line) ──────────────────────
def row(icon, label, value, lc=Bl, vc=Wh):
    print(f"  {lc}{BD}{icon}  {label}{R}")
    print(f"    {DM}└─{R}  {vc}{value}{R}")

def rowA(icon, label, value, lc=Bl, vc=Wh):
    """ASCII-label inline row"""
    pad = max(18 - len(label), 1)
    print(f"  {lc}{BD}{icon}  {label}{R}{'·'*pad}{vc}{value}{R}")

def bullet(txt, c=DM):
    print(f"      {c}◦  {txt}{R}")

def kv(k, v, kc=DM, vc=Wh):
    """compact key:value"""
    print(f"  {kc}{k}:{R}  {vc}{v}{R}")

# ── Progress bar ──────────────────────────────────────
def progress(current, total, width=30, c=Gr):
    pct   = current / total if total > 0 else 0
    filled= int(width * pct)
    bar   = '█' * filled + '░' * (width - filled)
    print(f"\r  {c}[{bar}]{R}  {BD}{current}/{total}{R}", end='', flush=True)

# ── Spinner ───────────────────────────────────────────
_SPINNERS = {
    'dots':   ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'],
    'line':   ['─','╲','│','╱'],
    'star':   ['✶','✸','✹','✺','✹','✷'],
    'pulse':  ['▁','▂','▃','▄','▅','▆','▇','█','▇','▆','▅','▄','▃','▂'],
    'arrow':  ['>','>>','>>>','>>>','>>','>'],
}

def spin(msg, secs=1.2, style='dots', c=Cy):
    fr  = _SPINNERS.get(style, _SPINNERS['dots'])
    end = time.time() + secs; i = 0
    while time.time() < end:
        f = fr[i % len(fr)]
        print(f"\r  {c}{BD}{f}{R}  {DM}{msg}...{R}   ", end='', flush=True)
        time.sleep(0.08); i += 1
    print('\r' + ' '*60 + '\r', end='')

def spin_done(msg, c=Gr):
    print(f"  {c}{BD}✔{R}  {DM}{msg}{R}")

# ╔══════════════════════════════════════════════════════╗
# ║  Banner                                              ║
# ╚══════════════════════════════════════════════════════╝
_ART_DISCORD = r"""
 ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗
 ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
 ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
 ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
 ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
 ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝"""

_ART_TOKEN = r"""
 ████████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗
 ╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║
    ██║   ██║   ██║█████╔╝ █████╗  ██╔██╗ ██║
    ██║   ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║
    ██║   ╚██████╔╝██║  ██╗███████╗██║ ╚████║
    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝"""

def banner():
    clr()
    for line in _ART_DISCORD.split('\n'):
        print(_grad(line, _GRAD_MAIN))
    for line in _ART_TOKEN.split('\n'):
        print(_grad(line, _GRAD_ICE))
    blank()
    # Info bar
    now    = datetime.now().strftime('%H:%M:%S')
    lline  = f"  v5.1  ·  Termux Edition  ·  Advanced Scanner"
    rline  = f"  {now}"
    spaces = W - len(lline) + 4 - len(rline) + 4
    print(f"  {DM}╔{'═'*W}╗")
    print(f"  ║{R}{Cy}{lline}{R}{DM}{' '*max(spaces,1)}{rline}  {DM}║")
    print(f"  ╚{'═'*W}╝{R}")
    blank()

# ╔══════════════════════════════════════════════════════╗
# ║  Token Core                                          ║
# ╚══════════════════════════════════════════════════════╝
def clean(t): return t.replace('Bot ', '').strip()

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
            'days': age.days%30,
        }
    except: return None

def mask(t):
    c = clean(t)
    return c[:10]+'·'*18+c[-6:] if len(c)>20 else '·'*len(c)

# ── API Layer ─────────────────────────────────────────
BASE = 'https://discord.com/api/v10'

def _req(ep, t, bot=False, method='GET', data=None, params=None):
    pfx = 'Bot ' if bot else ''
    h   = {'Authorization': pfx+clean(t), 'Content-Type':'application/json'}
    url = BASE+ep
    try:
        if   method == 'GET':    return requests.get   (url, headers=h, timeout=10, params=params)
        elif method == 'PATCH':  return requests.patch (url, headers=h, json=data,  timeout=10)
        elif method == 'POST':   return requests.post  (url, headers=h, json=data,  timeout=10)
        elif method == 'DELETE': return requests.delete(url, headers=h,             timeout=10)
    except: return None

def _safe(ep, t, bot=False, params=None):
    try:
        r = _req(ep, t, bot, params=params)
        return r.json() if r and r.status_code==200 else []
    except: return []

def check_token(t):
    try:
        r = _req('/users/@me', t)
        if r and r.status_code==200:
            return {'ok':True,'type':'User Token','data':r.json()}
        r2 = _req('/users/@me', t, bot=True)
        if r2 and r2.status_code==200:
            return {'ok':True,'type':'Bot Token','data':r2.json()}
        return {'ok':False,'why':f"HTTP {r.status_code if r else '?'}"}
    except requests.Timeout:      return {'ok':False,'why':'Timeout'}
    except requests.ConnectionError: return {'ok':False,'why':'ไม่มีอินเทอร์เน็ต'}
    except Exception as e:        return {'ok':False,'why':str(e)}

# ── Advanced API ──────────────────────────────────────
def api_guilds(t,b=False):      return _safe('/users/@me/guilds',t,b) or []
def api_connections(t):         return _safe('/users/@me/connections',t) or []
def api_billing(t):             return _safe('/users/@me/billing/payment-sources',t) or []
def api_boosts(t):              return _safe('/users/@me/guilds/premium/subscription-slots',t) or []
def api_relationships(t):       return _safe('/users/@me/relationships',t) or []
def api_dms(t):                 return _safe('/users/@me/channels',t) or []
def api_gifts(t):               return _safe('/users/@me/entitlements/gifts',t) or []
def api_settings(t):
    r = _req('/users/@me/settings',t); return r.json() if r and r.status_code==200 else {}
def api_applications(t):        return _safe('/oauth2/tokens',t) or []
def api_activities(t):
    r = _req('/users/@me/activities/statistics/applications',t)
    return r.json() if r and r.status_code==200 else []
def api_check_gift(code,t):
    r = _req(f'/entitlements/gift-codes/{code}',t)
    return r.json() if r and r.status_code==200 else None
def api_hypesquad_edit(t,house_id):
    r = _req('/hypesquad/online',t,method='POST',data={'house_id':house_id})
    return r and r.status_code==204

# ── Lookups ───────────────────────────────────────────
FLAG_MAP = {
    1:'Discord Staff',2:'Partner',4:'HypeSquad Events',
    8:'Bug Hunter L1',64:'Bravery',128:'Brilliance',
    256:'Balance',512:'Early Supporter',16384:'Bug Hunter L2',
    131072:'Verified Bot Dev',4194304:'Active Dev',
}
NITRO = {0:'None',1:'Nitro Classic',2:'Nitro',3:'Nitro Basic'}
HOUSE = {1:'Bravery',2:'Brilliance',3:'Balance'}

def avatar_url(uid,h):
    if not h: return 'ไม่มี Avatar'
    ext = 'gif' if h.startswith('a_') else 'png'
    return f"https://cdn.discordapp.com/avatars/{uid}/{h}.{ext}?size=512"

def banner_url(uid,h):
    if not h: return None
    ext = 'gif' if h.startswith('a_') else 'png'
    return f"https://cdn.discordapp.com/banners/{uid}/{h}.{ext}?size=512"

def fmt_ts(ts):
    try:
        dt = datetime.fromisoformat(str(ts).replace('Z','+00:00'))
        return dt.strftime('%Y-%m-%d  %H:%M:%S')
    except: return str(ts)

# ╔══════════════════════════════════════════════════════╗
# ║  Display — Base Info                                 ║
# ╚══════════════════════════════════════════════════════╝
def print_base_info(d, res_type, dec=None):
    disc  = d.get('discriminator','0')
    uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
            else f"{d.get('username','?')}#{disc}"
    is_bot = res_type == 'Bot Token'

    # ── Header card ──────────────────────────────────
    blank()
    print(f"  {Cy}╔{'═'*W}╗{R}")
    t_type = tag_ok('USER') if not is_bot else tag_info('BOT')
    print(f"  {Cy}║{R}  {t_type}  {BD}{Wh}{uname}{R}{Cy}{'':>{W-len(uname)-10}}║{R}")
    print(f"  {Cy}║{R}  {DM}ID: {d.get('id','?')}{Cy}{'':>{W-len(str(d.get('id','?')))-6}}║{R}")
    if dec:
        ca_str = dec['created'].strftime('%Y-%m-%d  %H:%M:%S')
        age_str= f"{dec['years']}y {dec['months']}m {dec['days']}d"
        print(f"  {Cy}║{R}  {DM}Created: {ca_str}   Age: {age_str}{Cy}{'':>2}║{R}")
    print(f"  {Cy}╚{'═'*W}╝{R}")
    blank()

    if not is_bot:
        av = avatar_url(d.get('id',''), d.get('avatar'))
        kv('Avatar', av, DM, DM)
        bn = banner_url(d.get('id',''), d.get('banner'))
        if bn: kv('Banner', bn, DM, DM)
        bio = d.get('bio','') or d.get('global_name','')
        if bio: kv('Bio', bio, DM, Wh)

    return is_bot

# ╔══════════════════════════════════════════════════════╗
# ║  Scan Modules                                        ║
# ╚══════════════════════════════════════════════════════╝

def _sec_score_bar(score, total=4):
    colors = [Rd, Rd, Ye, Gr, Gr]
    c      = colors[score]
    filled = '█' * score
    empty  = '░' * (total - score)
    return f"{c}{BD}{filled}{DM}{empty}{R}  {c}{BD}{score}/{total}{R}"

def scan_security(t, d):
    section("Security Audit", Rd, '🛡')
    blank()
    v  = d.get('verified',False)
    m  = d.get('mfa_enabled',False)
    ph = d.get('phone')
    em = d.get('email')

    row('✉', 'ยืนยันอีเมล',
        (tag_ok('ยืนยันแล้ว') if v else tag_err('ยังไม่ยืนยัน')), Bl, Wh)
    row('🔐','2FA',
        (tag_ok('เปิดใช้งาน') if m else tag_err('ปิด — บัญชีเสี่ยง!')), Bl, Wh)
    row('📱','เบอร์โทรศัพท์',
        ph if ph else tag_err('ไม่ได้ผูกเบอร์'), Bl, Ye if ph else Wh)
    if em:
        ep = em.split('@')
        masked_em = ep[0][:2]+'*****@'+ep[1] if len(ep)==2 else '***'
        row('📧','อีเมล', masked_em, Bl, Wh)

    score  = sum([bool(v),bool(m),bool(ph),bool(em)])
    blank()
    print(f"  {Bl}{BD}Security Score{R}  {_sec_score_bar(score)}")
    section_end(Rd)

def scan_nitro(t, d):
    section("Nitro & Boosts", Cy, '💎')
    blank()
    nt = d.get('premium_type',0)
    nc = Cy if nt>0 else DM
    print(f"  {nc}{BD}Nitro:{R}  {nc}{NITRO.get(nt,'?')}{R}")
    if d.get('premium_since'):
        kv('Since', fmt_ts(d['premium_since']), DM, Wh)
    blank()

    spin("ดึง Server Boosts", 0.8, 'pulse', Cy)
    boosts = api_boosts(t)
    if boosts and isinstance(boosts,list):
        used   = sum(1 for b in boosts if b.get('premium_guild_subscription'))
        unused = len(boosts)-used
        row('🚀','Server Boosts',
            f"{Mg}{BD}{len(boosts)} total{R}  {DM}|{R}  {Gr}used:{used}{R}  {DM}|{R}  {Cy}free:{unused}{R}", Mg, Wh)
        for b in boosts:
            s = b.get('premium_guild_subscription')
            if s: bullet(f"→ Guild {s.get('guild_id','?')}  since {fmt_ts(s.get('started_at',''))}", Mg)
    else:
        info("ไม่มี Server Boosts")

    spin("ตรวจสอบ Nitro Gifts", 0.7, 'star', Ye)
    gifts = api_gifts(t)
    if gifts and isinstance(gifts,list):
        found(f"พบ Nitro Gift {len(gifts)} รายการ !")
        for g in gifts: bullet(f"ID: {g.get('id','?')}  SKU: {g.get('sku_id','?')}", Ye)
    else:
        info("ไม่มี Nitro Gift")
    section_end(Cy)

def scan_guilds(t, is_bot):
    section("Server Scan", Ye, '🏰')
    blank()
    spin("ดึงรายการเซิร์ฟเวอร์", 1.0, 'dots', Ye)
    guilds = api_guilds(t, is_bot)
    if not guilds or not isinstance(guilds,list):
        info("ดึงข้อมูลเซิร์ฟเวอร์ไม่ได้"); return

    own_c   = sum(1 for g in guilds if g.get('owner'))
    adm_c   = sum(1 for g in guilds if int(g.get('permissions','0'))&0x8)

    print(f"  {Ye}{BD}เซิร์ฟเวอร์ทั้งหมด:{R}  {Wh}{BD}{len(guilds)}{R}  "
          f"{DM}|{R}  {Cy}Owner:{own_c}{R}  {DM}|{R}  "
          f"{''+Rd if adm_c else DM}Admin:{adm_c}{R}")
    blank()

    for g in guilds[:8]:
        perms = int(g.get('permissions','0'))
        tags  = []
        if g.get('owner'):   tags.append(tag_ok('Owner'))
        if perms & 0x8:      tags.append(tag_err('Admin'))
        if perms & 0x4:      tags.append(tag_err('Ban'))
        if perms & 0x2:      tags.append(tag_info('Kick'))
        if perms & 0x20:     tags.append(tag_dim('Manage'))
        tag_str = ' '.join(tags) if tags else tag_dim('Member')
        hr_dot()
        print(f"  {BD}{Wh}{g.get('name','?')}{R}  {tag_str}")
        print(f"  {DM}  └─ ID: {g.get('id','?')}{R}")

    if len(guilds)>8:
        blank(); info(f"... และอีก {len(guilds)-8} เซิร์ฟเวอร์")
    section_end(Ye)

def scan_friends(t):
    section("Friends & Relationships", Gr, '👥')
    blank()
    spin("ดึงรายชื่อเพื่อน", 0.8, 'dots', Gr)
    rels = api_relationships(t)
    if not rels or not isinstance(rels,list):
        info("ดึงข้อมูลเพื่อนไม่ได้"); return

    friends  = [x for x in rels if x.get('type')==1]
    blocked  = [x for x in rels if x.get('type')==2]
    incoming = [x for x in rels if x.get('type')==3]
    outgoing = [x for x in rels if x.get('type')==4]

    stats = (f"  {Gr}{BD}เพื่อน:{len(friends)}{R}  "
             f"{Rd}บล็อค:{len(blocked)}{R}  "
             f"{Ye}ขาเข้า:{len(incoming)}{R}  "
             f"{Bl}ขาออก:{len(outgoing)}{R}")
    print(stats); blank()

    if friends:
        info(f"เพื่อน {min(5,len(friends))} คนล่าสุด:")
        for f in friends[:5]:
            u    = f.get('user',{})
            disc = u.get('discriminator','0')
            un   = f"@{u.get('username','?')}" if disc in ('0',None,'') \
                   else f"{u.get('username','?')}#{disc}"
            bullet(f"{Wh}{BD}{un}{R}  {DM}({u.get('id','?')}){R}", Wh)

    if incoming:
        blank(); found(f"คำขอเพื่อน {len(incoming)} คนรอตอบรับ !")
        for f in incoming[:3]:
            u    = f.get('user',{})
            disc = u.get('discriminator','0')
            un   = f"@{u.get('username','?')}" if disc in ('0',None,'') \
                   else f"{u.get('username','?')}#{disc}"
            bullet(un, Ye)
    section_end(Gr)

def scan_dms(t):
    section("Direct Messages", Bl, '💬')
    blank()
    spin("ดึง DM Channels", 0.8, 'line', Bl)
    dms = api_dms(t)
    if not dms or not isinstance(dms,list):
        info("ดึงข้อมูล DM ไม่ได้"); return

    row('💬','DM Channels', f"{Bl}{BD}{len(dms)}{R} ช่อง", Bl, Wh)
    blank()
    for ch in dms[:6]:
        if ch.get('type')==1:
            rec  = ch.get('recipients',[{}])[0] if ch.get('recipients') else {}
            disc = rec.get('discriminator','0')
            un   = f"@{rec.get('username','?')}" if disc in ('0',None,'') \
                   else f"{rec.get('username','?')}#{disc}"
            print(f"  {tag_info('DM')}  {BD}{Wh}{un}{R}  {DM}ch:{ch.get('id','?')}{R}")
        elif ch.get('type')==3:
            name = ch.get('name') or f"Group ({len(ch.get('recipients',[]))+1})"
            print(f"  {tag_dim('GDM')}  {BD}{Mg}{name}{R}  {DM}ch:{ch.get('id','?')}{R}")
    if len(dms)>6: info(f"... และอีก {len(dms)-6} ช่อง")
    section_end(Bl)

def scan_connections(t):
    section("Linked Accounts", Mg, '🔗')
    blank()
    spin("ดึง Linked Accounts", 0.8, 'dots', Mg)
    conns = api_connections(t)
    if not conns or not isinstance(conns,list):
        info("ไม่มี Linked Accounts"); return

    row('🔗','Linked Accounts', f"{Mg}{BD}{len(conns)}{R} บัญชี", Mg, Wh)
    blank()
    for c in conns:
        vf  = tag_ok('✔') if c.get('verified') else tag_err('✘')
        vis = f"{DM}Public{R}" if c.get('visibility')==1 else f"{DM}Private{R}"
        print(f"  {tag_info(c.get('type','?').upper())}  {BD}{Wh}{c.get('name','?')}{R}  {vf}  {vis}")
    section_end(Mg)

def scan_billing(t):
    section("Payment & Billing", Ye, '💳')
    blank()
    spin("ดึง Payment Methods", 0.8, 'pulse', Ye)
    bills = api_billing(t)
    if not bills or not isinstance(bills,list):
        info("ไม่มี Payment หรือดึงไม่ได้"); return

    found(f"พบ Payment Methods {len(bills)} รายการ !")
    blank()
    bmap = {1:'Credit/Debit Card',2:'PayPal',3:'Google Pay',4:'Apple Pay'}
    for b in bills:
        btype = bmap.get(b.get('type',0),'Unknown')
        l4    = b.get('last_4','')
        exp   = f"{b.get('expires_month','?')}/{b.get('expires_year','?')}"
        vld   = tag_ok('Valid') if b.get('invalid') is False else tag_err('Invalid')
        dflt  = f"  {tag_dim('Default')}" if b.get('default') else ''
        hr_dot()
        print(f"  {Ye}{BD}{btype}{R}  {'****'+l4 if l4 else ''}{dflt}")
        print(f"  {DM}  └─ Expire: {exp}  {vld}{R}")
    section_end(Ye)

def scan_settings(t):
    section("Account Settings", Cy, '⚙')
    blank()
    spin("ดึง Settings", 0.8, 'arrow', Cy)
    s = api_settings(t)
    if not s: info("ดึง Settings ไม่ได้"); return

    rowA('--','Locale',         s.get('locale','?'),  Bl, Wh)
    rowA('--','Theme',          s.get('theme','?'),   Bl, Wh)
    rowA('--','Status',         s.get('status','?'),  Bl, Ye)
    rowA('--','Dev Mode',       tag_ok('On') if s.get('developer_mode') else tag_err('Off'), Bl, Wh)
    rowA('--','GIF AutoPlay',   tag_ok('On') if s.get('gif_auto_play')  else tag_dim('Off'), Bl, Wh)
    rowA('--','Animate Emoji',  tag_ok('On') if s.get('animate_emojis') else tag_dim('Off'), Bl, Wh)
    em = {0:'ปิด',1:'เพื่อนไม่มี role',2:'เปิดทุก DM'}
    rowA('--','Explicit Filter', em.get(s.get('explicit_content_filter',0),'?'), Bl, Wh)
    section_end(Cy)

def scan_apps(t):
    section("Authorized Apps", Mg, '🔌')
    blank()
    spin("ดึง Authorized Apps", 0.8, 'dots', Mg)
    apps = api_applications(t)
    if not apps or not isinstance(apps,list):
        info("ไม่มี Authorized Apps"); return

    row('🔌','Authorized Apps', f"{Mg}{BD}{len(apps)}{R} แอป", Mg, Wh)
    blank()
    for a in apps[:8]:
        app    = a.get('application',{})
        name   = app.get('name','?')
        scopes = ', '.join(a.get('scopes',[]))
        hr_dot()
        print(f"  {Mg}{BD}{name}{R}")
        print(f"  {DM}  └─ Scopes: {scopes}{R}")
    if len(apps)>8: info(f"... และอีก {len(apps)-8} แอป")
    section_end(Mg)

def scan_activities(t):
    section("Game / Activity Stats", Bl, '🎮')
    blank()
    spin("ดึง Activity Stats", 0.8, 'dots', Bl)
    acts = api_activities(t)
    if not acts or not isinstance(acts,list):
        info("ไม่มีข้อมูล Activities"); return

    row('🎮','Apps / Games', f"{Bl}{BD}{len(acts)}{R} รายการ", Bl, Wh)
    blank()
    for a in acts[:6]:
        total  = a.get('total_duration',0)
        h, m   = total//3600, (total%3600)//60
        app_id = a.get('application_id','?')
        hr_dot()
        print(f"  {Bl}AppID: {app_id}{R}  {DM}{h}h {m}m{R}")
    section_end(Bl)

# ╔══════════════════════════════════════════════════════╗
# ║  Save Report                                         ║
# ╚══════════════════════════════════════════════════════╝
def save_report(token, dec, res, extra=None):
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = os.path.expanduser(f"~/token_report_{ts}.txt")
    L     = ['═'*52,
             '  Discord Token Report  v5.1',
             f"  Date     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             '═'*52,
             f"  Token    : {mask(token)}"]
    if dec:
        L += [f"  UserID   : {dec['uid']}",
              f"  Created  : {dec['created'].strftime('%Y-%m-%d %H:%M:%S')}",
              f"  Age      : {dec['years']}y {dec['months']}m {dec['days']}d"]
    if res and res.get('ok'):
        d     = res['data']
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        pf    = d.get('public_flags',0)
        badges= [v for k,v in FLAG_MAP.items() if pf&k]
        L += [f"  Type     : {res['type']}",
              f"  Username : {uname}",
              f"  ID       : {d.get('id','?')}",
              f"  Email    : {d.get('email','N/A')}",
              f"  Phone    : {d.get('phone','N/A')}",
              f"  Verified : {d.get('verified','?')}",
              f"  MFA      : {d.get('mfa_enabled','?')}",
              f"  Nitro    : {NITRO.get(d.get('premium_type',0),'?')}",
              f"  Avatar   : {avatar_url(d.get('id',''),d.get('avatar'))}"]
        if badges: L.append(f"  Badges   : {', '.join(badges)}")
    if extra: L += ['','── Additional Info ──'] + extra
    L.append('═'*52)
    with open(fname,'w',encoding='utf-8') as f: f.write('\n'.join(L))
    return fname

# ╔══════════════════════════════════════════════════════╗
# ║  Input helpers                                       ║
# ╚══════════════════════════════════════════════════════╝
def get_tok(prompt="ใส่โทเคน Discord"):
    blank()
    print(f"  {DM}┌─ Token Input {'─'*(W-14)}┐{R}")
    t = _inp(f"  {DM}│{R}  {Cy}{BD}{prompt}{R}  {DM}│{R}\n  {DM}└{'─'*W}┘{R}\n  {Cy}> {R}")
    if not t:
        err("กรุณาใส่โทเคน"); pause("กด Enter เพื่อกลับ"); return None
    return t

def ask(prompt):
    return _inp(f"\n  {Cy}{BD}?  {prompt}{R}  {DM}>{R}  ")

# ╔══════════════════════════════════════════════════════╗
# ║  Modes                                               ║
# ╚══════════════════════════════════════════════════════╝

def mode_full():
    banner()
    title("Full Check  —  ตรวจสอบทั้งหมด", Gr, '🔍')
    info("Security · Nitro · Servers · Friends · DMs · Billing · Apps")
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        blank(); err("รูปแบบโทเคนไม่ถูกต้อง")
        print(f"\n  {DM}{mask(t)}{R}"); pause("กด Enter เพื่อกลับ"); return

    spin("ตรวจสอบ Discord API", 1.5, 'pulse', Cy)
    dec = decode_tok(t)
    res = check_token(t)

    title("ข้อมูลบัญชี", Cy)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌"); warn(res.get('why','')); pause(); return

    d      = res['data']
    is_bot = print_base_info(d, res['type'], dec)

    pf     = d.get('public_flags',0)
    badges = [v for k,v in FLAG_MAP.items() if pf&k]
    if badges:
        blank(); row('🎖','Badges','  '.join([f"{Ye}{BD}{b}{R}" for b in badges]),Mg,Wh)

    scan_security(t, d)
    if not is_bot: scan_nitro(t, d)
    scan_guilds(t, is_bot)
    if not is_bot:
        scan_friends(t); scan_dms(t); scan_connections(t)
        scan_billing(t); scan_settings(t); scan_apps(t)

    blank(); hr_thick(DM)
    print(f"  {DM}Token : {mask(t)}{R}")
    hr_thick(DM)

    if ask("บันทึก Report? (y/n)").lower() == 'y':
        f = save_report(t, dec, res)
        ok(f"บันทึกแล้วที่ : {f}")

    blank(); hr('─', Rd)
    warn("ควร Reset โทเคนทันทีหลังการตรวจสอบ")
    warn("อย่าแชร์โทเคนกับผู้อื่น")
    hr('─', Rd); pause()


def mode_advanced():
    banner()
    title("Advanced Scan  —  เลือก Scan เอง", Mg, '⚙')
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        err("รูปแบบโทเคนไม่ถูกต้อง"); pause("กด Enter เพื่อกลับ"); return

    spin("ตรวจสอบโทเคน", 1.2, 'dots', Mg)
    res = check_token(t)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌"); warn(res.get('why','')); pause(); return

    d      = res['data']
    is_bot = res['type'] == 'Bot Token'

    SCANS = [
        ('1','🛡','Security Audit',      lambda: scan_security(t,d)),
        ('2','💎','Nitro & Boosts',      lambda: scan_nitro(t,d)),
        ('3','🏰','Server Scan',         lambda: scan_guilds(t,is_bot)),
        ('4','👥','Friends',             lambda: scan_friends(t)),
        ('5','💬','DM Channels',         lambda: scan_dms(t)),
        ('6','🔗','Linked Accounts',     lambda: scan_connections(t)),
        ('7','💳','Billing / Payment',   lambda: scan_billing(t)),
        ('8','⚙','Account Settings',    lambda: scan_settings(t)),
        ('9','🔌','Authorized Apps',     lambda: scan_apps(t)),
        ('a','🎮','Activity Stats',      lambda: scan_activities(t)),
        ('0','🚪','กลับ',                None),
    ]

    while True:
        banner()
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        ok(f"{uname}  ·  {res['type']}")
        blank(); hr_thick(Mg)
        for num,icon,name,_ in SCANS:
            c = Rd if num=='0' else Wh
            hl= f"{DM}" if num=='0' else ''
            print(f"  {Mg}{BD} {num} {R}  {icon}  {hl}{c}{name}{R}")
        hr_thick(Mg)
        ch = ask("เลือก Scan")
        if ch == '0': break
        fn = next((f for n,_,_,f in SCANS if n==ch),None)
        if fn: fn(); pause()
        else: err("กรุณาเลือกตัวเลือกที่มี"); time.sleep(0.6)


def mode_gift():
    banner()
    title("Gift Code Checker", Ye, '🎁')
    info("ตรวจสอบ Nitro Gift Codes หลายอันพร้อมกัน")
    t = get_tok("ใส่โทเคน (ใช้ authenticate)")
    if not t: return
    blank()
    codes, i = [], 1
    while True:
        c = _inp(f"  {Ye}Gift Code {i}{R}  {DM}(done เพื่อเริ่ม){R}  {Cy}>{R}  ")
        if not c or c.lower()=='done': break
        codes.append(c); i += 1

    if not codes: err("ไม่มี Code"); pause(); return

    blank(); hr_thick(Ye)
    valid_codes = []
    for idx, code in enumerate(codes, 1):
        progress(idx, len(codes), c=Ye); blank()
        spin(f"ตรวจสอบ {code[:10]}...", 0.7, 'star', Ye)
        result = api_check_gift(code, t)
        if result and not result.get('message'):
            sku  = result.get('store_listing',{}).get('sku',{})
            name = sku.get('name','Nitro')
            uses = result.get('uses',0); max_u = result.get('max_uses',1)
            found(f"VALID  ·  {name}  ·  Uses: {uses}/{max_u}")
            print(f"  {Gr}{BD}https://discord.gift/{code}{R}")
            valid_codes.append(code)
        else:
            msg = result.get('message','Invalid') if result else 'Request failed'
            err(f"INVALID  ·  {code[:14]}...  ·  {msg}")

    blank(); hr_thick(Ye)
    print(f"  {BD}สรุป{R}   {tag_ok(f'Valid: {len(valid_codes)}')}  {tag_err(f'Invalid: {len(codes)-len(valid_codes)}')}")
    hr_thick(Ye)
    if valid_codes:
        if ask("แสดง Valid Codes? (y/n)").lower()=='y':
            for c in valid_codes: print(f"  {Gr}  https://discord.gift/{c}{R}")
    pause()


def mode_hypesquad():
    banner()
    title("HypeSquad Changer", Mg, '🏆')
    info("เปลี่ยน HypeSquad house ของบัญชี")
    t = get_tok()
    if not t: return
    blank()
    print(f"  {Rd}{BD} 1 {R}  🏅  Bravery      {DM}กล้าหาญ{R}")
    print(f"  {Ye}{BD} 2 {R}  ⚡  Brilliance   {DM}ฉลาด{R}")
    print(f"  {Gr}{BD} 3 {R}  ⚖  Balance      {DM}สมดุล{R}")
    blank()
    ch = ask("เลือก (1-3)")
    if ch not in ('1','2','3'): err("เลือกผิด"); pause(); return
    spin("กำลังเปลี่ยน HypeSquad", 1.0, 'pulse', Mg)
    if api_hypesquad_edit(t, int(ch)):
        ok(f"เปลี่ยนเป็น HypeSquad {HOUSE[int(ch)]} สำเร็จ!")
    else:
        err("ไม่สำเร็จ — Token อาจไม่ใช่ User Token")
    pause()


def mode_offline():
    banner()
    title("Offline Decode  —  ถอดรหัสโทเคน", Ye, '📴')
    info("ไม่ใช้อินเทอร์เน็ต  ถอดรหัสข้อมูลจากโทเคนเท่านั้น")
    t = get_tok()
    if not t: return
    spin("ถอดรหัส", 0.7, 'line', Ye)
    dec = decode_tok(t)
    blank(); hr_thick(Cy)
    if dec:
        ok("รูปแบบโทเคน : ถูกต้อง"); blank()
        rowA('ID','User ID',    dec['uid'], Bl, Wh)
        row('📅','สร้างบัญชีเมื่อ', dec['created'].strftime('%Y-%m-%d  %H:%M:%S'), Bl, Ye)
        row('⏱','อายุบัญชี',   f"{dec['years']} ปี  {dec['months']} เดือน  {dec['days']} วัน", Bl, Cy)
    else:
        err("รูปแบบโทเคน : ไม่ถูกต้อง")
    hr_thick(Cy)
    blank(); print(f"  {DM}Token : {mask(t)}{R}"); pause()


def mode_fmt():
    banner()
    title("Format Check  —  ตรวจรูปแบบ", Cy, '📋')
    t = get_tok("ใส่โทเคน")
    if not t: return
    blank(); hr_thick(Cy)
    if valid_fmt(t):
        ok("รูปแบบโทเคนถูกต้อง  ✅")
        p = clean(t).split('.')
        blank()
        rowA('>>','Part 1  User ID',   f"{len(p[0])} chars", Bl, Wh)
        rowA('>>','Part 2  Timestamp', f"{len(p[1])} chars", Bl, Wh)
        rowA('>>','Part 3  HMAC',      f"{len(p[2])} chars", Bl, Wh)
    else:
        err("รูปแบบโทเคนไม่ถูกต้อง  ❌")
        blank()
        print(f"  {Ye}รูปแบบที่ถูกต้อง:{R}")
        print(f"  {DM}  xxxxxxxxxxxx . xxxxxxx . xxxxxxxxxxxxxxxxxx{R}")
        print(f"  {DM}   24-28 chars .  6-7    .   27-40 chars{R}")
    hr_thick(Cy); pause()


def mode_bulk():
    banner()
    title("Bulk Check  —  เช็คหลายโทเคน", Mg, '📦')
    info("ใส่โทเคนทีละบรรทัด  พิมพ์ done หรือ Enter ว่างเพื่อเริ่ม")
    blank()
    tokens, i = [], 1
    while True:
        t = _inp(f"  {Cy}Token {i}{R}  {DM}>{R}  ")
        if not t or t.lower()=='done': break
        tokens.append(t); i += 1

    if not tokens: err("ไม่มีโทเคน"); pause(); return

    ok_list, fail_list = [], []
    blank(); hr_thick(Mg)

    for idx, t in enumerate(tokens, 1):
        blank()
        progress(idx, len(tokens), c=Mg); blank()
        print(f"  {DM}{mask(t)}{R}")

        if not valid_fmt(t):
            err("รูปแบบไม่ถูกต้อง"); fail_list.append(t); continue

        spin("เช็ค", 0.8, 'dots', Cy)
        res = check_token(t)
        if res['ok']:
            d    = res['data']
            disc = d.get('discriminator','0')
            un   = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                   else f"{d.get('username','?')}#{disc}"
            nt   = NITRO.get(d.get('premium_type',0),'?')
            tags = []
            if d.get('mfa_enabled'): tags.append(tag_ok('2FA'))
            if d.get('phone'):       tags.append(tag_ok('Phone'))
            if d.get('premium_type',0)>0: tags.append(tag_info('Nitro'))
            tag_str = '  '.join(tags)
            ok(f"{BD}{un}{R}  {DM}{res['type']}{R}  {tag_str}")
            ok_list.append({'token':t,'username':un,'type':res['type'],
                            'nitro':nt,'mfa':bool(d.get('mfa_enabled')),
                            'phone':bool(d.get('phone'))})
        else:
            err(f"INVALID  ·  {res.get('why','?')}")
            fail_list.append(t)

    # Summary
    blank(); hr_thick(Mg)
    nitro_c = sum(1 for x in ok_list if x['nitro']!='None')
    mfa_c   = sum(1 for x in ok_list if x['mfa'])
    print(f"\n  {BD}สรุปผล{R}")
    print(f"  {tag_ok(f' Valid: {len(ok_list)} ')}  {tag_err(f' Invalid: {len(fail_list)} ')}"
          f"  {tag_info(f' Nitro: {nitro_c} ')}  {tag_dim(f' 2FA: {mfa_c} ')}")
    blank(); hr_thick(Mg)

    if ok_list and ask("บันทึก Valid Tokens? (y/n)").lower()=='y':
        ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = os.path.expanduser(f"~/bulk_valid_{ts}.txt")
        with open(fname,'w',encoding='utf-8') as f:
            for x in ok_list:
                f.write(f"{x['token']}  |  {x['username']}  |  "
                        f"{x['type']}  |  {x['nitro']}  |  "
                        f"MFA:{x['mfa']}  |  Phone:{x['phone']}\n")
        ok(f"บันทึกแล้วที่ : {fname}")
    pause()


def show_help():
    banner()
    title("คู่มือการใช้งาน", Cy, '📖')
    items = [
        ('1','🔍','Full Check',     'ตรวจสอบทุกอย่างในครั้งเดียว'),
        ('2','⚙ ','Advanced Scan',  'เลือก scan เฉพาะส่วนที่ต้องการ'),
        ('3','🎁','Gift Checker',   'ตรวจสอบ Nitro Gift Codes'),
        ('4','🏆','HypeSquad',      'เปลี่ยน HypeSquad house'),
        ('5','📴','Offline Decode', 'ถอดรหัสโทเคน ไม่ใช้เน็ต'),
        ('6','📋','Format Check',   'ตรวจรูปแบบโทเคน'),
        ('7','📦','Bulk Check',     'เช็คหลายโทเคนพร้อมกัน + บันทึกผล'),
    ]
    for num,icon,name,desc in items:
        print(f"  {Cy}{BD} {num} {R}  {icon}  {BD}{name}{R}")
        print(f"           {DM}{desc}{R}"); blank()

    hr_thick(Gr)
    print(f"  {Gr}{BD}วิธีติดตั้งบน Termux{R}"); blank()
    for c in [
        "pkg update && pkg install python",
        "pip install requests",
        "curl -o ~/Checker_Token.py <GitHub Raw URL>",
        "python ~/Checker_Token.py",
    ]:
        print(f"  {DM}  $  {Cy}{c}{R}")
    hr_thick(Gr); pause()

# ╔══════════════════════════════════════════════════════╗
# ║  Main Menu                                           ║
# ╚══════════════════════════════════════════════════════╝
MENU = [
    ('1','🔍','Full Check',      'ตรวจสอบทุกอย่าง',        Gr,  True),
    ('2','⚙ ','Advanced Scan',   'เลือก scan เองได้',       Mg,  False),
    ('3','🎁','Gift Checker',    'ตรวจสอบ Gift Code',        Ye,  False),
    ('4','🏆','HypeSquad',       'เปลี่ยน House',            Cy,  False),
    ('5','📴','Offline Decode',  'ไม่ใช้เน็ต',               Ye,  False),
    ('6','📋','Format Check',    'ตรวจรูปแบบ',               Cy,  False),
    ('7','📦','Bulk Check',      'หลายโทเคน',                Mg,  False),
    ('8','📖','คู่มือ',           '',                         Wh,  False),
    ('0','🚪','ออก',             '',                         Rd,  False),
]
ACTS = {
    '1':mode_full,'2':mode_advanced,'3':mode_gift,'4':mode_hypesquad,
    '5':mode_offline,'6':mode_fmt,'7':mode_bulk,'8':show_help,
}

def main():
    while True:
        banner()

        # Menu box
        print(f"  {Cy}╔{'═'*W}╗{R}")
        print(f"  {Cy}║{R}  {BD}{'เลือกโหมดการทำงาน':^{W-2}}{R}  {Cy}║{R}")
        print(f"  {Cy}╠{'═'*W}╣{R}")
        blank()

        for num,icon,name,sub,col,hot in MENU:
            if hot:
                # Highlighted entry
                line = f"  {BGm}{Wh}{BD} {num} {R}  {icon}  {Mg}{BD}{name:<18}{R}  {DM}{sub}{R}"
            elif num == '0':
                line = f"  {Rd}{BD} {num} {R}  {icon}  {Rd}{name}{R}"
            else:
                line = f"  {col}{BD} {num} {R}  {icon}  {col}{name:<18}{R}  {DM}{sub}{R}"
            print(line)

        blank()
        print(f"  {Cy}╚{'═'*W}╝{R}")

        try:
            ch = _inp(f"\n  {Cy}{BD}  เลือก (0-8){R}  {DM}>{R}  ")
        except EOFError: break

        if ch == '0':
            clr()
            blank()
            print(_grad("  ขอบคุณที่ใช้งาน  See you next time!", _GRAD_GOLD))
            blank()
            break
        elif ch in ACTS:
            ACTS[ch]()
        else:
            err("กรุณาเลือก 0-8")
            time.sleep(0.7)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Ye}  Ctrl+C — ออกจากโปรแกรม{R}\n")
    except Exception as e:
        print(f"\n  {Rd}  Error: {e}{R}\n")
