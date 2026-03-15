#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════╗
║   Discord Token Checker - Termux v3.0   ║
║   รันได้บน Termux & Pydroid 3           ║
╚══════════════════════════════════════════╝
"""

import sys
import os
import re
import base64
import json
import time
from datetime import datetime

# ── ตรวจสอบ requests ──────────────────────────────────────────────────────────
try:
    import requests
except ImportError:
    print("\n[!] ไม่พบ requests กรุณารันคำสั่งนี้ก่อน:")
    print("    pip install requests\n")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
#  ANSI Colors & Styles
# ─────────────────────────────────────────────────────────────────────────────
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    UL      = '\033[4m'

    BLACK   = '\033[30m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'

    BG_BLACK  = '\033[40m'
    BG_BLUE   = '\033[44m'
    BG_CYAN   = '\033[46m'

    @staticmethod
    def gradient(text: str) -> str:
        """ไล่สีม่วง → ฟ้า ทีละอักขระ"""
        colors = ['\033[95m', '\033[94m', '\033[96m', '\033[94m', '\033[95m']
        out, i = '', 0
        for ch in text:
            if ch != ' ':
                out += colors[i % len(colors)] + ch
                i += 1
            else:
                out += ch
        return out + C.RESET

def b(txt): return f"{C.BOLD}{txt}{C.RESET}"
def dim(txt): return f"{C.DIM}{txt}{C.RESET}"

# ─────────────────────────────────────────────────────────────────────────────
#  Utility
# ─────────────────────────────────────────────────────────────────────────────
def clr():
    os.system('clear' if os.name != 'nt' else 'cls')

def pause(msg="กด Enter เพื่อดำเนินการต่อ..."):
    input(f"\n{C.YELLOW}  ↩  {msg}{C.RESET}")

def divider(char='─', width=52, color=C.CYAN):
    print(f"{color}{char * width}{C.RESET}")

def loading(msg="กำลังตรวจสอบ", secs=1.2):
    frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    end_time = time.time() + secs
    i = 0
    while time.time() < end_time:
        print(f"\r  {C.CYAN}{frames[i % len(frames)]}{C.RESET}  {C.BOLD}{msg}...{C.RESET}", end='', flush=True)
        time.sleep(0.08)
        i += 1
    print('\r' + ' ' * 40 + '\r', end='')

# ─────────────────────────────────────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────────────────────────────────────
BANNER = r"""
  ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗ 
  ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
  ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
  ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
  ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
  ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ 
"""

TOKEN_ART = r"""
  ████████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗
  ╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║
     ██║   ██║   ██║█████╔╝ █████╗  ██╔██╗ ██║
     ██║   ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║
     ██║   ╚██████╔╝██║  ██╗███████╗██║ ╚████║
     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝
