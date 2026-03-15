#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Token Checker v5.0 — Termux Edition
Advanced Token Scanner  |  Thai Fixed
"""

import sys, os, re, base64, time, json
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

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

Rd = '\033[91m'
Gr = '\033[92m'
Ye = '\033[93m'
Bl = '\033[94m'
Mg = '\033[95m'
Cy = '\033[96m'
Wh = '\033[97m'

BGm = '\033[45m'
BGr = '\033[41m'
BGg = '\033[42m'
BGb = '\033[44m'
BGc = '\033[46m'

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
#  UI
# ══════════════════════════════════════════════════════════════════
W = 52

def clr(): os.system('clear' if os.name != 'nt' else 'cls')

def pause(msg="กด Enter เพื่อดำเนินการต่อ"):
    input(f"\n  {Ye}>>  {msg} ...{R}")

def hr(ch='─', c=Cy):   print(f"  {c}{ch * W}{R}")
def blank():             print()

def title(txt, c=Mg):
    print(f"\n  {c}{BD}{'═' * W}{R}")
    print(f"  {c}{BD}  {txt}{R}")
    print(f"  {c}{BD}{'═' * W}{R}\n")

def section(txt, c=Bl):
    print(f"\n  {c}{BD}  ── {txt} ──{R}")
    hr('─', DM)

def spin(msg, secs=1.2):
    fr = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    end, i = time.time() + secs, 0
    while time.time() < end:
        print(f"\r  {Cy}{fr[i%10]}{R}  {BD}{msg}{R}  ", end='', flush=True)
        time.sleep(0.07); i += 1
    print('\r' + ' ' * 55 + '\r', end='')

def ok(msg):   print(f"  {Gr}{BD}[+]{R}  {Gr}{msg}{R}")
def err(msg):  print(f"  {Rd}{BD}[-]{R}  {Rd}{msg}{R}")
def info(msg): print(f"  {Cy}{BD}[i]{R}  {msg}")
def warn(msg): print(f"  {Ye}{BD}[!]{R}  {Ye}{msg}{R}")
def found(msg):print(f"  {Mg}{BD}[*]{R}  {Mg}{msg}{R}")

# 2-line row (Thai/Emoji safe — ไม่มี padding)
def row(icon, label, value, lc=Bl, vc=Wh):
    print(f"  {lc}{icon}  {BD}{label}{R}")
    print(f"      {vc}{value}{R}")

# inline row — ASCII label only
def rowA(icon, label, value, lc=Bl, vc=Wh):
    pad = max(16 - len(label), 1)
    print(f"  {lc}{icon}  {BD}{label}{R}{' ' * pad}{vc}{value}{R}")

def bullet(txt, c=DM):
    print(f"      {c}•  {txt}{R}")

# ══════════════════════════════════════════════════════════════════
#  Banner
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
    print(f"  {DM}{'─' * W}{R}")
    print(f"  {DM}v5.0  |  Termux Edition  |  Advanced Scanner{R}")
    print(f"  {DM}{'─' * W}{R}\n")

# ══════════════════════════════════════════════════════════════════
#  Token Core
# ══════════════════════════════════════════════════════════════════
def clean(t): return t.replace('Bot ', '').strip()

def valid_fmt(t):
    return bool(re.match(r'^[\w-]{24,28}\.[\w-]{6,7}\.[\w-]{27,40}$', clean(t)))

def decode_tok(t):
    try:
        p = clean(t).split('.')
        if len(p) != 3: return None
        uid = base64.b64decode(p[0] + '=' * (-len(p[0]) % 4)).decode('utf-8', 'ignore')
        tb  = base64.b64decode(p[1] + '=' * (-len(p[1]) % 4))
        ms  = int.from_bytes(tb, 'big') + 1420070400000
        ca  = datetime.fromtimestamp(ms / 1000)
        age = datetime.now() - ca
        return {
            'uid': uid, 'created': ca,
            'years': age.days // 365,
            'months': (age.days % 365) // 30,
            'days': age.days % 30,
        }
    except: return None

def mask(t):
    c = clean(t)
    return c[:10] + '·' * 18 + c[-6:] if len(c) > 20 else '·' * len(c)

# ══════════════════════════════════════════════════════════════════
#  API Layer
# ══════════════════════════════════════════════════════════════════
BASE = 'https://discord.com/api/v10'

def _req(ep, t, bot=False, method='GET', data=None, params=None):
    pfx = 'Bot ' if bot else ''
    h = {'Authorization': pfx + clean(t), 'Content-Type': 'application/json'}
    url = BASE + ep
    try:
        if method == 'GET':
            return requests.get(url, headers=h, timeout=10, params=params)
        elif method == 'PATCH':
            return requests.patch(url, headers=h, json=data, timeout=10)
        elif method == 'POST':
            return requests.post(url, headers=h, json=data, timeout=10)
        elif method == 'DELETE':
            return requests.delete(url, headers=h, timeout=10)
    except: return None

def _safe(ep, t, bot=False, params=None):
    try:
        r = _req(ep, t, bot, params=params)
        if r and r.status_code == 200:
            return r.json()
        return [] if r and r.status_code == 200 else []
    except: return []

def check_token(t):
    try:
        r = _req('/users/@me', t)
        if r and r.status_code == 200:
            return {'ok': True, 'type': 'User Token', 'data': r.json()}
        r2 = _req('/users/@me', t, bot=True)
        if r2 and r2.status_code == 200:
            return {'ok': True, 'type': 'Bot Token', 'data': r2.json()}
        code = r.status_code if r else '?'
        return {'ok': False, 'why': f'HTTP {code}'}
    except requests.Timeout:
        return {'ok': False, 'why': 'Timeout'}
    except requests.ConnectionError:
        return {'ok': False, 'why': 'ไม่มีอินเทอร์เน็ต'}
    except Exception as e:
        return {'ok': False, 'why': str(e)}

# ══════════════════════════════════════════════════════════════════
#  Advanced API Calls
# ══════════════════════════════════════════════════════════════════

def api_profile(t):
    """โปรไฟล์เต็ม รวม bio, banner, accent color"""
    r = _req('/users/@me', t)
    return r.json() if r and r.status_code == 200 else {}

def api_guilds(t, bot=False):
    return _safe('/users/@me/guilds', t, bot) or []

def api_guild_detail(guild_id, t, bot=False):
    """ข้อมูลเซิร์ฟเวอร์ + member count"""
    r = _req(f'/guilds/{guild_id}', t, bot, params={'with_counts': 'true'})
    return r.json() if r and r.status_code == 200 else {}

def api_guild_member(guild_id, t, bot=False):
    """ข้อมูล member ของบัญชีในเซิร์ฟเวอร์นั้น"""
    r = _req(f'/guilds/{guild_id}/members/@me', t, bot)
    return r.json() if r and r.status_code == 200 else {}

def api_connections(t):
    return _safe('/users/@me/connections', t) or []

def api_billing(t):
    return _safe('/users/@me/billing/payment-sources', t) or []

def api_boosts(t):
    return _safe('/users/@me/guilds/premium/subscription-slots', t) or []

def api_relationships(t):
    return _safe('/users/@me/relationships', t) or []

def api_dms(t):
    """DM channels ทั้งหมด"""
    return _safe('/users/@me/channels', t) or []

def api_dm_messages(channel_id, t, limit=5):
    """ข้อความล่าสุดใน DM"""
    return _safe(f'/channels/{channel_id}/messages', t,
                 params={'limit': limit}) or []

def api_gifts(t):
    """ตรวจสอบ Nitro gifts ที่รอ claim"""
    return _safe('/users/@me/entitlements/gifts', t) or []

def api_library(t):
    """เกมใน library"""
    return _safe('/users/@me/library', t) or []

def api_voice_regions(t):
    return _safe('/voice/regions', t) or []

def api_hypesquad_edit(t, house_id):
    """เปลี่ยน HypeSquad (1=Bravery, 2=Brilliance, 3=Balance)"""
    r = _req('/hypesquad/online', t, method='POST', data={'house_id': house_id})
    return r and r.status_code == 204

def api_settings(t):
    """User settings"""
    r = _req('/users/@me/settings', t)
    return r.json() if r and r.status_code == 200 else {}

def api_applications(t):
    """Apps ที่ authorize ไว้"""
    return _safe('/oauth2/tokens', t) or []

def api_experiments(t):
    """Experiments / A-B tests ที่ account เข้าร่วม"""
    r = _req('/experiments', t)
    return r.json() if r and r.status_code == 200 else {}

def api_invites(t):
    """Invites ที่สร้างไว้"""
    r = _req('/users/@me/invites', t)
    return r.json() if r and r.status_code == 200 else []

def api_sticker_packs(t):
    return _safe('/sticker-packs', t) or []

def api_activities(t):
    """Recent activities"""
    r = _req('/users/@me/activities/statistics/applications', t)
    return r.json() if r and r.status_code == 200 else []

def api_check_gift(code, t):
    """ตรวจสอบ gift code"""
    r = _req(f'/entitlements/gift-codes/{code}', t)
    return r.json() if r and r.status_code == 200 else None

# ══════════════════════════════════════════════════════════════════
#  Display helpers
# ══════════════════════════════════════════════════════════════════
FLAG_MAP = {
    1: 'Discord Staff', 2: 'Partner', 4: 'HypeSquad Events',
    8: 'Bug Hunter L1', 64: 'Bravery', 128: 'Brilliance',
    256: 'Balance', 512: 'Early Supporter',
    16384: 'Bug Hunter L2', 131072: 'Verified Bot Dev',
    4194304: 'Active Dev',
}
NITRO = {0: 'None', 1: 'Nitro Classic', 2: 'Nitro', 3: 'Nitro Basic'}
HOUSE = {1: 'Bravery', 2: 'Brilliance', 3: 'Balance'}

def avatar_url(uid, av_hash):
    if not av_hash: return 'ไม่มี Avatar'
    ext = 'gif' if av_hash.startswith('a_') else 'png'
    return f"https://cdn.discordapp.com/avatars/{uid}/{av_hash}.{ext}?size=512"

def banner_url(uid, bn_hash):
    if not bn_hash: return None
    ext = 'gif' if bn_hash.startswith('a_') else 'png'
    return f"https://cdn.discordapp.com/banners/{uid}/{bn_hash}.{ext}?size=512"

def fmt_ts(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z','+00:00'))
        return dt.strftime('%Y-%m-%d  %H:%M:%S')
    except: return str(ts_str)

def print_base_info(d, res_type, dec=None):
    """แสดงข้อมูลพื้นฐานของ token"""
    disc  = d.get('discriminator','0')
    uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
            else f"{d.get('username','?')}#{disc}"

    ok("สถานะ : โทเคนใช้งานได้  ✅")
    blank()
    rowA('--', 'Token Type', res_type, Cy, Wh)
    rowA('--', 'Username',   uname,    Bl, Wh)
    rowA('--', 'Account ID', d.get('id','?'), Bl, Wh)

    if dec:
        row('📅', 'สร้างบัญชีเมื่อ',
            dec['created'].strftime('%Y-%m-%d  %H:%M:%S'), Bl, Ye)
        age = f"{dec['years']} ปี  {dec['months']} เดือน  {dec['days']} วัน"
        row('⏱', 'อายุบัญชี', age, Bl, Cy)

    is_bot = res_type == 'Bot Token'
    if is_bot:
        row('🤖', 'ประเภทบัญชี', 'Bot Account', Cy, Cy)
        return is_bot

    # avatar + banner
    av = avatar_url(d.get('id',''), d.get('avatar'))
    row('--', 'Avatar URL', av, Bl, DM)
    bn = banner_url(d.get('id',''), d.get('banner'))
    if bn:
        row('--', 'Banner URL', bn, Mg, DM)

    # bio
    bio = d.get('bio','') or d.get('global_name','')
    if bio:
        row('--', 'Bio / Display Name', bio, Bl, Wh)

    # accent color
    if d.get('accent_color'):
        row('--', 'Accent Color', f"#{d['accent_color']:06X}", Bl, Wh)

    return is_bot

# ══════════════════════════════════════════════════════════════════
#  ── SCAN MODULES ──────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════

def scan_security(t, d):
    """Security Audit — 2FA, email, phone, billing"""
    section("Security Audit", Rd)

    v = d.get('verified', False)
    row('✉ ', 'ยืนยันอีเมล',
        '✅ ยืนยันแล้ว' if v else '❌ ยังไม่ยืนยัน', Bl, Gr if v else Rd)

    m = d.get('mfa_enabled', False)
    row('🔐', '2FA',
        '✅ เปิดใช้งาน' if m else '❌ ปิดใช้งาน — บัญชีเสี่ยง!', Bl, Gr if m else Rd)

    ph = d.get('phone')
    row('📱', 'เบอร์โทรศัพท์',
        ph if ph else '❌ ไม่ได้ผูกเบอร์', Bl, Ye if ph else Rd)

    if d.get('email'):
        ep = d['email'].split('@')
        em = ep[0][:2]+'*****@'+ep[1] if len(ep)==2 else '***'
        row('📧', 'อีเมล', em, Bl, Wh)

    # คะแนน security
    score = sum([bool(v), bool(m), bool(ph), bool(d.get('email'))])
    stars = '★' * score + '☆' * (4 - score)
    color = Gr if score >= 3 else (Ye if score == 2 else Rd)
    blank()
    row('🛡', 'Security Score', f"{stars}  ({score}/4)", Bl, color)

def scan_nitro(t, d):
    """Nitro + Boosts + Gifts"""
    section("Nitro & Boosts", Cy)

    nt = d.get('premium_type', 0)
    row('💎', 'Nitro', NITRO.get(nt,'?'), Bl, Cy if nt > 0 else DM)

    if d.get('premium_since'):
        row('--', 'Nitro since', fmt_ts(d['premium_since']), Bl, Wh)

    # boosts
    spin("ดึง Server Boosts", 0.8)
    boosts = api_boosts(t)
    if boosts and isinstance(boosts, list):
        used   = sum(1 for b in boosts if b.get('premium_guild_subscription'))
        unused = len(boosts) - used
        row('🚀', 'Server Boosts',
            f"รวม {len(boosts)}  |  ใช้ {used}  |  ว่าง {unused}", Bl, Mg)
        for b in boosts:
            sub = b.get('premium_guild_subscription')
            if sub:
                gid   = sub.get('guild_id','?')
                since = fmt_ts(sub.get('started_at',''))
                bullet(f"Boost → Guild {gid}  (since {since})", Mg)
    else:
        info("ไม่มี Server Boosts")

    # gifts
    spin("ตรวจสอบ Nitro Gifts", 0.8)
    gifts = api_gifts(t)
    if gifts and isinstance(gifts, list):
        found(f"พบ Nitro Gift {len(gifts)} รายการ!")
        for g in gifts:
            bullet(f"ID: {g.get('id','?')}  SKU: {g.get('sku_id','?')}", Ye)
    else:
        info("ไม่มี Nitro Gift ที่รอ Claim")

def scan_guilds(t, is_bot):
    """เซิร์ฟเวอร์ — แสดง roles, permissions, admin"""
    section("Server Scan", Ye)

    spin("ดึงรายการเซิร์ฟเวอร์", 1.0)
    guilds = api_guilds(t, is_bot)
    if not guilds or not isinstance(guilds, list):
        info("ดึงข้อมูลเซิร์ฟเวอร์ไม่ได้"); return

    own_count   = sum(1 for g in guilds if g.get('owner'))
    admin_count = sum(1 for g in guilds
                      if int(g.get('permissions','0')) & 0x8)  # Administrator bit

    row('🏰', 'เซิร์ฟเวอร์ทั้งหมด',  f"{len(guilds)} แห่ง", Ye, Ye)
    row('👑', 'เป็นเจ้าของ',          f"{own_count} แห่ง",   Ye, Cy)
    row('🔑', 'มีสิทธิ์ Admin',        f"{admin_count} แห่ง", Ye, Rd if admin_count else Wh)
    blank()

    for g in guilds[:8]:
        perms     = int(g.get('permissions','0'))
        is_owner  = g.get('owner', False)
        is_admin  = bool(perms & 0x8)
        can_ban   = bool(perms & 0x4)
        can_kick  = bool(perms & 0x2)
        can_manage= bool(perms & 0x20)

        tags = []
        if is_owner:  tags.append(f"{Cy}[Owner]{R}")
        if is_admin:  tags.append(f"{Rd}[Admin]{R}")
        if can_ban:   tags.append(f"{Rd}[Ban]{R}")
        if can_kick:  tags.append(f"{Ye}[Kick]{R}")
        if can_manage:tags.append(f"{Mg}[Manage]{R}")

        tag_str = '  '.join(tags) if tags else f"{DM}[Member]{R}"
        print(f"  {DM}{'─'*W}{R}")
        print(f"  {BD}{Wh}{g.get('name','?')}{R}  {tag_str}")
        print(f"    {DM}ID: {g.get('id','?')}{R}")

    if len(guilds) > 8:
        blank()
        info(f"... และอีก {len(guilds)-8} เซิร์ฟเวอร์  (แสดง 8 อันดับแรก)")

def scan_friends(t):
    """เพื่อน + blocked + pending"""
    section("Friends & Relationships", Gr)

    spin("ดึงรายชื่อเพื่อน", 0.8)
    rels = api_relationships(t)
    if not rels or not isinstance(rels, list):
        info("ดึงข้อมูลเพื่อนไม่ได้"); return

    friends  = [x for x in rels if x.get('type') == 1]
    blocked  = [x for x in rels if x.get('type') == 2]
    incoming = [x for x in rels if x.get('type') == 3]
    outgoing = [x for x in rels if x.get('type') == 4]

    row('👥', 'เพื่อน',          f"{len(friends)} คน",  Gr, Gr)
    row('🚫', 'บล็อค',           f"{len(blocked)} คน",  Rd, Rd)
    row('📩', 'คำขอขาเข้า',      f"{len(incoming)} คน", Ye, Ye)
    row('📤', 'คำขอขาออก',       f"{len(outgoing)} คน", Bl, Bl)
    blank()

    if friends:
        info(f"เพื่อน {min(5,len(friends))} คนล่าสุด:")
        for f in friends[:5]:
            u = f.get('user', {})
            disc = u.get('discriminator','0')
            un = f"@{u.get('username','?')}" if disc in ('0',None,'') \
                 else f"{u.get('username','?')}#{disc}"
            bullet(f"{un}  (ID: {u.get('id','?')})", Wh)

    if incoming:
        blank()
        found(f"มีคำขอเพื่อน {len(incoming)} คนรอการตอบรับ!")
        for f in incoming[:3]:
            u = f.get('user', {})
            disc = u.get('discriminator','0')
            un = f"@{u.get('username','?')}" if disc in ('0',None,'') \
                 else f"{u.get('username','?')}#{disc}"
            bullet(un, Ye)

def scan_dms(t):
    """DM channels ล่าสุด"""
    section("Direct Messages", Bl)

    spin("ดึง DM channels", 0.8)
    dms = api_dms(t)
    if not dms or not isinstance(dms, list):
        info("ดึงข้อมูล DM ไม่ได้"); return

    row('💬', 'DM Channels', f"{len(dms)} ช่อง", Bl, Bl)
    blank()

    for ch in dms[:6]:
        ch_type = ch.get('type', 0)
        if ch_type == 1:  # DM
            rec = ch.get('recipients', [{}])[0] if ch.get('recipients') else {}
            disc = rec.get('discriminator','0')
            un = f"@{rec.get('username','?')}" if disc in ('0',None,'') \
                 else f"{rec.get('username','?')}#{disc}"
            last = ch.get('last_message_id','')
            print(f"  {Bl}DM{R}  {BD}{un}{R}  {DM}ch:{ch.get('id','?')}{R}")
        elif ch_type == 3:  # Group DM
            name = ch.get('name') or f"Group ({len(ch.get('recipients',[]))+1} คน)"
            print(f"  {Mg}GDM{R}  {BD}{name}{R}  {DM}ch:{ch.get('id','?')}{R}")

    if len(dms) > 6:
        info(f"... และอีก {len(dms)-6} ช่อง")

def scan_connections(t):
    """Linked accounts"""
    section("Linked Accounts", Mg)

    spin("ดึง Linked Accounts", 0.8)
    conns = api_connections(t)
    if not conns or not isinstance(conns, list):
        info("ไม่มี Linked Accounts"); return

    row('🔗', 'Linked Accounts', f"{len(conns)} บัญชี", Mg, Mg)
    blank()
    for c in conns:
        vf   = '✅' if c.get('verified') else '❌'
        vis  = '🌐 Public' if c.get('visibility') == 1 else '🔒 Private'
        name = c.get('name','?')
        ctype= c.get('type','?').upper()
        print(f"  {Mg}[{ctype}]{R}  {BD}{name}{R}  {vf}  {DM}{vis}{R}")
        if c.get('show_activity'):
            bullet("แสดง Activity บน Profile", Cy)

def scan_billing(t):
    """Payment methods"""
    section("Payment & Billing", Ye)

    spin("ดึง Payment Methods", 0.8)
    bills = api_billing(t)
    if not bills or not isinstance(bills, list):
        info("ไม่มี Payment Methods หรือดึงไม่ได้"); return

    found(f"พบ Payment Methods {len(bills)} รายการ!")
    blank()
    btype_map = {1:'Credit/Debit Card', 2:'PayPal', 3:'Google Pay', 4:'Apple Pay'}
    for b in bills:
        btype = btype_map.get(b.get('type',0),'Unknown')
        l4    = b.get('last_4','')
        exp   = f"{b.get('expires_month','?')}/{b.get('expires_year','?')}"
        vld   = '✅ Valid' if b.get('invalid') is False else '⚠ Invalid'
        dflt  = '  [Default]' if b.get('default') else ''
        print(f"  {Ye}{btype}{R}  {'****'+l4 if l4 else ''}")
        print(f"    {DM}Expire: {exp}  |  {vld}{dflt}{R}")

def scan_settings(t):
    """User settings — theme, locale, activity"""
    section("Account Settings", Cy)

    spin("ดึง Settings", 0.8)
    s = api_settings(t)
    if not s: info("ดึง Settings ไม่ได้"); return

    locale  = s.get('locale','?')
    theme   = s.get('theme','?')
    status  = s.get('status','?')
    afk     = s.get('afk_timeout','?')
    dev_mode= s.get('developer_mode', False)
    explicit= s.get('explicit_content_filter', 0)
    gif_auto= s.get('gif_auto_play', False)
    animate = s.get('animate_emojis', False)

    rowA('--', 'Locale',      locale,              Bl, Wh)
    rowA('--', 'Theme',       theme,               Bl, Wh)
    rowA('--', 'Status',      status,              Bl, Ye)
    rowA('--', 'AFK Timeout', f"{afk} วินาที",     Bl, Wh)
    rowA('--', 'Dev Mode',    '✅' if dev_mode else '❌', Bl, Gr if dev_mode else Rd)
    rowA('--', 'GIF AutoPlay','✅' if gif_auto else '❌', Bl, Wh)
    rowA('--', 'Animate Emoji','✅' if animate else '❌', Bl, Wh)

    explicit_map = {0:'ปิด', 1:'เพื่อนไม่มี role', 2:'เปิดทุก DM'}
    rowA('--', 'Explicit Filter', explicit_map.get(explicit,'?'), Bl, Wh)

def scan_apps(t):
    """OAuth2 apps ที่ authorize ไว้"""
    section("Authorized Apps", Mg)

    spin("ดึง Authorized Apps", 0.8)
    apps = api_applications(t)
    if not apps or not isinstance(apps, list):
        info("ไม่มี Authorized Apps"); return

    row('🔌', 'Authorized Apps', f"{len(apps)} แอป", Mg, Mg)
    blank()
    for a in apps[:8]:
        app  = a.get('application', {})
        name = app.get('name','?')
        scopes = ', '.join(a.get('scopes',[]))
        print(f"  {Mg}{BD}{name}{R}")
        print(f"    {DM}Scopes: {scopes}{R}")

    if len(apps) > 8:
        info(f"... และอีก {len(apps)-8} แอป")

def scan_activities(t):
    """Activity statistics"""
    section("Game / Activity Stats", Bl)

    spin("ดึง Activity Stats", 0.8)
    acts = api_activities(t)
    if not acts or not isinstance(acts, list):
        info("ไม่มีข้อมูล Activities"); return

    row('🎮', 'Games / Apps', f"{len(acts)} รายการ", Bl, Bl)
    blank()
    # sort by total_duration_or_sessions
    for a in acts[:6]:
        app_id  = a.get('application_id','?')
        total   = a.get('total_duration', 0)
        hours   = total // 3600
        minutes = (total % 3600) // 60
        print(f"  {Bl}AppID: {app_id}{R}  {DM}{hours}h {minutes}m{R}")

# ══════════════════════════════════════════════════════════════════
#  Save Report
# ══════════════════════════════════════════════════════════════════
def save_report(token, dec, res, extra=None):
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = os.path.expanduser(f"~/token_report_{ts}.txt")
    lines = [
        '=' * 52,
        '  Discord Token Report  v5.0',
        f"  Date     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        '=' * 52,
        f"  Token    : {mask(token)}",
    ]
    if dec:
        lines += [
            f"  UserID   : {dec['uid']}",
            f"  Created  : {dec['created'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Age      : {dec['years']}y {dec['months']}m {dec['days']}d",
        ]
    if res and res.get('ok'):
        d     = res['data']
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        lines += [
            f"  Type     : {res['type']}",
            f"  Username : {uname}",
            f"  ID       : {d.get('id','?')}",
            f"  Email    : {d.get('email','N/A')}",
            f"  Phone    : {d.get('phone','N/A')}",
            f"  Verified : {d.get('verified','?')}",
            f"  MFA      : {d.get('mfa_enabled','?')}",
            f"  Nitro    : {NITRO.get(d.get('premium_type',0),'?')}",
            f"  Avatar   : {avatar_url(d.get('id',''), d.get('avatar'))}",
        ]
        pf = d.get('public_flags', 0)
        badges = [v for k, v in FLAG_MAP.items() if pf & k]
        if badges:
            lines.append(f"  Badges   : {', '.join(badges)}")
    if extra:
        lines += ['', '── Additional Info ──'] + extra
    lines.append('=' * 52)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return fname

# ══════════════════════════════════════════════════════════════════
#  Input
# ══════════════════════════════════════════════════════════════════
def get_tok(prompt="ใส่โทเคน Discord"):
    try:
        t = input(f"\n  {BD}{Cy}>>  {prompt}: {R}").strip()
    except EOFError:
        return None
    if not t:
        err("กรุณาใส่โทเคน"); pause("กด Enter เพื่อกลับ"); return None
    return t

def ask(prompt):
    try: return input(f"  {BD}{Cy}>>  {prompt}: {R}").strip()
    except EOFError: return ''

# ══════════════════════════════════════════════════════════════════
#  ── MODES ────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════

def mode_full():
    """Full Check — ทุกอย่างในครั้งเดียว"""
    banner()
    title("Full Check  —  ตรวจสอบทั้งหมด", Gr)
    info("Security + Nitro + Servers + Friends + DMs + Billing + Apps")
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        err("รูปแบบโทเคนไม่ถูกต้อง"); pause("กด Enter เพื่อกลับ"); return

    spin("ตรวจสอบ Discord API", 1.5)
    dec = decode_tok(t)
    res = check_token(t)

    title("ข้อมูลบัญชี", Cy)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌"); warn(res.get('why','')); pause(); return

    d      = res['data']
    is_bot = print_base_info(d, res['type'], dec)

    # badges
    pf = d.get('public_flags', 0)
    badges = [v for k, v in FLAG_MAP.items() if pf & k]
    if badges:
        blank(); row('🎖', 'Badges', '  |  '.join(badges), Mg, Ye)

    # run all scans
    scan_security(t, d)
    if not is_bot:
        scan_nitro(t, d)
    scan_guilds(t, is_bot)
    if not is_bot:
        scan_friends(t)
        scan_dms(t)
        scan_connections(t)
        scan_billing(t)
        scan_settings(t)
        scan_apps(t)

    blank(); print(f"  {Ye}>> Token : {mask(t)}{R}")

    sv = ask("บันทึก Report? (y/n)")
    if sv.lower() == 'y':
        f = save_report(t, dec, res)
        ok(f"บันทึกแล้วที่ : {f}")

    blank(); hr('─', Rd)
    warn("ควร Reset โทเคนทันทีหลังการตรวจสอบ")
    warn("อย่าแชร์โทเคนกับผู้อื่น")
    hr('─', Rd)
    pause()


def mode_advanced():
    """Advanced Scan — เลือก scan เฉพาะส่วน"""
    banner()
    title("Advanced Scan  —  เลือก Scan ที่ต้องการ", Mg)
    t = get_tok()
    if not t: return
    if not valid_fmt(t):
        err("รูปแบบโทเคนไม่ถูกต้อง"); pause("กด Enter เพื่อกลับ"); return

    spin("ตรวจสอบโทเคน", 1.2)
    res = check_token(t)
    if not res['ok']:
        err("โทเคนใช้งานไม่ได้  ❌"); warn(res.get('why','')); pause(); return

    d      = res['data']
    is_bot = res['type'] == 'Bot Token'

    SCAN_MENU = [
        ('1', 'Security Audit',     lambda: scan_security(t, d)),
        ('2', 'Nitro & Boosts',     lambda: scan_nitro(t, d)),
        ('3', 'Server Scan',        lambda: scan_guilds(t, is_bot)),
        ('4', 'Friends & Relations',lambda: scan_friends(t)),
        ('5', 'DM Channels',        lambda: scan_dms(t)),
        ('6', 'Linked Accounts',    lambda: scan_connections(t)),
        ('7', 'Billing / Payment',  lambda: scan_billing(t)),
        ('8', 'Account Settings',   lambda: scan_settings(t)),
        ('9', 'Authorized Apps',    lambda: scan_apps(t)),
        ('a', 'Activity Stats',     lambda: scan_activities(t)),
        ('0', 'กลับ',               None),
    ]

    while True:
        banner()
        disc  = d.get('discriminator','0')
        uname = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                else f"{d.get('username','?')}#{disc}"
        ok(f"Token Valid  |  {uname}  |  {res['type']}")
        blank(); hr()
        for num, name, _ in SCAN_MENU:
            c = Rd if num == '0' else Cy
            print(f"  {c}{BD} {num} {R}  {name}")
        hr()
        ch = ask("เลือก Scan")
        if ch == '0': break
        found = next((fn for n,_,fn in SCAN_MENU if n == ch), None)
        if found:
            found()
            pause()
        else:
            err("กรุณาเลือกตัวเลือกที่มี"); time.sleep(0.6)


def mode_gift():
    """ตรวจสอบ Nitro Gift Code"""
    banner()
    title("Gift Code Checker", Ye)
    info("ตรวจสอบว่า Gift Code ใช้งานได้หรือไม่")
    t = get_tok("ใส่โทเคน (ใช้ authenticate)")
    if not t: return
    blank()
    codes = []
    i = 1
    while True:
        try:
            c = input(f"  {Cy}Gift Code {i} (หรือ done): {R}").strip()
        except EOFError: break
        if not c or c.lower() == 'done': break
        codes.append(c); i += 1

    if not codes: err("ไม่มี Code"); pause(); return
    blank(); hr()
    valid_codes = []
    for code in codes:
        spin(f"ตรวจสอบ {code[:8]}...", 0.7)
        result = api_check_gift(code, t)
        if result and not result.get('message'):
            sku = result.get('store_listing',{}).get('sku',{})
            name = sku.get('name','Nitro')
            uses = result.get('uses',0)
            max_u= result.get('max_uses',1)
            found(f"VALID  |  {name}  |  Uses: {uses}/{max_u}")
            print(f"    {Gr}https://discord.gift/{code}{R}")
            valid_codes.append(code)
        else:
            msg = result.get('message','Invalid') if result else 'Request failed'
            err(f"INVALID  |  {code[:12]}...  |  {msg}")
    blank()
    print(f"  {BD}สรุป{R}   {Gr}Valid: {len(valid_codes)}{R}  |  {Rd}Invalid: {len(codes)-len(valid_codes)}{R}")
    if valid_codes:
        blank()
        sv = ask("Copy Valid Codes? (y/n)")
        if sv.lower() == 'y':
            for c in valid_codes:
                print(f"  {Gr}https://discord.gift/{c}{R}")
    pause()


def mode_hypesquad():
    """เปลี่ยน HypeSquad house"""
    banner()
    title("HypeSquad Changer", Mg)
    info("เปลี่ยน HypeSquad house ของบัญชี")
    t = get_tok()
    if not t: return
    blank()
    print(f"  {Cy}{BD}1{R}  Bravery   (กล้าหาญ)")
    print(f"  {Bl}{BD}2{R}  Brilliance (ฉลาด)")
    print(f"  {Gr}{BD}3{R}  Balance   (สมดุล)")
    blank()
    ch = ask("เลือก (1-3)")
    if ch not in ('1','2','3'):
        err("เลือกผิด"); pause(); return
    spin("กำลังเปลี่ยน HypeSquad", 1.0)
    success = api_hypesquad_edit(t, int(ch))
    if success:
        ok(f"เปลี่ยนเป็น HypeSquad {HOUSE[int(ch)]} สำเร็จ!")
    else:
        err("ไม่สำเร็จ — Token อาจไม่ใช่ User Token")
    pause()


def mode_offline():
    banner()
    title("Offline Decode  —  ถอดรหัสโทเคน", Ye)
    info("ไม่ใช้อินเทอร์เน็ต  ถอดรหัสข้อมูลจากโทเคนเท่านั้น")
    t = get_tok()
    if not t: return
    spin("ถอดรหัส", 0.7)
    dec = decode_tok(t)
    title("ข้อมูลจากโทเคน  (Offline)", Cy)
    if dec:
        ok("รูปแบบโทเคน : ถูกต้อง"); blank()
        rowA('ID','User ID', dec['uid'], Bl, Wh)
        row('📅','สร้างบัญชีเมื่อ',
            dec['created'].strftime('%Y-%m-%d  %H:%M:%S'), Bl, Ye)
        age = f"{dec['years']} ปี  {dec['months']} เดือน  {dec['days']} วัน"
        row('⏱','อายุบัญชี', age, Bl, Cy)
    else:
        err("รูปแบบโทเคน : ไม่ถูกต้อง")
    blank(); print(f"  {Ye}>> Token : {mask(t)}{R}")
    pause()


def mode_fmt():
    banner()
    title("Format Check  —  ตรวจรูปแบบโทเคน", Cy)
    t = get_tok("ใส่โทเคน")
    if not t: return
    is_ok = valid_fmt(t)
    blank(); hr()
    if is_ok:
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
    hr(); pause()


def mode_bulk():
    banner()
    title("Bulk Check  —  เช็คหลายโทเคน", Mg)
    info("ใส่โทเคนทีละบรรทัด  พิมพ์ done หรือ Enter ว่างเพื่อเริ่ม")
    blank()
    tokens, i = [], 1
    while True:
        try:
            t = input(f"  {Cy}Token {i}: {R}").strip()
        except EOFError: break
        if not t or t.lower() == 'done': break
        tokens.append(t); i += 1

    if not tokens: err("ไม่มีโทเคน"); pause(); return

    ok_list, fail_list = [], []
    for idx, t in enumerate(tokens, 1):
        hr('·', DM)
        print(f"  {BD}[{idx}/{len(tokens)}]{R}  {DM}{mask(t)}{R}")
        if not valid_fmt(t):
            err("รูปแบบไม่ถูกต้อง"); fail_list.append(t); continue
        spin("เช็ค", 0.8)
        res = check_token(t)
        if res['ok']:
            d    = res['data']
            disc = d.get('discriminator','0')
            un   = f"@{d.get('username','?')}" if disc in ('0',None,'') \
                   else f"{d.get('username','?')}#{disc}"
            nt   = NITRO.get(d.get('premium_type',0),'?')
            mfa  = '🔐' if d.get('mfa_enabled') else ''
            ph   = '📱' if d.get('phone') else ''
            ok(f"VALID  |  {un}  |  {nt}  {mfa}{ph}")
            ok_list.append({'token':t,'username':un,'type':res['type'],
                           'nitro':nt,'mfa':bool(d.get('mfa_enabled')),
                           'phone':bool(d.get('phone'))})
        else:
            err(f"INVALID  |  {res.get('why','?')}"); fail_list.append(t)

    blank(); hr('═', Mg)
    print(f"\n  {BD}สรุปผล{R}   {Gr}Valid: {len(ok_list)}{R}   {Rd}Invalid: {len(fail_list)}{R}")
    if ok_list:
        nitro_count = sum(1 for x in ok_list if x['nitro'] != 'None')
        mfa_count   = sum(1 for x in ok_list if x['mfa'])
        print(f"  {Cy}Nitro: {nitro_count}{R}   {Ye}MFA On: {mfa_count}{R}")
    hr('═', Mg)

    if ok_list:
        sv = ask("บันทึก Valid Tokens? (y/n)")
        if sv.lower() == 'y':
            ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
            fname = os.path.expanduser(f"~/bulk_valid_{ts}.txt")
            with open(fname,'w',encoding='utf-8') as f:
                for x in ok_list:
                    f.write(
                        f"{x['token']}  |  {x['username']}  |  "
                        f"{x['type']}  |  {x['nitro']}  |  "
                        f"MFA:{x['mfa']}  |  Phone:{x['phone']}\n"
                    )
            ok(f"บันทึกแล้วที่ : {fname}")
    pause()


def show_help():
    banner()
    title("คู่มือการใช้งาน", Cy)
    items = [
        ('1','Full Check',     'ตรวจสอบทั้งหมดครั้งเดียว (โหมดหลัก)'),
        ('2','Advanced Scan',  'เลือก scan เฉพาะส่วนที่ต้องการ'),
        ('3','Gift Checker',   'ตรวจสอบ Nitro Gift Codes'),
        ('4','HypeSquad',      'เปลี่ยน HypeSquad house'),
        ('5','Offline Decode', 'ถอดรหัสโทเคน ไม่ใช้เน็ต'),
        ('6','Format Check',   'ตรวจรูปแบบโทเคน'),
        ('7','Bulk Check',     'เช็คหลายโทเคนพร้อมกัน'),
    ]
    for num, name, desc in items:
        print(f"  {Cy}{BD}[{num}]{R}  {BD}{name}{R}")
        print(f"       {DM}{desc}{R}"); blank()
    hr()
    print(f"  {Gr}{BD}วิธีติดตั้งบน Termux{R}")
    for c in [
        "pkg update && pkg install python",
        "pip install requests",
        "curl -o ~/Checker_Token.py <GitHub Raw URL>",
        "python ~/Checker_Token.py",
    ]:
        print(f"  {DM}  $ {c}{R}")
    hr(); pause()

# ══════════════════════════════════════════════════════════════════
#  Main Menu
# ══════════════════════════════════════════════════════════════════
MENU = [
    ('1','🔍','Full Check',     'ตรวจสอบทุกอย่าง',         Gr,  BGg),
    ('2','⚙ ','Advanced Scan',  'เลือก scan เองได้',        Mg,  BGm),
    ('3','🎁','Gift Checker',   'ตรวจสอบ Gift Code',         Ye,  ''),
    ('4','🏆','HypeSquad',      'เปลี่ยน House',             Cy,  ''),
    ('5','📴','Offline Decode', 'ไม่ใช้เน็ต',                Ye,  ''),
    ('6','📋','Format Check',   'ตรวจรูปแบบ',                Cy,  ''),
    ('7','📦','Bulk Check',     'หลายโทเคน',                 Mg,  ''),
    ('8','📖','คู่มือ',          '',                          Wh,  ''),
    ('0','🚪','ออก',            '',                          Rd,  ''),
]
ACTS = {
    '1':mode_full,'2':mode_advanced,'3':mode_gift,'4':mode_hypesquad,
    '5':mode_offline,'6':mode_fmt,'7':mode_bulk,'8':show_help,
}

def main():
    while True:
        banner()
        print(f"  {BD}เลือกโหมด{R}\n")
        hr()
        blank()
        for num, icon, name, sub, col, bg in MENU:
            sub_txt = f"  {DM}— {sub}{R}" if sub else ''
            print(f"  {bg}{col}{BD} {num} {R}  {icon}  {col}{BD}{name}{R}{sub_txt}")
        blank(); hr()
        try:
            ch = input(f"\n  {BD}>>  เลือก (0-8): {R}").strip()
        except EOFError: break
        if ch == '0':
            clr(); print(f"\n  {Gr}>>  ขอบคุณที่ใช้งาน  See you!{R}\n"); break
        elif ch in ACTS:
            ACTS[ch]()
        else:
            err("กรุณาเลือก 0-8"); time.sleep(0.7)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Ye}>>  Ctrl+C — ออกจากโปรแกรม{R}\n")
    except Exception as e:
        print(f"\n  {Rd}>>  Error: {e}{R}\n")