"""

def print_banner():
    clr()
    for line in BANNER.split('\n'):
        print(C.gradient(line))
    for line in TOKEN_ART.split('\n'):
        print(C.gradient(line))
    print(f"  {C.DIM}{'─'*52}{C.RESET}")
    print(f"  {C.DIM}Checker v3.0  •  Termux Edition  •  No Bot Needed{C.RESET}")
    print(f"  {C.DIM}{'─'*52}{C.RESET}\n")

# ─────────────────────────────────────────────────────────────────────────────
#  Token Logic
# ─────────────────────────────────────────────────────────────────────────────
def clean(token: str) -> str:
    return token.replace('Bot ', '').strip()

def validate_format(token: str) -> bool:
    pattern = r'^[\w-]{24,28}\.[\w-]{6,7}\.[\w-]{27,40}$'
    return bool(re.match(pattern, clean(token)))

def decode_token(token: str) -> dict | None:
    try:
        parts = clean(token).split('.')
        if len(parts) != 3:
            return None

        # Part 1 → User ID
        uid_b64 = parts[0] + '=' * (-len(parts[0]) % 4)
        user_id = base64.b64decode(uid_b64).decode('utf-8', errors='ignore')

        # Part 2 → Timestamp
        ts_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
        ts_bytes = base64.b64decode(ts_b64)
        timestamp = int.from_bytes(ts_bytes, 'big') + 1420070400000
        created_at = datetime.fromtimestamp(timestamp / 1000)

        return {
            'user_id'   : user_id,
            'created_at': created_at,
            'hmac'      : parts[2],
            'parts'     : len(parts),
        }
    except Exception:
        return None

def check_online(token: str) -> dict:
    tok = clean(token)
    headers = {'Authorization': tok, 'Content-Type': 'application/json'}
    url = 'https://discord.com/api/v10/users/@me'

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            return {'valid': True, 'type': 'User Token', 'data': r.json()}

        if r.status_code == 401:
            headers['Authorization'] = f'Bot {tok}'
            r2 = requests.get(url, headers=headers, timeout=10)
            if r2.status_code == 200:
                return {'valid': True, 'type': 'Bot Token', 'data': r2.json()}
            return {'valid': False, 'reason': f'Unauthorized ({r2.status_code})'}

        return {'valid': False, 'reason': f'HTTP {r.status_code}'}

    except requests.Timeout:
        return {'valid': False, 'reason': 'หมดเวลาเชื่อมต่อ (ตรวจสอบเน็ต)'}
    except requests.ConnectionError:
        return {'valid': False, 'reason': 'ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้'}
    except Exception as e:
        return {'valid': False, 'reason': str(e)}

def mask_token(token: str) -> str:
    t = clean(token)
    return t[:10] + '·' * 20 + t[-6:] if len(t) > 20 else '·' * len(t)

# ─────────────────────────────────────────────────────────────────────────────
#  Display Result
# ─────────────────────────────────────────────────────────────────────────────
def tag(color, icon, label, value=''):
    print(f"  {color}{icon}  {C.BOLD}{label:<22}{C.RESET}{color}{value}{C.RESET}")

def print_result(decoded: dict | None, online: dict | None = None):
    print()
    divider('═', color=C.MAGENTA)
    print(f"  {C.BOLD}{C.MAGENTA}📊  ผลการตรวจสอบ{C.RESET}")
    divider('═', color=C.MAGENTA)

    # ── Decoded info ──────────────────────────────────────────────────────────
    print(f"\n  {C.CYAN}{b('[ ข้อมูลจากโทเคน ]')}{C.RESET}")
    divider('─', color=C.DIM)
    if decoded:
        tag(C.GREEN,  '✔', 'รูปแบบโทเคน',   'ถูกต้อง')
        tag(C.BLUE,   '🆔','User/Bot ID',   decoded['user_id'])
        if decoded.get('created_at'):
            tag(C.BLUE, '📅','สร้างเมื่อ', decoded['created_at'].strftime('%Y-%m-%d  %H:%M:%S'))
    else:
        tag(C.RED, '✘', 'รูปแบบโทเคน', 'ไม่ถูกต้อง')

    # ── Online result ─────────────────────────────────────────────────────────
    if online:
        print(f"\n  {C.YELLOW}{b('[ ผลการตรวจสอบออนไลน์ ]')}{C.RESET}")
        divider('─', color=C.DIM)

        if online['valid']:
            d = online['data']
            tag(C.GREEN,  '✔', 'สถานะ',         'โทเคนใช้งานได้  ✅')
            tag(C.CYAN,   '🏷', 'ประเภท',        online['type'])

            disc = d.get('discriminator', '0')
            uname = f"@{d.get('username','N/A')}" if disc in ('0', None) \
                    else f"{d.get('username','N/A')}#{disc}"
            tag(C.BLUE,   '👤','ชื่อผู้ใช้',    uname)
            tag(C.BLUE,   '🆔','Account ID',    d.get('id', 'N/A'))

            if d.get('bot'):
                tag(C.CYAN, '🤖','ประเภทบัญชี', 'Bot Account')
                stat = 'Public Bot' if d.get('public') else 'Private Bot'
                tag(C.CYAN, '🌐','สถานะบอท', stat)
            else:
                if d.get('email'):
                    ep = d['email'].split('@')
                    hidden = ep[0][:2] + '*****@' + ep[1] if len(ep) == 2 else '***'
                    tag(C.BLUE, '📧','อีเมล', hidden)

                v = d.get('verified', False)
                tag(C.BLUE, '✉', 'ยืนยันอีเมล',
                    f"{'✅ ยืนยันแล้ว' if v else '❌ ยังไม่ยืนยัน'}")

                if 'mfa_enabled' in d:
                    m = d['mfa_enabled']
                    tag(C.BLUE, '🔐','2FA',
                        f"{'✅ เปิดใช้งาน' if m else '❌ ปิดใช้งาน'}")

                if 'premium_type' in d:
                    nitro_map = {0:'ไม่มี Nitro 🆓', 1:'Nitro Classic 💎',
                                 2:'Nitro 💎', 3:'Nitro Basic 💎'}
                    tag(C.BLUE, '💠','Nitro',
                        nitro_map.get(d['premium_type'], 'ไม่ทราบ'))

                if d.get('public_flags', 0) > 0:
                    tag(C.BLUE, '🚩','Public Flags', str(d['public_flags']))
        else:
            tag(C.RED, '✘', 'สถานะ', 'โทเคนใช้งานไม่ได้  ❌')
            tag(C.RED, '📝','เหตุผล', online.get('reason', '?'))

    print()
    divider('═', color=C.MAGENTA)

# ─────────────────────────────────────────────────────────────────────────────
#  Input helper
# ─────────────────────────────────────────────────────────────────────────────
def get_token(prompt="ใส่โทเคน Discord") -> str | None:
    t = input(f"\n  {C.BOLD}{C.CYAN}🔑  {prompt}: {C.RESET}").strip()
    if not t:
        print(f"\n  {C.RED}❌  กรุณาใส่โทเคน{C.RESET}")
        pause("กด Enter เพื่อกลับ...")
        return None
    return t

# ─────────────────────────────────────────────────────────────────────────────
#  Modes
# ─────────────────────────────────────────────────────────────────────────────
def mode_full():
    """โหมดเช็คแบบเต็ม (ออนไลน์)"""
    print_banner()
    print(f"  {b(C.GREEN + '🌐  โหมดเช็คแบบเต็ม (ออนไลน์)')}{C.RESET}")
    print(f"  {C.DIM}ต้องการการเชื่อมต่ออินเทอร์เน็ต{C.RESET}")
    divider()

    token = get_token()
    if not token:
        return

    if not validate_format(token):
        print(f"\n  {C.RED}❌  รูปแบบโทเคนไม่ถูกต้อง{C.RESET}")
        print(f"  {C.YELLOW}🔑  {mask_token(token)}{C.RESET}")
        pause("กด Enter เพื่อกลับ...")
        return

    loading("กำลังตรวจสอบกับ Discord API", 1.5)

    decoded = decode_token(token)
    online  = check_online(token)

    print_result(decoded, online)

    print(f"  {C.YELLOW}🔑  โทเคน (ซ่อน): {mask_token(token)}{C.RESET}\n")
    print(f"  {C.RED}{b('⚠  คำเตือนด้านความปลอดภัย:')}{C.RESET}")
    print(f"  {C.RED}   • ควร Reset โทเคนนี้ทันทีหลังการตรวจสอบ{C.RESET}")
    print(f"  {C.RED}   • อย่าแชร์โทเคนกับผู้อื่น{C.RESET}")
    print(f"  {C.RED}   • ใช้เฉพาะโทเคนของตัวเองเท่านั้น{C.RESET}")
    pause()


def mode_offline():
    """โหมดออฟไลน์ (ถอดรหัสเท่านั้น)"""
    print_banner()
    print(f"  {b(C.YELLOW + '📴  โหมดออฟไลน์')}{C.RESET}")
    print(f"  {C.DIM}ถอดรหัสข้อมูลจากโทเคนโดยไม่ต้องใช้เน็ต{C.RESET}")
    divider()

    token = get_token()
    if not token:
        return

    loading("กำลังถอดรหัส", 0.8)

    decoded = decode_token(token)
    print_result(decoded, None)

    print(f"  {C.YELLOW}🔑  โทเคน (ซ่อน): {mask_token(token)}{C.RESET}")
    pause()


def mode_format():
    """ตรวจสอบรูปแบบโทเคน"""
    print_banner()
    print(f"  {b(C.CYAN + '📋  ตรวจสอบรูปแบบโทเคน')}{C.RESET}")
    divider()

    token = get_token("ใส่โทเคนที่ต้องการตรวจสอบ")
    if not token:
        return

    is_ok = validate_format(token)
    print()
    divider('─', color=C.DIM)

    if is_ok:
        parts = clean(token).split('.')
        print(f"  {C.GREEN}✅  รูปแบบโทเคนถูกต้อง{C.RESET}\n")
        print(f"  {C.CYAN}{b('โครงสร้างโทเคน:')}{C.RESET}")
        print(f"  {C.BLUE}  ส่วนที่ 1 (User ID)  : {len(parts[0])} ตัวอักษร{C.RESET}")
        print(f"  {C.BLUE}  ส่วนที่ 2 (Timestamp): {len(parts[1])} ตัวอักษร{C.RESET}")
        print(f"  {C.BLUE}  ส่วนที่ 3 (HMAC)     : {len(parts[2])} ตัวอักษร{C.RESET}")
    else:
        print(f"  {C.RED}❌  รูปแบบโทเคนไม่ถูกต้อง{C.RESET}\n")
        print(f"  {C.YELLOW}{b('รูปแบบที่ถูกต้อง:')}{C.RESET}")
        print(f"  {C.DIM}  • ต้องมี 3 ส่วน คั่นด้วย '.'{C.RESET}")
        print(f"  {C.DIM}  • ส่วน 1 : 24-28 ตัวอักษร{C.RESET}")
        print(f"  {C.DIM}  • ส่วน 2 : 6-7 ตัวอักษร{C.RESET}")
        print(f"  {C.DIM}  • ส่วน 3 : 27-40 ตัวอักษร{C.RESET}")

    divider('─', color=C.DIM)
    pause()


def mode_bulk():
    """เช็คหลายโทเคนพร้อมกัน"""
    print_banner()
    print(f"  {b(C.MAGENTA + '📦  โหมดเช็คหลายโทเคน (Bulk)')}{C.RESET}")
    print(f"  {C.DIM}ใส่โทเคนทีละบรรทัด  พิมพ์ DONE เมื่อเสร็จ{C.RESET}")
    divider()

    tokens = []
    idx = 1
    while True:
        t = input(f"  {C.CYAN}โทเคน {idx}: {C.RESET}").strip()
        if t.upper() == 'DONE' or t == '':
            break
        tokens.append(t)
        idx += 1

    if not tokens:
        print(f"\n  {C.RED}❌  ไม่มีโทเคนที่จะตรวจสอบ{C.RESET}")
        pause()
        return

    print(f"\n  {C.CYAN}⏳  กำลังตรวจสอบ {len(tokens)} โทเคน...{C.RESET}\n")
    valid_count = 0
    invalid_count = 0

    for i, tok in enumerate(tokens, 1):
        divider('·', color=C.DIM)
        print(f"  {C.BOLD}[{i}/{len(tokens)}]  {mask_token(tok)}{C.RESET}")

        if not validate_format(tok):
            print(f"  {C.RED}❌  รูปแบบไม่ถูกต้อง{C.RESET}")
            invalid_count += 1
            continue

        loading("ตรวจสอบ", 1.0)
        result = check_online(tok)

        if result['valid']:
            d = result['data']
            disc = d.get('discriminator', '0')
            uname = f"@{d.get('username','?')}" if disc in ('0', None) \
                    else f"{d.get('username','?')}#{disc}"
            print(f"  {C.GREEN}✅  VALID  •  {uname}  •  {result['type']}{C.RESET}")
            valid_count += 1
        else:
            print(f"  {C.RED}❌  INVALID  •  {result.get('reason','?')}{C.RESET}")
            invalid_count += 1

    print()
    divider('═', color=C.MAGENTA)
    print(f"  {b('สรุปผล')}  |  {C.GREEN}✅ Valid: {valid_count}{C.RESET}  |  {C.RED}❌ Invalid: {invalid_count}{C.RESET}")
    divider('═', color=C.MAGENTA)
    pause()


def show_help():
    print_banner()
    help_text = f"""  {C.CYAN}{b('📖  คู่มือการใช้งาน')}{C.RESET}
  {'─'*50}

  {b('1.  เช็คโทเคนแบบเต็ม (ออนไลน์)')}
      ตรวจสอบโทเคนกับ Discord API โดยตรง
      ดูข้อมูลบัญชีแบบละเอียด  ต้องใช้เน็ต

  {b('2.  เช็คโทเคนออฟไลน์')}
      ถอดรหัสข้อมูล User ID และเวลาที่สร้าง
      ไม่ต้องใช้เน็ต

  {b('3.  ตรวจสอบรูปแบบโทเคน')}
      เช็คว่าโทเคนมีรูปแบบถูกต้องไหม
      ไม่ส่งข้อมูลออกอินเทอร์เน็ต

  {b('4.  เช็คหลายโทเคน (Bulk)')}
      ใส่หลายโทเคนพร้อมกัน  พิมพ์ DONE เมื่อเสร็จ

  {'─'*50}
  {C.CYAN}{b('📱  โครงสร้างโทเคน Discord')}{C.RESET}
  {C.DIM}MTk4NjI...MQ.ZnCjm1XVW7...{C.RESET}
  {C.DIM}└─Part1─┘└Part2┘└──Part3──┘{C.RESET}

  {'─'*50}
  {C.YELLOW}{b('⚠   คำเตือน')}{C.RESET}
  {C.RED}  • ใช้เฉพาะโทเคนของตัวเองเท่านั้น{C.RESET}
  {C.RED}  • Reset โทเคนหลังการทดสอบเสมอ{C.RESET}
  {C.RED}  • อย่าแชร์โทเคนกับบุคคลอื่น{C.RESET}

  {'─'*50}
  {C.GREEN}{b('💡  วิธีติดตั้งบน Termux')}{C.RESET}
  {C.DIM}  pkg update && pkg install python{C.RESET}
  {C.DIM}  pip install requests{C.RESET}
  {C.DIM}  python Checker_Token.py{C.RESET}
  {'─'*50}
"""
    print(help_text)
    pause()

# ─────────────────────────────────────────────────────────────────────────────
#  Main Menu
# ─────────────────────────────────────────────────────────────────────────────
def menu_item(num, icon, label, color=C.WHITE):
    print(f"  {C.BOLD}{color} {num} {C.RESET} {icon}  {label}")

def main_menu():
    while True:
        print_banner()
        print(f"  {C.BOLD}เลือกโหมดการตรวจสอบ{C.RESET}\n")
        divider('─')
        menu_item('1', '🌐', 'เช็คโทเคนแบบเต็มรูปแบบ  (ออนไลน์)',  C.BG_BLUE  + C.WHITE)
        menu_item('2', '📴', 'เช็คโทเคนออฟไลน์',                    C.BG_CYAN  + C.BLACK)
        menu_item('3', '📋', 'ตรวจสอบรูปแบบโทเคน',                  C.CYAN)
        menu_item('4', '📦', 'เช็คหลายโทเคน  (Bulk)',                C.MAGENTA)
        menu_item('5', '📖', 'คู่มือการใช้งาน',                      C.YELLOW)
        menu_item('0', '🚪', 'ออกจากโปรแกรม',                        C.RED)
        divider('─')

        choice = input(f"\n  {C.BOLD}เลือก → {C.RESET}").strip()

        if   choice == '1': mode_full()
        elif choice == '2': mode_offline()
        elif choice == '3': mode_format()
        elif choice == '4': mode_bulk()
        elif choice == '5': show_help()
        elif choice == '0':
            clr()
            print(f"\n  {C.GREEN}👋  ขอบคุณที่ใช้งาน  See you!{C.RESET}\n")
            break
        else:
            print(f"\n  {C.RED}❌  กรุณาเลือก 0-5 เท่านั้น{C.RESET}")
            time.sleep(1)

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}👋  ออกจากโปรแกรม (Ctrl+C){C.RESET}\n")
    except Exception as e:
        print(f"\n  {C.RED}❌  เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}{C.RESET}\n")
