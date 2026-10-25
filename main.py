# /// script
# dependencies = [
#   "arabic-reshaper==3.0.0",
#   "python-bidi==0.4.2",
#   "six",
# ]
# ///
"""
Supermarket Simulator 2D — v9.0 [UNIVERSAL]
Auto-detect · Progressive difficulty · Locked levels
Arabic + English · Fullscreen · Full Mouse Support · Modern UI
"""
import platform as _plat
import os as _os
import sys as _sys
import asyncio

IS_WEB = _sys.platform == "emscripten"                      # pygbag (iPhone / browser)
IS_ANDROID = ("ANDROID_ARGUMENT" in _os.environ) or ("ANDROID_PRIVATE" in _os.environ)

def _data_dir():
    """Writable folder for settings + save file."""
    try:
        if IS_ANDROID:
            d = _os.environ.get("ANDROID_PRIVATE") or _os.environ.get("ANDROID_ARGUMENT")
            if d: return d
        if IS_WEB:
            d = "/data/data/supermarket2d"
            _os.makedirs(d, exist_ok=True)
            return d
    except Exception:
        pass
    return "."

DATA_DIR = _data_dir()

def _detect_quality_raw():
    score = 0
    info = []
    try:
        cores = _os.cpu_count() or 2
        info.append(f"CPU cores: {cores}")
        if cores <= 2: score += 0
        elif cores <= 4: score += 1
        else: score += 2
    except Exception:
        info.append("CPU cores: unknown")

    try:
        arch = _plat.machine()
        bits = 64 if ("64" in arch or "AMD64" in arch) else 32
        info.append(f"Architecture: {bits}-bit")
        if bits == 32:
            return 0, info
    except Exception:
        pass

    ram_gb = None
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        ram_gb = stat.ullTotalPhys / (1024 ** 3)
        info.append(f"RAM: {ram_gb:.1f} GB")
    except Exception:
        info.append("RAM: unknown")

    if ram_gb is not None:
        if ram_gb < 4: score += 0
        elif ram_gb < 8: score += 1
        else: score += 2

    if score <= 1:
        return 0, info
    elif score <= 3:
        return 1, info
    else:
        return 2, info

def _detect_quality():
    q, info = _detect_quality_raw()
    if IS_WEB:
        q = 0; info.append("Platform: web (forced POTATO)")
    elif IS_ANDROID:
        q = min(q, 1); info.append("Platform: Android (max NORMAL)")
    return q, info

QUALITY, _DEVICE_INFO = _detect_quality()
print("=" * 50)
print("[AUTO-DETECT] Device info:")
for _line in _DEVICE_INFO:
    print(f"  • {_line}")
_qname = 'POTATO' if QUALITY == 0 else 'NORMAL' if QUALITY == 1 else 'NASA'
print(f"[AUTO-DETECT] Quality level: {QUALITY} ({_qname})")
print("=" * 50)

import pygame, random, sys, math, json, os, struct, wave, io
from enum import Enum, auto
try:
    from mobile import TouchControls
except Exception as _ex:
    TouchControls = None
    print('[Touch] disabled:', _ex)

# ============ ARABIC SUPPORT ============
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_AR = True
except ImportError:
    HAS_AR = False
    print("[Lang] Install arabic-reshaper + python-bidi for proper Arabic")


# ============================================================
# SETTINGS
# ============================================================
class Settings:
    FILE = os.path.join(DATA_DIR, "settings.json")
    def __init__(self):
        self.data = {"language": "en", "fullscreen": False}
        self.load()
    def load(self):
        if os.path.exists(self.FILE):
            try:
                with open(self.FILE, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except Exception as ex: print("Settings load:", ex)
    def save(self):
        try:
            with open(self.FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as ex: print("Settings save:", ex)
    @property
    def lang(self): return self.data.get("language", "en")
    @property
    def fullscreen(self): return self.data.get("fullscreen", False)
    def toggle_lang(self):
        self.data["language"] = "ar" if self.lang == "en" else "en"
        self.save()
    def toggle_fullscreen(self):
        self.data["fullscreen"] = not self.fullscreen
        self.save()

SET = Settings()


# ============================================================
# LANGUAGE
# ============================================================
LANG = {
    "en": {
        "title1": "SUPERMARKET", "title2": "SIMULATOR 2D",
        "subtitle": "Manage · Hire · Catch thieves · Grow your empire",
        "new_game": "NEW GAME", "load_save": "LOAD SAVE",
        "settings": "SETTINGS", "quit": "QUIT",
        "resume": "RESUME", "save_game": "SAVE GAME",
        "main_menu": "MAIN MENU", "back": "BACK",
        "language": "Language", "fullscreen": "Fullscreen",
        "on": "ON", "off": "OFF", "done": "DONE",
        "settings_title": "SETTINGS", "controls": "Controls",
        "mouse_hint": "Click buttons · ESC to go back",
        "progression": "PROGRESSION", "pause_title": "PAUSED",
        "hire_title": "HIRE EMPLOYEES", "supplier_title": "WHOLESALE SUPPLIER",
        "day_end": "END OF DAY", "next_day": "NEXT DAY",
        "customers_served": "Customers served", "customers_lost": "Customers lost",
        "thieves_caught": "Thieves caught", "revenue": "Revenue",
        "purchases": "Purchases", "salaries": "Salaries", "profit": "Day profit",
        "total": "Total money", "level": "Store level", "rating": "Rating",
        "money": "MONEY", "skip": "SPACE to skip", "welcome": "WELCOME BACK",
        "best": "BEST", "goal": "Goal", "close": "CLOSE",
        "order": "ORDER", "hire": "HIRE", "you_won": "YOU PAID OFF THE DEBT!",
        "day": "DAY", "queue": "QUEUE", "served": "SERVED",
        "emp": "EMP", "lv": "LV",
    },
    "ar": {
        "title1": "سوبرماركت", "title2": "محاكي 2D",
        "subtitle": "أدر · وظّف · امسك اللصوص · كبّر إمبراطوريتك",
        "new_game": "لعبة جديدة", "load_save": "تحميل الحفظ",
        "settings": "الإعدادات", "quit": "خروج",
        "resume": "استئناف", "save_game": "حفظ اللعبة",
        "main_menu": "القائمة الرئيسية", "back": "رجوع",
        "language": "اللغة", "fullscreen": "شاشة كاملة",
        "on": "مفعّل", "off": "معطّل", "done": "تم",
        "settings_title": "الإعدادات", "controls": "التحكم",
        "mouse_hint": "اضغط الأزرار بالماوس · ESC للرجوع",
        "progression": "التطور", "pause_title": "إيقاف مؤقت",
        "hire_title": "توظيف موظفين", "supplier_title": "المورد بالجملة",
        "day_end": "نهاية اليوم", "next_day": "اليوم التالي",
        "customers_served": "عملاء تم خدمتهم", "customers_lost": "عملاء خسرتهم",
        "thieves_caught": "لصوص تم القبض عليهم", "revenue": "الإيرادات",
        "purchases": "المشتريات", "salaries": "الرواتب", "profit": "ربح اليوم",
        "total": "المال الكلي", "level": "مستوى المتجر", "rating": "التقييم",
        "money": "المال", "skip": "SPACE للتخطي", "welcome": "أهلاً بعودتك",
        "best": "الأفضل", "goal": "الهدف", "close": "إغلاق",
        "order": "اطلب", "hire": "وظّف", "you_won": "!سددت الدين",
        "day": "يوم", "queue": "طابور", "served": "خُدموا",
        "emp": "موظف", "lv": "مستوى",
    }
}

def tr(key):
    return LANG[SET.lang].get(key, key)

def shape_text(s):
    if SET.lang != "ar": return s
    if HAS_AR:
        try: return get_display(arabic_reshaper.reshape(s))
        except Exception: return s[::-1]
    return s[::-1]

def render_ar(font, text, color):
    return font.render(shape_text(str(text)), True, color)


# ============================================================
# CONFIG (Auto-tuned based on QUALITY)
# ============================================================
class CFG:
    if QUALITY == 0:       # 🥔 POTATO
        SW, SH = 800, 500
        FPS = 25
        PARTICLE_MULT = 0.25
        ENABLE_TINT = False
        CUSTOMER_CAP = 0.4
        SPRITE_SCALE = 1
    elif QUALITY == 1:     # 🎮 NORMAL
        SW, SH = 1280, 800
        FPS = 60
        PARTICLE_MULT = 1.0
        ENABLE_TINT = True
        CUSTOMER_CAP = 1.0
        SPRITE_SCALE = 4
    else:                  # 🚀 NASA
        SW, SH = 1600, 1000
        FPS = 60
        PARTICLE_MULT = 2.0
        ENABLE_TINT = True
        CUSTOMER_CAP = 1.5
        SPRITE_SCALE = 4

    HUD_H = max(70, int(SH * 0.097))
    WALL_T = 20
    START_MONEY = 80.0
    P_SPEED = 260.0
    P_SIZE = 30
    RADIUS = 110
    SAVE = os.path.join(DATA_DIR, "supermarket_save.json")
    THIEF_CHANCE = 0.10
    THIEF_BOUNTY = 3.0
    STEAL_PENALTY = 40.0
    DEBT_GOAL = 50000.0
    INTRO_SEC = 60.0
    LEVEL_MSG_SEC = 4.0

# Scale factor (based on 1280x800 reference)
SCALE = CFG.SW / 1280.0

def pcount(n):
    """Scaled particle count (respects quality)."""
    return max(1, int(n * CFG.PARTICLE_MULT))

def sx(v): return int(v * SCALE)
def sy(v): return int(v * SCALE)


class C:
    WHITE=(250,250,252); BLACK=(12,14,20); DARK=(24,28,40); DARKER=(16,20,30)
    RED=(240,90,95); GREEN=(80,215,120); GREEN_D=(45,165,90)
    BLUE=(90,150,240); YELLOW=(255,210,90); ORANGE=(255,165,80)
    PURPLE=(180,130,230); CYAN=(100,215,235)
    GRAY=(150,160,180); LGRAY=(210,215,225)
    GLASS_BG=(22,28,46,235); GLASS_BORDER=(90,130,210,200)
    GLASS_HL=(140,180,255,90); ACCENT=(100,200,255)
    STORAGE_FLOOR=(200,185,165)
    SHELF_WOOD=(165,115,70); SHELF_WOOD_D=(120,80,45); SHELF_WOOD_L=(200,155,110)
    COUNTER_C=(215,190,155); COUNTER_D=(165,140,110); COUNTER_L=(240,220,190)
    LOGO_YELLOW=(255,205,40); LOGO_YELLOW_D=(230,175,20)
    LOGO_GREEN=(120,200,80); LOGO_OUTLINE=(30,40,50)


# ============================================================
# GAME DATA
# ============================================================
LEVELS = [
    {"name":"Training","day_len":240,"max_cust":3,"spawn_rate":9.0,
     "shelf_cols":2,"shelf_rows":1,"unlock":2,"max_emp":1,"queue_max":3,
     "fc":(232,228,218),"wc":(75,82,100),"c_cost":200,"s_cost":150,"sal":0},
    {"name":"Very Easy","day_len":300,"max_cust":5,"spawn_rate":7.0,
     "shelf_cols":2,"shelf_rows":2,"unlock":3,"max_emp":2,"queue_max":3,
     "fc":(230,226,215),"wc":(78,85,105),"c_cost":250,"s_cost":180,"sal":5},
    {"name":"Easy","day_len":360,"max_cust":8,"spawn_rate":5.5,
     "shelf_cols":3,"shelf_rows":2,"unlock":4,"max_emp":3,"queue_max":4,
     "fc":(225,220,210),"wc":(80,90,115),"c_cost":350,"s_cost":250,"sal":10},
    {"name":"Medium","day_len":420,"max_cust":12,"spawn_rate":4.5,
     "shelf_cols":4,"shelf_rows":2,"unlock":5,"max_emp":4,"queue_max":5,
     "fc":(220,215,205),"wc":(70,85,110),"c_cost":450,"s_cost":350,"sal":20},
    {"name":"Medium+","day_len":480,"max_cust":16,"spawn_rate":3.8,
     "shelf_cols":4,"shelf_rows":2,"unlock":6,"max_emp":5,"queue_max":6,
     "fc":(215,210,200),"wc":(65,80,105),"c_cost":550,"s_cost":450,"sal":35},
    {"name":"Hard","day_len":540,"max_cust":22,"spawn_rate":3.0,
     "shelf_cols":4,"shelf_rows":3,"unlock":7,"max_emp":7,"queue_max":7,
     "fc":(210,205,195),"wc":(60,75,100),"c_cost":700,"s_cost":550,"sal":55},
    {"name":"Very Hard","day_len":600,"max_cust":30,"spawn_rate":2.3,
     "shelf_cols":5,"shelf_rows":3,"unlock":8,"max_emp":10,"queue_max":9,
     "fc":(205,200,190),"wc":(55,70,95),"c_cost":850,"s_cost":700,"sal":80},
    {"name":"EXTREME","day_len":660,"max_cust":45,"spawn_rate":1.5,
     "shelf_cols":5,"shelf_rows":4,"unlock":8,"max_emp":14,"queue_max":12,
     "fc":(200,195,185),"wc":(50,65,90),"c_cost":1100,"s_cost":900,"sal":130},
]
THRESHOLDS = [0, 500, 1500, 3500, 7000, 14000, 28000, 55000]

PRODUCTS = [
    {"key":"chips","name":"Chips","cost":1.5,"price":4.0,"unlock":0,"color":(255,205,85)},
    {"key":"soda","name":"Soda","cost":1.0,"price":3.0,"unlock":0,"color":(230,70,70)},
    {"key":"water","name":"Water","cost":0.5,"price":2.0,"unlock":0,"color":(140,215,250)},
    {"key":"candy","name":"Candy","cost":1.0,"price":3.0,"unlock":200,"color":(245,130,205)},
    {"key":"juice","name":"Juice","cost":2.0,"price":5.0,"unlock":500,"color":(255,175,75)},
    {"key":"bread","name":"Bread","cost":3.0,"price":7.0,"unlock":1200,"color":(215,170,115)},
    {"key":"milk","name":"Milk","cost":4.0,"price":9.0,"unlock":2500,"color":(250,250,255)},
    {"key":"cheese","name":"Cheese","cost":6.0,"price":12.0,"unlock":5000,"color":(250,220,100)},
]

STORY_EN = [
    ("Three months ago...", "Your father passed away.\nHe left you his small corner shop — and his debts."),
    ("The bank's final notice:", f"You have 30 days to pay ${CFG.DEBT_GOAL:,.0f}.\nOtherwise the shop is gone."),
    ("But you refuse to give up.", "You'll work the register.\nYou'll restock the shelves.\nYou'll grow it into an empire."),
    ("This is your story.", "Every customer matters. Every dollar counts.\n\nLet's begin."),
]
STORY_AR = [
    ("منذ ثلاثة أشهر...", "توفي والدك.\nترك لك متجره الصغير — وديونه."),
    ("الإشعار الأخير من البنك:", f"لديك 30 يوماً لسداد {CFG.DEBT_GOAL:,.0f}$.\nوإلا سيتم بيع المتجر."),
    ("لكنك رفضت الاستسلام.", "ستعمل على الصندوق.\nستملأ الرفوف.\nستحوّله إلى إمبراطورية."),
    ("هذه قصتك.", "كل عميل مهم. كل دولار يُحسب.\n\nهيا نبدأ."),
]

def get_story():
    return STORY_AR if SET.lang == "ar" else STORY_EN

def level_index(e):
    lv = 0
    for i, t in enumerate(THRESHOLDS):
        if e >= t: lv = i
    return min(lv, len(LEVELS)-1)

def prod(k):
    for p in PRODUCTS:
        if p["key"] == k: return p
    return None


# ============================================================
# ASSETS
# ============================================================
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def load_img(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    if not os.path.exists(path): return None
    try:
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as ex:
        print(f"[Asset] {name}: {ex}"); return None

LOGO = None
SPRITES = {}
TOUCH = None

def mk_font(size, bold=False):
    desktop = not (IS_ANDROID or IS_WEB)
    if desktop:
        try:
            if pygame.font.match_font("tahoma"):
                return pygame.font.SysFont("Tahoma", size, bold=bold)
        except Exception:
            pass
    for fn in (("font_bold.ttf" if bold else "font.ttf"), "font.ttf"):
        p = os.path.join(ASSET_DIR, fn)
        if os.path.exists(p):
            try: return pygame.font.Font(p, size)
            except Exception as ex: print("[Font]", ex)
    return pygame.font.SysFont("Tahoma", size, bold=bold)


# ============================================================
# AUDIO (procedural, halal — no music)
# ============================================================
SR = 44100

def _pack(buf):
    d = struct.pack(f"<{len(buf)}h", *buf)
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(d)
    bio.seek(0)
    return pygame.mixer.Sound(bio)

def tone(f=440, dur=0.08, wt="sine", vol=0.4, f2=None):
    n = int(SR*dur); b=[]
    for i in range(n):
        t = i/SR
        fr = f + (f2-f)*(i/n) if f2 else f
        ph = 2*math.pi*fr*t
        if wt=="sine": s = math.sin(ph)
        elif wt=="square": s = 1.0 if math.sin(ph)>0 else -1.0
        else: s = 2*((fr*t)%1.0)-1.0
        b.append(int(s*(1.0-i/n)*vol*32767))
    return _pack(b)

def seq(fs, dur=0.06, vol=0.35):
    ne = int(SR*dur); b=[]
    for f in fs:
        for i in range(ne):
            t = i/SR
            b.append(int(math.sin(2*math.pi*f*t)*(1-i/ne)*vol*32767))
    return _pack(b)

def noise(dur=0.05, vol=0.15, hp=False):
    n = int(SR*dur); b=[]; pv=0
    for i in range(n):
        s = random.uniform(-1,1)
        if hp: s = s - pv*0.8; pv = s
        b.append(int(s*(1-i/n)*vol*32767))
    return _pack(b)

class Audio:
    def __init__(self):
        self.sfx = {}
        try:
            self.sfx["scan"]=seq([880,1100],0.055,0.4)
            self.sfx["paid"]=seq([523,659,784,1047],0.07,0.35)
            self.sfx["restock"]=tone(330,0.09,"sine",0.3,440)
            self.sfx["order"]=seq([440,550],0.065,0.3)
            self.sfx["hire"]=seq([392,523,659],0.07,0.35)
            self.sfx["lose"]=tone(200,0.18,"sine",0.25,120)
            self.sfx["dayend"]=seq([523,587,659,698,784],0.09,0.35)
            self.sfx["daystart"]=seq([659,784],0.08,0.3)
            self.sfx["lvlup"]=seq([392,523,659,784,1047,1318],0.08,0.38)
            self.sfx["click"]=tone(600,0.03,"square",0.2)
            self.sfx["error"]=seq([200,180],0.08,0.3)
            self.sfx["step"]=noise(0.04,0.12,True)
            self.sfx["alarm"]=seq([440,330,440,330],0.12,0.35)
            self.sfx["ching"]=seq([1200,1800],0.05,0.4)
            self.sfx["busted"]=seq([660,880,1320,1760],0.09,0.42)
            self.sfx["steal"]=tone(150,0.25,"sine",0.3,80)
            self.sfx["story"]=seq([330,440],0.15,0.25)
        except Exception as ex: print("Audio:", ex)
    def play(self, n):
        try:
            if n in self.sfx: self.sfx[n].play()
        except: pass


# ============================================================
# UI HELPERS
# ============================================================
def soft_shadow(surf, rect, radius=20, spread=14, alpha=130, offset_y=6):
    for i in range(spread, 0, -1):
        a = int(alpha * (1 - i/spread) ** 2)
        r = rect.inflate(i*2, i*2).move(0, offset_y)
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0,0,0,a), s.get_rect(), border_radius=radius+i)
        surf.blit(s, r.topleft)

def glass_panel(surf, rect, radius=20, bg=None, border=None):
    if bg is None: bg = C.GLASS_BG
    if border is None: border = C.GLASS_BORDER
    soft_shadow(surf, rect, radius, spread=16, alpha=140)
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, bg, s.get_rect(), border_radius=radius)
    surf.blit(s, rect.topleft)
    hl = pygame.Surface((rect.w, 3), pygame.SRCALPHA)
    hl.fill(C.GLASS_HL)
    surf.blit(hl, (rect.x+8, rect.y+1))
    pygame.draw.rect(surf, border, rect, 2, border_radius=radius)

def gradient_rect(surf, rect, top, bottom, radius=0):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h-1)
        c = tuple(int(top[i] + (bottom[i]-top[i])*t) for i in range(3))
        pygame.draw.line(s, c, (0, y), (rect.w, y))
    if radius > 0:
        mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=radius)
        s.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(s, rect.topleft)

def glow_circle(surf, cx, cy, r, color, alpha=100, layers=5):
    for i in range(layers, 0, -1):
        a = int(alpha * (1 - i/layers) / 3)
        s = pygame.Surface((r*2+i*4, r*2+i*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (r+i*2, r+i*2), r+i*2)
        surf.blit(s, (cx-r-i*2, cy-r-i*2))

def draw_gradient_bg(surf):
    for y in range(0, CFG.SH, 4):
        t = y / CFG.SH
        r = int(18 + 30*t); g = int(20 + 20*t); b = int(35 + 40*t)
        pygame.draw.rect(surf, (r,g,b), (0, y, CFG.SW, 4))

def draw_modern_bg(surf, anim=0.0):
    draw_gradient_bg(surf)
    n_dots = 40 if QUALITY > 0 else 12
    for i in range(n_dots):
        sxx = (i*137 + int(anim*15*(i%3+1))) % CFG.SW
        syy = (i*91 + int(anim*10*((i+1)%3+1))) % CFG.SH
        r = 1 + i%3
        s = pygame.Surface((r*6, r*6), pygame.SRCALPHA)
        pygame.draw.circle(s, (120,180,255,40), (r*3, r*3), r*3)
        surf.blit(s, (sxx-r*3, syy-r*3))


# ============================================================
# BUTTON
# ============================================================
class Button:
    def __init__(self, rect, text, action, style="primary",
                 accent=None, bg=None, font=None, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.style = style
        self.accent = accent or C.GREEN
        self.bg = bg or (30, 90, 55)
        self.font = font
        self.enabled = enabled
        self.hovered = False
        self._pressed = False
        # Cache font at 60% for subtitle
        self._sub_font = None
    def update_hover(self, mp):
        self.hovered = self.enabled and self.rect.collidepoint(mp)
    def handle_event(self, ev, audio=None):
        if not self.enabled: return False
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                self._pressed = True
                return False
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if self._pressed and self.rect.collidepoint(ev.pos):
                self._pressed = False
                if audio: audio.play("click")
                self.action()
                return True
            self._pressed = False
        return False
    def draw(self, surf, render_fn):
        soft_shadow(surf, self.rect, 14, spread=10, alpha=90)
        base = self.bg
        if self.hovered and self.enabled:
            base = tuple(min(255, c+20) for c in base)
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, base, s.get_rect(), border_radius=14)
        surf.blit(s, self.rect.topleft)
        for i in range(self.rect.h//3):
            a = int(45 * (1 - i/(self.rect.h/3)))
            pygame.draw.line(surf, (*self.accent, a),
                             (self.rect.x+2, self.rect.y+i+2),
                             (self.rect.right-2, self.rect.y+i+2))
        border_col = self.accent if self.enabled else C.GRAY
        if self.hovered:
            border_col = tuple(min(255, c+40) for c in self.accent)
        pygame.draw.rect(surf, border_col, self.rect, 2, border_radius=14)
        if self.font:
            txt_col = C.WHITE if self.enabled else C.GRAY
            t = render_fn(self.font,
                tr(self.text) if self.text in LANG[SET.lang] else self.text, txt_col)
            surf.blit(t, (self.rect.centerx-t.get_width()//2,
                          self.rect.centery-t.get_height()//2))


# ============================================================
# SPRITE HELPERS
# ============================================================
SPRITE_SCALE = CFG.SPRITE_SCALE

def smooth_circle(color, r):
    size = r * 2
    big = pygame.Surface((size*SPRITE_SCALE, size*SPRITE_SCALE), pygame.SRCALPHA)
    pygame.draw.circle(big, color, (size*SPRITE_SCALE//2, size*SPRITE_SCALE//2),
                       r*SPRITE_SCALE)
    return pygame.transform.smoothscale(big, (size, size))


# ============================================================
# UTILITIES
# ============================================================
class Shake:
    def __init__(self): self.a = 0.0
    def add(self, x): self.a = min(30.0, self.a + x)
    def update(self, dt):
        if self.a > 0: self.a = max(0.0, self.a - 90.0*dt)
    def off(self):
        if self.a <= 0: return (0,0)
        i = int(self.a); return (random.randint(-i,i), random.randint(-i,i))

class FloatText:
    def __init__(self, x, y, text, color=C.GREEN, big=False, life=1.2):
        self.x=x; self.y=y; self.text=text; self.color=color
        self.life=life; self.max=life; self.big=big
    def update(self, dt):
        self.y -= 70*dt; self.life -= dt; return self.life > 0
    def draw(self, s, fb, fs, ox=0, oy=0):
        a = int(255*max(0,self.life)/self.max)
        f = fb if self.big else fs
        t = f.render(self.text, True, self.color); t.set_alpha(a)
        bg = pygame.Surface((t.get_width()+10, t.get_height()+6), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0,0,0,int(a*0.6)), bg.get_rect(), border_radius=6)
        s.blit(bg, (self.x-t.get_width()//2-5+ox, int(self.y)-3+oy))
        s.blit(t, (self.x-t.get_width()//2+ox, int(self.y)+oy))

class Particle:
    def __init__(self, x, y, color, variant="star"):
        self.x = x+random.randint(-15,15); self.y = y+random.randint(-10,10)
        self.vx = random.uniform(-150,150); self.vy = random.uniform(-260,-80)
        self.color = color; self.life = random.uniform(0.5,0.9)
        self.max = self.life; self.r = random.randint(3,7); self.v = variant
    def update(self, dt):
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += 500*dt; self.life -= dt
        return self.life > 0
    def draw(self, s, ox=0, oy=0):
        a = max(0, int(255*self.life/self.max))
        if self.v == "star":
            c = smooth_circle((*self.color, a), self.r)
            s.blit(c, (int(self.x-self.r+ox), int(self.y-self.r+oy)))
        else:
            sz = self.r*2
            big = pygame.Surface((sz*4, sz*4), pygame.SRCALPHA)
            pygame.draw.polygon(big, (*self.color, a),
                [(sz*2,0),(sz*4,sz*2),(sz*2,sz*4),(0,sz*2)])
            sm = pygame.transform.smoothscale(big, (sz, sz))
            s.blit(sm, (int(self.x-self.r+ox), int(self.y-self.r+oy)))

def time_tint(p):
    p = max(0.0, min(1.0, p))
    if p < 0.25: return (0,0,0,0)
    if p < 0.55:
        t = (p-0.25)/0.30; return (255,210,130,int(20*t))
    if p < 0.80:
        t = (p-0.55)/0.25; return (255,130,70,int(20+45*t))
    t = (p-0.80)/0.20; return (30,20,80,int(65+85*t))

def phase_label(p):
    if p < 0.25: return "MORNING"
    if p < 0.55: return "NOON"
    if p < 0.80: return "SUNSET"
    return "CLOSING"

def phase_col(p):
    if p < 0.25: return (255,240,200)
    if p < 0.55: return (255,255,200)
    if p < 0.80: return (255,180,100)
    return (140,140,220)


# ============================================================
# ENTITIES
# ============================================================
class Shelf:
    def __init__(self, key, rect, maxs=20):
        self.key = key; self.stock = 0; self.max = maxs; self.rect = rect
    @property
    def product(self): return prod(self.key) or PRODUCTS[0]
    def restock(self, a):
        add = min(self.max - self.stock, a); self.stock += add; return add
    def take(self):
        if self.stock <= 0: return False
        self.stock -= 1; return True

class CState(Enum):
    ENTER=auto(); SHOP=auto(); PICK=auto(); TOQ=auto()
    INQ=auto(); PAY=auto(); LEAVE=auto(); BUST=auto()

class CKind(Enum):
    NORMAL=auto(); VIP=auto(); THIEF=auto()

class Customer:
    def __init__(self, unlocked, kind=CKind.NORMAL):
        self.kind = kind
        self.rect = pygame.Rect(0,0,26,26); self.rect.center = (650, CFG.SH-10)
        self.speed = random.uniform(90,145)
        if kind == CKind.VIP: self.speed = random.uniform(60,90)
        self.shirt = random.choice([(240,130,170),(245,180,120),(155,200,240),
            (200,220,150),(225,160,225),(200,200,200),(170,220,220),(250,200,150)])
        if kind == CKind.VIP: self.shirt = (255,215,0)
        if kind == CKind.THIEF: self.shirt = (40,40,45)
        self.skin = random.choice([(255,220,180),(230,190,150),(200,155,115)])
        self.hair = random.choice([(50,35,25),(100,60,35),(25,25,30),(150,100,50)])
        self.wants=[]; self.basket=[]; self.state=CState.ENTER
        self.target=None; self.wait=0.0
        self.patience = random.uniform(5.0,10.0); self.qw=0.0
        self._pick(unlocked)
    def _pick(self, u):
        if not u: return
        n = random.randint(1, min(4, len(u)))
        self.wants = random.sample([p["key"] for p in u], n)
    def _target(self, shelves):
        while self.wants:
            k = self.wants[0]
            for s in shelves:
                if s.key == k and s.stock > 0:
                    self.target = s; return True
            self.wants.pop(0)
        self.target = None; return False
    def bval(self):
        return sum(prod(k)["price"] for k in self.basket if prod(k))
    def sus(self):
        return (self.kind == CKind.THIEF
                and self.state in (CState.SHOP, CState.PICK)
                and len(self.basket) > 0)

class EKind(Enum):
    CASHIER=auto(); STOCKER=auto(); GUARD=auto(); CLEANER=auto()

EINFO = {
    EKind.CASHIER:{"name":"Cashier","color":(100,180,240),"speed":120,"label":"C"},
    EKind.STOCKER:{"name":"Stocker","color":(240,150,100),"speed":130,"label":"S"},
    EKind.GUARD:{"name":"Guard","color":(200,80,80),"speed":110,"label":"G"},
    EKind.CLEANER:{"name":"Cleaner","color":(180,240,180),"speed":140,"label":"L"},
}

class Employee:
    def __init__(self, kind):
        self.kind = kind; info = EINFO[kind]
        self.rect = pygame.Rect(0,0,26,26)
        self.speed = info["speed"]; self.color = info["color"]; self.label = info["label"]
        self.task=None; self.target=None; self.cd=0.0; self.wander=None; self.anim=0.0
        if kind == EKind.CASHIER: self.rect.center = (1010,620)
        elif kind in (EKind.STOCKER, EKind.CLEANER): self.rect.center = (150,520)
        else: self.rect.center = (200,680)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0,0,CFG.P_SIZE,CFG.P_SIZE)
        self.rect.center = (1050,720)
        self.speed = CFG.P_SPEED
        self.money = CFG.START_MONEY; self.earned = 0.0; self.spent = 0.0
        self.rating = 3.0; self.level = 0
        self.day = 1; self.day_time = 0.0
        self.served=0; self.lost=0
        self.de=0.0; self.ds=0.0
        self.tserved=0; self.tlost=0; self.caught=0
        self.back = {p["key"]:0 for p in PRODUCTS}
        self.back["chips"]=20; self.back["soda"]=10; self.back["water"]=10
    def afford(self, c): return self.money >= c
    def spend(self, a):
        if not self.afford(a): return False
        self.money -= a; self.spent += a; self.ds += a; return True
    def earn(self, a):
        self.money += a; self.earned += a; self.de += a
    def move(self, dx, dy, dt, obs):
        ox = self.rect.x
        self.rect.x += int(dx*self.speed*dt)
        for r in obs:
            if self.rect.colliderect(r): self.rect.x = ox; break
        oy = self.rect.y
        self.rect.y += int(dy*self.speed*dt)
        for r in obs:
            if self.rect.colliderect(r): self.rect.y = oy; break
        self.rect.x = max(CFG.WALL_T+4, min(CFG.SW-CFG.WALL_T-4-self.rect.w, self.rect.x))
        self.rect.y = max(CFG.HUD_H+CFG.WALL_T+4,
                          min(CFG.SH-CFG.WALL_T-4-self.rect.h, self.rect.y))
    def unlocked(self): return PRODUCTS[:LEVELS[self.level]["unlock"]]
    def lv(self): return LEVELS[self.level]


# ============================================================
# GEOMETRY
# ============================================================
HUD_RECT = pygame.Rect(0,0,CFG.SW,CFG.HUD_H)
STORE_RECT = pygame.Rect(CFG.WALL_T, CFG.HUD_H+CFG.WALL_T, 220, 240)
STORE_WALL = pygame.Rect(CFG.WALL_T+220, CFG.HUD_H+CFG.WALL_T, CFG.WALL_T, 240)
STORE_DOOR = pygame.Rect(CFG.WALL_T+220, CFG.HUD_H+CFG.WALL_T+90, CFG.WALL_T, 70)
PC_RECT = pygame.Rect(40, CFG.HUD_H+55, 60, 70)
COUNTER = pygame.Rect(int(CFG.SW*0.6875), int(CFG.SH*0.7375), 320, 110)
REGISTER = pygame.Rect(int(CFG.SW*0.867), int(CFG.SH*0.7625), 70, 50)
ENTRANCE = pygame.Rect(CFG.SW//2-90, CFG.SH-CFG.WALL_T, 180, CFG.WALL_T)
QFRONT = (int(CFG.SW*0.789), int(CFG.SH*0.68))
QSPACE = 65

def mv(rect, tx, ty, sp):
    dx = tx - rect.centerx; dy = ty - rect.centery
    d = math.hypot(dx, dy)
    if d < sp or d < 1:
        rect.centerx = int(tx); rect.centery = int(ty); return True
    rect.x += int(dx/d*sp); rect.y += int(dy/d*sp)
    return False


# ============================================================
# GAME STATE
# ============================================================
class Ev:
    def __init__(self, kind, dur): self.kind = kind; self.dur = dur; self.tl = dur
    def tick(self, dt): self.tl -= dt; return self.tl > 0

class GS:
    def __init__(self, audio):
        self.audio = audio
        self.player = Player()
        self.shelves = []
        self.customers=[]; self.employees=[]; self.queue=[]
        self.floats=[]; self.particles=[]; self.events=[]
        self.shake = Shake()
        self.state = "MENU"
        self.spawn_t = 0.0; self.step_t = 0.0; self.ev_cd = 25.0
        self.msg = ""; self.msg_t = 0.0
        self.lvl_flash = 0.0
        self.scan_anim = 0.0; self.scan_pos = (0,0)
        self.end_summary = {}; self.prev_lvl = 0
        self.tutorial = 0
        self.intro_idx = 0; self.intro_t = 0.0
        self.high = {"best_day":0,"best_profit":0.0,"best_rating":0.0,"best_level":0,
                     "unlocked_level":0}  # <-- for progressive unlock
        self.game_won = False
        self.prev_state = "MENU"
        self._rebuild()
    def show(self, t, d=1.5): self.msg = t; self.msg_t = d
    def _rebuild(self):
        lv = LEVELS[self.player.level]
        cols = lv["shelf_cols"]; rows = lv["shelf_rows"]
        total = cols*rows; keys = [p["key"] for p in PRODUCTS]
        self.shelves.clear()
        SH_W, SH_H = 165, 76; GX, GY = 35, 105
        X0, Y0 = 300, 180
        for i in range(total):
            r, c = i//cols, i%cols
            x = X0 + c*(SH_W+GX); y = Y0 + r*(SH_H+GY)
            self.shelves.append(Shelf(keys[i%len(keys)], pygame.Rect(x,y,SH_W,SH_H)))
    def new_game(self):
        self.player = Player()
        self.customers.clear(); self.employees.clear(); self.queue.clear()
        self.floats.clear(); self.particles.clear(); self.events.clear()
        self.prev_lvl = 0; self.tutorial = 0; self.ev_cd = 25.0
        self.game_won = False
        self.intro_idx = 0; self.intro_t = 0.0
        self.lvl_flash = 0.0
        self._rebuild()
        self.state = "INTRO"
        self.audio.play("story")
    def save(self):
        try:
            d = {"version":4,
                "player":{"money":self.player.money,"earned":self.player.earned,
                    "spent":self.player.spent,"rating":self.player.rating,
                    "level":self.player.level,"day":self.player.day,
                    "tserved":self.player.tserved,"tlost":self.player.tlost,
                    "caught":self.player.caught,"back":self.player.back},
                "shelves":[{"p":s.key,"s":s.stock} for s in self.shelves],
                "employees":[{"k":e.kind.name} for e in self.employees],
                "high":self.high}
            with open(CFG.SAVE,"w",encoding="utf-8") as f: json.dump(d,f,indent=2)
            return True
        except Exception as ex:
            self.show(f"Save failed: {ex}",3.0); return False
    def load(self):
        if not os.path.exists(CFG.SAVE): return False
        try:
            with open(CFG.SAVE,"r",encoding="utf-8") as f: d = json.load(f)
            p = d.get("player",{})
            self.player.money = p.get("money", CFG.START_MONEY)
            self.player.earned = p.get("earned",0.0)
            self.player.spent = p.get("spent",0.0)
            self.player.rating = p.get("rating",3.0)
            self.player.level = p.get("level",0)
            self.player.day = p.get("day",1)
            self.player.tserved = p.get("tserved",0)
            self.player.tlost = p.get("tlost",0)
            self.player.caught = p.get("caught",0)
            self.player.day_time = 0.0
            self.player.served = 0; self.player.lost = 0
            self.player.de = 0.0; self.player.ds = 0.0
            self.player.rect.center = (int(CFG.SW*0.82), int(CFG.SH*0.9))
            br = p.get("back",{})
            for k in self.player.back: self.player.back[k] = int(br.get(k,0))
            self.high.update(d.get("high",{}))
            self._rebuild()
            sm = {s["p"]:s["s"] for s in d.get("shelves",[])}
            for s in self.shelves: s.stock = int(sm.get(s.key,0))
            self.employees.clear()
            for e in d.get("employees",[]):
                try: self.employees.append(Employee(EKind[e["k"]]))
                except KeyError: pass
            self.customers.clear(); self.queue.clear()
            self.floats.clear(); self.particles.clear(); self.events.clear()
            self.prev_lvl = self.player.level
            self.tutorial = 6
            self.intro_idx = 0
            self.lvl_flash = 0.0
            return True
        except Exception as ex:
            self.show(f"Load failed: {ex}",3.0); return False

    def update(self, dt):
        if self.state == "INTRO":
            self.intro_t += dt
            if self.intro_t >= CFG.INTRO_SEC:
                self._advance_intro()
            self.shake.update(dt)
            if self.msg_t > 0: self.msg_t -= dt
            return
        if self.state != "PLAY":
            if self.msg_t > 0: self.msg_t -= dt
            if self.lvl_flash > 0: self.lvl_flash -= dt
            self.shake.update(dt)
            return
        self.player.day_time += dt
        self._move_player(dt)
        self._check_level()
        self._events(dt)
        self._spawn(dt)
        self._employees(dt)
        self._customers(dt)
        self._floats_parts(dt)
        self.shake.update(dt)
        if self.lvl_flash > 0: self.lvl_flash -= dt
        if self.scan_anim > 0: self.scan_anim -= dt*60
        if self.msg_t > 0: self.msg_t -= dt
        if self.player.day_time >= self.player.lv()["day_len"]:
            self._end_day()

    def _advance_intro(self):
        self.intro_idx += 1
        self.intro_t = 0.0
        if self.intro_idx >= len(get_story()):
            self.audio.play("daystart")
            self.state = "PLAY"

    def _move_player(self, dt):
        keys = pygame.key.get_pressed()
        dx=dy=0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy+=1
        if dx and dy: dx*=0.707; dy*=0.707
        if TOUCH is not None and not (dx or dy) and (TOUCH.vx or TOUCH.vy):
            dx, dy = TOUCH.vx, TOUCH.vy
        if dx or dy:
            self.step_t += dt*60
            if self.step_t >= 18:
                self.step_t = 0; self.audio.play("step")
        obs = [s.rect for s in self.shelves]
        obs.append(COUNTER); obs.append(STORE_WALL)
        self.player.move(dx, dy, dt, obs)

    def _check_level(self):
        n = level_index(self.player.earned)
        if n > self.player.level:
            self.player.level = n
            self._rebuild()
            self.lvl_flash = CFG.LEVEL_MSG_SEC
            self.audio.play("lvlup")
            self.show(f"LEVEL UP! {LEVELS[n]['name']}", CFG.LEVEL_MSG_SEC)
            for _ in range(pcount(50)):
                self.particles.append(Particle(CFG.SW//2, CFG.SH//2, (100,255,100)))
            self.shake.add(10)
            # Update unlock tracker
            if n > self.high.get("unlocked_level", 0):
                self.high["unlocked_level"] = n

    def _events(self, dt):
        if self.ev_cd > 0: self.ev_cd -= dt
        for e in list(self.events):
            if not e.tick(dt): self.events.remove(e)
        if self.ev_cd <= 0 and not self.events:
            r = random.random(); lv = self.player.lv()
            if r < 0.35 and lv["max_cust"] > 10:
                self.events.append(Ev("rush",15.0))
                self.show("RUSH HOUR!",3.0); self.audio.play("alarm")
            elif r < 0.55:
                self.events.append(Ev("vip",20.0))
                self.show("VIP customer!",3.0)
            elif r < 0.80:
                for p in self.player.unlocked(): self.player.back[p["key"]] += 5
                self.events.append(Ev("delivery",3.0))
                self.show("Free delivery +5 each",3.0); self.audio.play("order")
            else:
                self.events.append(Ev("outage",10.0))
                self.show("POWER OUTAGE!",3.0); self.audio.play("alarm")
            self.ev_cd = random.uniform(40.0,70.0)

    def _spawn(self, dt):
        lv = self.player.lv()
        m = 0.7 + self.player.rating * 0.15
        self.spawn_t += dt * m
        rate = lv["spawn_rate"]
        for e in self.events:
            if e.kind == "rush": rate *= 0.4
        if self.spawn_t >= rate:
            self.spawn_t = 0
            cap = int(lv["max_cust"] * CFG.CUSTOMER_CAP)
            if len(self.customers) < cap:
                k = CKind.NORMAL; r = random.random()
                if any(e.kind=="vip" for e in self.events) and r < 0.30: k = CKind.VIP
                elif r < CFG.THIEF_CHANCE: k = CKind.THIEF
                self.customers.append(Customer(self.player.unlocked(), k))

    def _employees(self, dt):
        for e in self.employees:
            if e.anim > 0: e.anim -= dt*60
            if e.kind == EKind.CASHIER: self._cashier(e, dt)
            elif e.kind == EKind.STOCKER: self._stocker(e, dt)
            elif e.kind == EKind.GUARD: self._guard(e, dt)
            elif e.kind == EKind.CLEANER: self._cleaner(e, dt)

    def _cashier(self, e, dt):
        if e.cd > 0: e.cd -= dt; return
        mv(e.rect, 1010, 620, e.speed*dt)
        if not self.queue: return
        c = self.queue[0]
        if c.state not in (CState.PAY, CState.INQ) or not c.basket: return
        k = c.basket.pop(0); p = prod(k)
        if not p: return
        self.player.earn(p["price"])
        self.floats.append(FloatText(REGISTER.centerx, REGISTER.y-10,
            f"+${p['price']:.2f}", C.GREEN, big=True))
        for _ in range(pcount(8)):
            self.particles.append(Particle(REGISTER.centerx, REGISTER.centery,
                (100,220,100), "coin"))
        self.audio.play("scan"); self.shake.add(1.5)
        e.cd = 0.65; e.anim = 6
        if not c.basket:
            self.player.served += 1; self.player.tserved += 1
            self.player.rating = min(5.0, self.player.rating + 0.03)
            self.floats.append(FloatText(c.rect.centerx, c.rect.y-20, "PAID!",
                C.YELLOW, big=True))
            self.audio.play("paid")

    def _stocker(self, e, dt):
        if e.cd > 0:
            e.cd -= dt
            if e.cd <= 0 and e.task == "restock" and e.target:
                s = e.target; pk = s.key
                if self.player.back[pk] > 0 and s.stock < s.max:
                    a = min(s.max-s.stock, self.player.back[pk], 5)
                    s.restock(a); self.player.back[pk] -= a
                    self.floats.append(FloatText(s.rect.centerx, s.rect.y-10, f"+{a}", C.GREEN))
                    e.cd = 0.55
                    if s.stock >= s.max or self.player.back[pk] == 0:
                        e.task = None; e.target = None
                else: e.task = None; e.target = None
            return
        if e.target is None:
            cands = [s for s in self.shelves
                     if self.player.back[s.key] > 0 and s.stock < s.max*0.6]
            if cands: e.target = cands[0]; e.task = "to_shelf"
            else:
                if e.task != "wander" or e.wander is None:
                    e.task = "wander"
                    e.wander = (random.randint(300,1150), random.randint(180,700))
                if mv(e.rect, e.wander[0], e.wander[1], e.speed*0.6*dt):
                    e.wander = None; e.task = None
            return
        s = e.target
        if mv(e.rect, s.rect.centerx, s.rect.bottom+30, e.speed*dt):
            e.task = "restock"; e.cd = 0.4

    def _guard(self, e, dt):
        if e.wander is None or random.random() < 0.005:
            e.wander = (random.randint(500,750), random.randint(550,720))
        mv(e.rect, e.wander[0], e.wander[1], e.speed*0.5*dt)
        if e.rect.centerx > 490: e.wander = None

    def _cleaner(self, e, dt):
        if e.cd > 0: e.cd -= dt; return
        self.player.rating = min(5.0, self.player.rating + 0.001)
        e.cd = 2.0
        if e.wander is None or random.random() < 0.008:
            e.wander = (random.randint(280,900), random.randint(180,720))
        mv(e.rect, e.wander[0], e.wander[1], e.speed*0.4*dt)

    def _customers(self, dt):
        for c in list(self.customers):
            if self._one(c, dt) == "rm": self.customers.remove(c)

    def _one(self, c, dt):
        lv = self.player.lv()
        gb = sum(1 for e in self.employees if e.kind == EKind.GUARD)*0.5
        if c.kind == CKind.THIEF and c.state == CState.SHOP and c.basket and len(c.basket) >= 2:
            if random.random() < 0.005:
                c.state = CState.LEAVE
                self.show("Thief escaping!",2.0); self.audio.play("steal")
        if c.state == CState.ENTER:
            if c.rect.centery > 500: c.rect.y -= int(c.speed*dt)
            else: c.state = CState.SHOP
        elif c.state == CState.SHOP:
            if c.target is None:
                if not c._target(self.shelves):
                    if c.basket: c.state = CState.TOQ
                    else:
                        self.player.lost += 1; self.player.tlost += 1
                        self.player.rating = max(1.0, self.player.rating - 0.12)
                        self.audio.play("lose"); c.state = CState.LEAVE
                    return None
            s = c.target
            if mv(c.rect, s.rect.centerx, s.rect.bottom+28, c.speed*dt):
                c.state = CState.PICK; c.wait = 22.0
        elif c.state == CState.PICK:
            c.wait -= dt*60
            if c.wait <= 0:
                s = c.target
                if s and s.take():
                    c.basket.append(s.key)
                    self.floats.append(FloatText(s.rect.centerx, s.rect.y-10, "-1", C.YELLOW))
                if c.wants: c.wants.pop(0)
                c.target = None; c.state = CState.SHOP
        elif c.state == CState.TOQ:
            if c not in self.queue:
                qm = lv["queue_max"] + int(gb)
                if len(self.queue) < qm: self.queue.append(c)
                else:
                    self.player.lost += 1; self.player.tlost += 1
                    self.player.rating = max(1.0, self.player.rating - 0.12)
                    self.audio.play("lose"); c.state = CState.LEAVE; return None
            i = self.queue.index(c); tx = QFRONT[0] - i*QSPACE
            if mv(c.rect, tx, QFRONT[1], c.speed*dt): c.state = CState.INQ
        elif c.state == CState.INQ:
            if c not in self.queue: c.state = CState.LEAVE; return None
            i = self.queue.index(c)
            if i == 0: c.state = CState.PAY
            else:
                c.qw += dt
                if c.qw > c.patience:
                    self.queue.remove(c)
                    self.player.lost += 1; self.player.tlost += 1
                    self.player.rating = max(1.0, self.player.rating - 0.1)
                    self.audio.play("lose"); c.state = CState.LEAVE; return None
                tx = QFRONT[0] - i*QSPACE
                mv(c.rect, tx, QFRONT[1], c.speed*0.6*dt)
        elif c.state == CState.PAY:
            if not c.basket:
                if c in self.queue: self.queue.remove(c)
                c.state = CState.LEAVE
        elif c.state == CState.BUST:
            c.wait -= dt
            if c.wait <= 0: c.state = CState.LEAVE
        elif c.state == CState.LEAVE:
            if c in self.queue: self.queue.remove(c)
            if c.kind == CKind.THIEF and c.basket and not hasattr(c,"_st"):
                c._st = True
                loss = c.bval() * CFG.STEAL_PENALTY / 40.0
                self.player.money = max(0, self.player.money - loss)
                self.player.rating = max(1.0, self.player.rating - 0.25)
                self.floats.append(FloatText(c.rect.centerx, c.rect.y-20,
                    f"STOLEN! -${loss:.0f}", C.RED, big=True))
                self.show("Thief escaped!",2.5); self.audio.play("steal")
                self.shake.add(6)
            if mv(c.rect, CFG.SW//2+50, CFG.SH+20, c.speed*dt): return "rm"
            if c.rect.top > CFG.SH+30: return "rm"
        return None

    def _floats_parts(self, dt):
        for f in list(self.floats):
            if not f.update(dt): self.floats.remove(f)
        for p in list(self.particles):
            if not p.update(dt): self.particles.remove(p)

    def _end_day(self):
        lv = self.player.lv()
        sal = len(self.employees) * lv["sal"]
        self.player.money = max(0.0, self.player.money - sal)
        self.player.spent += sal
        profit = self.player.de - self.player.ds - sal
        leveled = self.player.level > self.prev_lvl
        self.prev_lvl = self.player.level
        self.end_summary = {"day":self.player.day,"earned":self.player.de,
            "spent":self.player.ds,"served":self.player.served,
            "lost":self.player.lost,"money":self.player.money,"profit":profit,
            "rating":self.player.rating,"level":self.player.level,
            "salaries":sal,"leveled_up":leveled}
        if self.player.day > self.high["best_day"]: self.high["best_day"] = self.player.day
        if profit > self.high["best_profit"]: self.high["best_profit"] = profit
        if self.player.rating > self.high["best_rating"]: self.high["best_rating"] = self.player.rating
        if self.player.level > self.high["best_level"]: self.high["best_level"] = self.player.level
        if self.player.level > self.high.get("unlocked_level", 0):
            self.high["unlocked_level"] = self.player.level
        if self.player.money >= CFG.DEBT_GOAL: self.game_won = True
        self.audio.play("dayend")
        self.state = "END_OF_DAY"

    def interact(self):
        pr = self.player.rect
        for c in self.customers:
            if c.kind == CKind.THIEF and c.sus():
                if pr.colliderect(c.rect.inflate(60,60)):
                    c.state = CState.BUST; c.wait = 1.0
                    bounty = c.bval() * CFG.THIEF_BOUNTY
                    self.player.earn(bounty); self.player.caught += 1
                    self.player.rating = min(5.0, self.player.rating + 0.15)
                    self.floats.append(FloatText(c.rect.centerx, c.rect.y-20,
                        f"BUSTED! +${bounty:.0f}", C.YELLOW, big=True))
                    for _ in range(pcount(20)):
                        self.particles.append(Particle(c.rect.centerx, c.rect.centery,
                            (255,215,0), "coin"))
                    self.audio.play("busted"); self.shake.add(8)
                    self.show(f"BUSTED! +${bounty:.0f}",2.5)
                    return
        dr = math.hypot(pr.centerx-REGISTER.centerx, pr.centery-REGISTER.centery)
        if dr < 90 and self.queue:
            c = self.queue[0]
            if c.state == CState.PAY and c.basket:
                k = c.basket.pop(0); p = prod(k)
                if p:
                    self.player.earn(p["price"])
                    self.floats.append(FloatText(REGISTER.centerx, REGISTER.y-10,
                        f"+${p['price']:.2f}", C.GREEN, big=True))
                    for _ in range(pcount(8)):
                        self.particles.append(Particle(REGISTER.centerx, REGISTER.centery,
                            (100,220,100), "coin"))
                    self.audio.play("scan")
                    self.scan_anim = 12; self.scan_pos = REGISTER.center
                    self.shake.add(2.5)
                    if not c.basket:
                        self.player.served += 1; self.player.tserved += 1
                        self.player.rating = min(5.0, self.player.rating + 0.03)
                        self.floats.append(FloatText(c.rect.centerx, c.rect.y-20,
                            "PAID!", C.YELLOW, big=True))
                        self.audio.play("ching"); self.shake.add(4)
                return
        for s in self.shelves:
            if math.hypot(pr.centerx-s.rect.centerx, pr.centery-s.rect.centery) < CFG.RADIUS:
                pk = s.key; p = prod(pk)
                if self.player.back[pk] > 0 and s.stock < s.max:
                    a = min(s.max-s.stock, self.player.back[pk], 10)
                    s.restock(a); self.player.back[pk] -= a
                    self.show(f"Restocked {a}x {p['name']}")
                    self.floats.append(FloatText(s.rect.centerx, s.rect.y-10, f"+{a}", C.GREEN))
                    for _ in range(pcount(6)):
                        self.particles.append(Particle(s.rect.centerx, s.rect.centery,
                            (200,255,200)))
                    self.audio.play("restock")
                elif self.player.back[pk] == 0:
                    self.show(f"No {p['name']}"); self.audio.play("error")
                else:
                    self.show("Shelf full"); self.audio.play("error")
                return
        if pr.colliderect(PC_RECT.inflate(80,80)):
            self.audio.play("click"); self.state = "SUPPLIER"; return
        self.show("Go near register / shelf / PC")

    def order(self, i):
        u = self.player.unlocked()
        if i >= len(u): return
        p = u[i]; c = p["cost"]*10
        if self.player.spend(c):
            self.player.back[p["key"]] += 10
            self.show(f"Ordered 10x {p['name']}")
            self.audio.play("order")
        else:
            self.show("No money!"); self.audio.play("error")

    def hire(self, k):
        lv = self.player.lv()
        if len(self.employees) >= lv["max_emp"]:
            self.show(f"Max {lv['max_emp']} employees!")
            self.audio.play("error"); return
        c = {"CASHIER":lv["c_cost"],"STOCKER":lv["s_cost"],
             "GUARD":int(lv["c_cost"]*0.7),"CLEANER":int(lv["s_cost"]*0.5)}[k.name]
        if not self.player.spend(c):
            self.show("No money!"); self.audio.play("error"); return
        self.employees.append(Employee(k))
        self.show(f"Hired {EINFO[k]['name']}!")
        self.audio.play("hire")

    def next_day(self):
        self.player.day += 1
        self.player.day_time = 0.0
        self.player.served = 0; self.player.lost = 0
        self.player.de = 0.0; self.player.ds = 0.0
        self.customers.clear(); self.queue.clear()
        self.floats.clear(); self.particles.clear(); self.events.clear()
        self.ev_cd = 30.0
        self.player.rect.center = (int(CFG.SW*0.82), int(CFG.SH*0.9))
        self.audio.play("daystart")
        self.state = "PLAY"
        

# ============================================================
# RENDERER
# ============================================================
class Renderer:
    def __init__(self, screen):
        self.scr = screen
        self.f_tiny = mk_font(max(10, int(12*SCALE)))
        self.f_sm = mk_font(max(11, int(14*SCALE)))
        self.f_md = mk_font(max(12, int(16*SCALE)), True)
        self.f_b = mk_font(max(13, int(18*SCALE)), True)
        self.f_l = mk_font(max(16, int(24*SCALE)), True)
        self.f_xl = mk_font(max(22, int(34*SCALE)), True)
        self.f_xxl = mk_font(max(32, int(54*SCALE)), True)
        self.menu_anim = 0.0
        self.menu_buttons = []
        self.pause_buttons = []
        self.settings_buttons = []
        self.end_buttons = []
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        cx = CFG.SW // 2
        F = self.f_b
        bw, bh = int(320*SCALE), int(56*SCALE)
        self.menu_buttons = [
            Button((cx-bw//2, int(400*SCALE), bw, bh), "new_game",
                   lambda: self._act("new_game"), font=F),
            Button((cx-bw//2, int(468*SCALE), bw, bh), "load_save",
                   lambda: self._act("load"), accent=C.BLUE, bg=(30,60,120), font=F),
            Button((cx-bw//2, int(536*SCALE), bw, bh), "settings",
                   lambda: self._act("settings"), accent=C.PURPLE, bg=(70,40,110), font=F),
            Button((cx-bw//2, int(604*SCALE), bw, bh), "quit",
                   lambda: self._act("quit"), accent=C.RED, bg=(100,35,40), font=F),
        ]
        pbx = cx - int(260*SCALE)
        pw, ph = int(452*SCALE), int(56*SCALE)
        self.pause_buttons = [
            Button((pbx+int(34*SCALE), int(240*SCALE), pw, ph), "resume",
                   lambda: self._act("resume"), font=F),
            Button((pbx+int(34*SCALE), int(304*SCALE), pw, ph), "save_game",
                   lambda: self._act("save"), accent=C.CYAN, bg=(30,80,90), font=F),
            Button((pbx+int(34*SCALE), int(368*SCALE), pw, ph), "settings",
                   lambda: self._act("settings"), accent=C.PURPLE, bg=(70,40,110), font=F),
            Button((pbx+int(34*SCALE), int(432*SCALE), pw, ph), "main_menu",
                   lambda: self._act("menu"), accent=C.ORANGE, bg=(90,60,30), font=F),
            Button((pbx+int(34*SCALE), int(496*SCALE), pw, ph), "quit",
                   lambda: self._act("quit"), accent=C.RED, bg=(100,35,40), font=F),
        ]
        sbx = cx - int(300*SCALE)
        sw2, sh2 = int(540*SCALE), int(64*SCALE)
        self.settings_buttons = [
            Button((sbx+int(30*SCALE), int(300*SCALE), sw2, sh2), "language",
                   lambda: self._act("toggle_lang"), accent=C.CYAN, bg=(30,70,90), font=F),
            Button((sbx+int(30*SCALE), int(380*SCALE), sw2, sh2), "fullscreen",
                   lambda: self._act("toggle_fs"), accent=C.GREEN, bg=(30,80,55), font=F),
            Button((sbx+int(30*SCALE), int(500*SCALE), sw2, int(60*SCALE)), "back",
                   lambda: self._act("settings_back"), accent=C.ORANGE, bg=(90,60,30), font=F),
        ]
        self.end_buttons = [
            Button((cx-int(170*SCALE), CFG.SH-int(130*SCALE),
                    int(340*SCALE), int(56*SCALE)), "next_day",
                   lambda: self._act("next_day"), accent=C.YELLOW, bg=(80,70,20), font=F),
        ]

    def _act(self, name):
        if self._action_cb: self._action_cb(name)
    _action_cb = None

    def draw(self, gs):
        if gs.state == "MENU": self._menu(gs); return
        if gs.state == "INTRO": self._intro(gs); return
        if gs.state == "SETTINGS": self._settings(gs); return
        ox, oy = gs.shake.off()
        self.scr.fill(C.DARK)
        self._floor(gs, ox, oy)
        self._walls(gs, ox, oy)
        self._storage(gs, ox, oy)
        for s in gs.shelves: self._shelf(gs, s, ox, oy)
        self._counter(gs, ox, oy)
        ents = []
        for c in gs.customers: ents.append(("c", c.rect.bottom, c))
        for e in gs.employees: ents.append(("e", e.rect.bottom, e))
        ents.append(("p", gs.player.rect.bottom, None))
        ents.sort(key=lambda x: x[1])
        for k, _, o in ents:
            if k == "c": self._customer(o, ox, oy)
            elif k == "e": self._employee(o, ox, oy)
            else: self._player(gs.player, ox, oy)
        for p in gs.particles: p.draw(self.scr, ox, oy)
        for f in gs.floats: f.draw(self.scr, self.f_l, self.f_b, ox, oy)
        lv = gs.player.lv()
        prog = gs.player.day_time / lv["day_len"]
        if CFG.ENABLE_TINT:
            r, g, b, a = time_tint(prog)
            if a > 0:
                ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
                ov.fill((r,g,b,a)); self.scr.blit(ov, (0,0))
        if any(e.kind == "outage" for e in gs.events):
            ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
            ov.fill((20,10,40,60)); self.scr.blit(ov, (0,0))
        self._hud(gs)
        self._backroom(gs)
        if gs.msg_t > 0 and gs.msg: self._msg(gs.msg)
        if gs.lvl_flash > 0:
            frac = gs.lvl_flash / CFG.LEVEL_MSG_SEC
            self._lvl_flash(int(140*frac), 1-frac)
        if gs.state == "PLAY" and gs.tutorial < 6: self._tutorial(gs)
        if gs.state == "PAUSE": self._pause(gs)
        if gs.state == "SUPPLIER": self._supplier(gs)
        if gs.state == "HIRE": self._hire(gs)
        if gs.state == "END_OF_DAY": self._end_day(gs)

    def _floor(self, gs, ox, oy):
        lv = gs.player.lv(); fc = lv["fc"]
        fc2 = tuple(max(0,c-12) for c in fc); fl = tuple(max(0,c-22) for c in fc)
        inner = pygame.Rect(CFG.WALL_T, CFG.HUD_H+CFG.WALL_T,
            CFG.SW-2*CFG.WALL_T, CFG.SH-CFG.HUD_H-2*CFG.WALL_T)
        sr = STORE_RECT.move(ox, oy)
        pygame.draw.rect(self.scr, C.STORAGE_FLOOR, sr)
        tile = 60
        for y in range(inner.y, inner.bottom, tile):
            for x in range(inner.x, inner.right, tile):
                r = pygame.Rect(x+ox, y+oy, tile, tile)
                if r.colliderect(sr): continue
                c = fc if ((x//tile)+(y//tile))%2 == 0 else fc2
                pygame.draw.rect(self.scr, c, r)
        for y in range(inner.y, inner.bottom, tile):
            pygame.draw.line(self.scr, fl, (inner.x+ox, y+oy), (inner.right+ox, y+oy), 1)
        for x in range(inner.x, inner.right, tile):
            pygame.draw.line(self.scr, fl, (x+ox, inner.y+oy), (x+ox, inner.bottom+oy), 1)

    def _walls(self, gs, ox, oy):
        wc = gs.player.lv()["wc"]
        wl = tuple(min(255,c+30) for c in wc)
        wd = tuple(max(0,c-27) for c in wc)
        W,H,T,HH = CFG.SW,CFG.SH,CFG.WALL_T,CFG.HUD_H
        pygame.draw.rect(self.scr, wc, (ox, HH+oy, W, T))
        pygame.draw.rect(self.scr, wl, (ox, HH+oy, W, 3))
        pygame.draw.rect(self.scr, wd, (ox, HH+T-3+oy, W, 3))
        pygame.draw.rect(self.scr, wc, (ox, HH+oy, T, H-HH))
        pygame.draw.rect(self.scr, wl, (ox, HH+oy, 3, H-HH))
        pygame.draw.rect(self.scr, wc, (W-T+ox, HH+oy, T, H-HH))
        pygame.draw.rect(self.scr, wl, (W-3+ox, HH+oy, 3, H-HH))
        pygame.draw.rect(self.scr, wc, (ox, H-T+oy, ENTRANCE.x, T))
        pygame.draw.rect(self.scr, wc, (ENTRANCE.right+ox, H-T+oy, W-ENTRANCE.right, T))
        mat = pygame.Rect(ENTRANCE.x+20+ox, H-T-8+oy, ENTRANCE.w-40, 6)
        pygame.draw.rect(self.scr, C.GREEN, mat, border_radius=3)
        pygame.draw.rect(self.scr, wc, STORE_WALL.move(ox, oy))
        pygame.draw.rect(self.scr, wl, (STORE_WALL.x+ox, STORE_WALL.y+oy, 3, STORE_WALL.h))
        pygame.draw.rect(self.scr, (200,170,120), STORE_DOOR.move(ox, oy))
        pygame.draw.rect(self.scr, C.YELLOW, STORE_DOOR.move(ox, oy), 2)

    def _storage(self, gs, ox, oy):
        t = self.f_b.render("STORAGE", True, (90,70,40))
        self.scr.blit(t, (STORE_RECT.centerx-t.get_width()//2+ox, STORE_RECT.y+6+oy))
        for i in range(3):
            bx = STORE_RECT.x+20+i*62+ox; by = STORE_RECT.y+150+oy
            pygame.draw.rect(self.scr, (180,130,80), (bx,by,52,42), border_radius=3)
            pygame.draw.rect(self.scr, (140,95,55), (bx,by,52,42), 2, border_radius=3)
        pr = PC_RECT.move(ox, oy)
        pygame.draw.rect(self.scr, (60,60,70), pr, border_radius=4)
        inner = pygame.Rect(pr.x+6, pr.y+6, pr.w-12, pr.h-20)
        pygame.draw.rect(self.scr, (80,180,220), inner, border_radius=3)
        pygame.draw.rect(self.scr, (40,40,50), pr, 2, border_radius=4)
        d = math.hypot(gs.player.rect.centerx-PC_RECT.centerx, gs.player.rect.centery-PC_RECT.centery)
        if d < 90: self._hint(pr.centerx, pr.y-23, "[E] Open Supplier", C.YELLOW)

    def _shelf(self, gs, s, ox, oy):
        r = s.rect.move(ox, oy); p = s.product
        sh = pygame.Surface((r.w+8, r.h+8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,60), (4,4,r.w,r.h), border_radius=8)
        self.scr.blit(sh, (r.x-4, r.y-4))
        pygame.draw.rect(self.scr, C.SHELF_WOOD, r, border_radius=6)
        pygame.draw.rect(self.scr, C.SHELF_WOOD_L, (r.x,r.y,r.w,6),
            border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(self.scr, C.SHELF_WOOD_D, (r.x,r.bottom-6,r.w,6),
            border_bottom_left_radius=6, border_bottom_right_radius=6)
        lr = pygame.Rect(r.x+4, r.y+8, r.w-8, 18)
        pygame.draw.rect(self.scr, (250,245,230), lr, border_radius=3)
        pygame.draw.rect(self.scr, p["color"], (lr.x+2, lr.y+2, 14, 14), border_radius=2)
        pygame.draw.rect(self.scr, C.BLACK, (lr.x+2, lr.y+2, 14, 14), 1, border_radius=2)
        lt = self.f_tiny.render(f"{p['name']} ${p['price']:.2f}", True, C.BLACK)
        self.scr.blit(lt, (lr.x+20, lr.y+3))
        sa = pygame.Rect(r.x+6, r.y+30, r.w-12, r.h-38)
        c2, r2 = 6, 2; sw = sa.w//c2; sh2 = sa.h//r2
        for i in range(min(s.stock, c2*r2)):
            rr = i//c2; cc = i%c2
            px = sa.x+cc*sw+2; py = sa.y+rr*sh2+2
            pygame.draw.rect(self.scr, p["color"], (px,py,sw-4,sh2-4), border_radius=2)
            pygame.draw.rect(self.scr, (60,40,20), (px,py,sw-4,sh2-4), 1, border_radius=2)
        if s.stock == 0:
            t = self.f_sm.render("EMPTY", True, (200,60,60))
            self.scr.blit(t, (r.centerx-t.get_width()//2, r.centery-t.get_height()//2+5))
        d = math.hypot(gs.player.rect.centerx-s.rect.centerx, gs.player.rect.centery-s.rect.centery)
        if d < CFG.RADIUS:
            h = None
            if gs.player.back[s.key] > 0 and s.stock < s.max: h = "[E] Restock"
            elif gs.player.back[s.key] == 0 and s.stock < s.max: h = "Order at PC"
            if h: self._hint(r.centerx, r.y-23, h, C.YELLOW)

    def _counter(self, gs, ox, oy):
        r = COUNTER.move(ox, oy)
        sh = pygame.Surface((r.w+10, r.h+10), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,70), (5,5,r.w,r.h), border_radius=10)
        self.scr.blit(sh, (r.x-5, r.y-5))
        pygame.draw.rect(self.scr, C.COUNTER_C, r, border_radius=8)
        pygame.draw.rect(self.scr, C.COUNTER_L, (r.x,r.y,r.w,12),
            border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.rect(self.scr, C.COUNTER_D, (r.x,r.bottom-8,r.w,8),
            border_bottom_left_radius=8, border_bottom_right_radius=8)
        reg = REGISTER.move(ox, oy)
        pygame.draw.rect(self.scr, (60,60,70), reg, border_radius=4)
        inner = pygame.Rect(reg.x+4, reg.y+4, reg.w-8, reg.h-12)
        pygame.draw.rect(self.scr, (100,200,230), inner, border_radius=2)
        d = math.hypot(gs.player.rect.centerx-REGISTER.centerx, gs.player.rect.centery-REGISTER.centery)
        if d < 90 and gs.queue:
            self._hint(reg.centerx, reg.y-31, "[E] Scan", C.YELLOW)
        if gs.scan_anim > 0:
            a = min(255, int(gs.scan_anim*30))
            s = pygame.Surface((200,200), pygame.SRCALPHA)
            pygame.draw.line(s, (100,255,150,a), (0,0), (200,200), 3)
            pygame.draw.line(s, (100,255,150,a), (200,0), (0,200), 3)
            self.scr.blit(s, (gs.scan_pos[0]-100+ox, gs.scan_pos[1]-100+oy))

    def _player(self, p, ox, oy):
        r = p.rect.move(ox, oy); cx, cy = r.centerx, r.centery
        spr = SPRITES.get("player")
        if spr:
            pulse = 12 + int(6*math.sin(pygame.time.get_ticks()*0.005))
            glow_circle(self.scr, cx, cy, r.w//2 + pulse//2, (100,200,255), alpha=90)
            sh = pygame.Surface((r.w+12, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0,0,0,120), sh.get_rect())
            self.scr.blit(sh, (r.x-6, r.bottom-5))
            self.scr.blit(spr, (cx - spr.get_width()//2, cy - spr.get_height()//2))
            ay = r.y - 22
            pts = [(cx, ay-12), (cx-8, ay-1), (cx+8, ay-1)]
            pygame.draw.polygon(self.scr, C.LOGO_YELLOW, pts)
            pygame.draw.polygon(self.scr, C.LOGO_OUTLINE, pts, 2)
            return
        pulse = 12 + int(6*math.sin(pygame.time.get_ticks()*0.005))
        glow_circle(self.scr, cx, cy, r.w//2 + pulse//2, (100,200,255), alpha=90)
        ay = r.y-24
        pts = [(cx, ay-14), (cx-9, ay-2), (cx+9, ay-2)]
        pygame.draw.polygon(self.scr, C.LOGO_YELLOW, pts)
        pygame.draw.polygon(self.scr, C.LOGO_OUTLINE, pts, 2)
        sh = pygame.Surface((r.w+12, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,120), sh.get_rect())
        self.scr.blit(sh, (r.x-6, r.bottom-5))
        body_big = pygame.Surface((r.w*4, r.h*4), pygame.SRCALPHA)
        pygame.draw.rect(body_big, C.LOGO_YELLOW, body_big.get_rect(), border_radius=10*4)
        pygame.draw.rect(body_big, C.LOGO_GREEN, (0, r.h*4-11*4, r.w*4, 11*4), border_radius=6*4)
        pygame.draw.rect(body_big, C.LOGO_OUTLINE, body_big.get_rect(), 3*4, border_radius=10*4)
        body = pygame.transform.smoothscale(body_big, (r.w, r.h))
        self.scr.blit(body, r.topleft)
        head = smooth_circle((255, 235, 200), 10)
        self.scr.blit(head, (cx-10, r.y-16))
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (cx, r.y-16), 10, 3)
        cap_big = pygame.Surface((22*4, 12*4), pygame.SRCALPHA)
        pygame.draw.ellipse(cap_big, C.LOGO_GREEN, (0, 0, 22*4, 10*4))
        pygame.draw.ellipse(cap_big, C.LOGO_OUTLINE, (0, 0, 22*4, 10*4), 2*4)
        pygame.draw.rect(cap_big, C.LOGO_GREEN, (0, 5*4, 22*4, 5*4),
                         border_bottom_left_radius=3*4, border_bottom_right_radius=3*4)
        cap = pygame.transform.smoothscale(cap_big, (22, 12))
        self.scr.blit(cap, (cx-11, r.y-24))
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (cx-4, r.y-15), 2)
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (cx+4, r.y-15), 2)
        pygame.draw.arc(self.scr, C.LOGO_OUTLINE, (cx-5, r.y-12, 10, 6), 3.14, 0, 2)

    def _customer(self, c, ox, oy):
        r = c.rect.move(ox, oy); cx = r.right-4; cy = r.bottom-4
        cw, ch = 24, 14
        sprite_idx = (hash(id(c)) % 6) + 1
        spr = SPRITES.get(f"customer_{sprite_idx}")
        if spr:
            ccx, ccy = r.centerx, r.centery
            pygame.draw.ellipse(self.scr, (0,0,0,70), (cx-2, cy+ch+1, cw+4, 4))
            pygame.draw.rect(self.scr, C.LOGO_YELLOW, (cx, cy, cw, ch), border_radius=4)
            pygame.draw.rect(self.scr, C.LOGO_GREEN, (cx+cw-3, cy-4, 5, ch+6), border_radius=3)
            pygame.draw.rect(self.scr, C.LOGO_OUTLINE, (cx+cw-3, cy-4, 5, ch+6), 2, border_radius=3)
            pygame.draw.rect(self.scr, C.LOGO_OUTLINE, (cx, cy, cw, ch), 2, border_radius=4)
            for wx in (cx+6, cx+cw-6):
                pygame.draw.circle(self.scr, C.LOGO_YELLOW, (wx, cy+ch+2), 4)
                pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (wx, cy+ch+2), 4, 2)
                pygame.draw.circle(self.scr, C.LOGO_GREEN, (wx, cy+ch+2), 1)
            n = len(c.basket)
            for i in range(min(n, 4)):
                p = prod(c.basket[i])
                if p:
                    pygame.draw.circle(self.scr, p["color"], (cx+6+i*5, cy+4), 3)
                    pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (cx+6+i*5, cy+4), 3, 1)
            sh = pygame.Surface((r.w+8, 7), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0,0,0,100), sh.get_rect())
            self.scr.blit(sh, (r.x-4, r.bottom-5))
            self.scr.blit(spr, (ccx - spr.get_width()//2, ccy - spr.get_height()//2))
            if c.kind == CKind.VIP:
                pygame.draw.circle(self.scr, C.LOGO_YELLOW, (ccx, r.y-30), 10)
                pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (ccx, r.y-30), 10, 2)
                t = self.f_sm.render("V", True, C.LOGO_OUTLINE)
                self.scr.blit(t, (ccx-t.get_width()//2, r.y-35))
            elif c.kind == CKind.THIEF and c.sus():
                pygame.draw.circle(self.scr, (240,90,95), (ccx, r.y-30), 10)
                pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (ccx, r.y-30), 10, 2)
                t = self.f_sm.render("!", True, C.WHITE)
                self.scr.blit(t, (ccx-t.get_width()//2, r.y-36))
            if c.state == CState.INQ:
                pct = max(0.0, 1.0-c.qw/c.patience)
                bw = r.w+8; bx = r.x-4; by = r.y-22
                pygame.draw.rect(self.scr, C.LOGO_OUTLINE, (bx-1,by-1,bw+2,7), border_radius=3)
                pygame.draw.rect(self.scr, (60,20,20), (bx,by,bw,5), border_radius=2)
                col = C.LOGO_GREEN if pct>0.5 else (C.LOGO_YELLOW if pct>0.25 else (240,90,95))
                pygame.draw.rect(self.scr, col, (bx,by,int(bw*pct),5), border_radius=2)
            if c.state == CState.PAY:
                pygame.draw.circle(self.scr, C.LOGO_YELLOW, (ccx, r.y-30), 8)
                pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (ccx, r.y-30), 8, 2)
                t = self.f_sm.render("!", True, C.LOGO_OUTLINE)
                self.scr.blit(t, (ccx-t.get_width()//2, r.y-36))
            return
        # Fallback drawing
        pygame.draw.ellipse(self.scr, (0,0,0,70), (cx-2, cy+ch+1, cw+4, 4))
        pygame.draw.rect(self.scr, C.LOGO_YELLOW, (cx, cy, cw, ch), border_radius=4)
        pygame.draw.rect(self.scr, C.LOGO_GREEN, (cx+cw-3, cy-4, 5, ch+6), border_radius=3)
        pygame.draw.rect(self.scr, C.LOGO_OUTLINE, (cx+cw-3, cy-4, 5, ch+6), 2, border_radius=3)
        pygame.draw.rect(self.scr, C.LOGO_OUTLINE, (cx, cy, cw, ch), 2, border_radius=4)
        for wx in (cx+6, cx+cw-6):
            pygame.draw.circle(self.scr, C.LOGO_YELLOW, (wx, cy+ch+2), 4)
            pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (wx, cy+ch+2), 4, 2)
            pygame.draw.circle(self.scr, C.LOGO_GREEN, (wx, cy+ch+2), 1)
        n = len(c.basket)
        for i in range(min(n, 4)):
            p = prod(c.basket[i])
            if p:
                pygame.draw.circle(self.scr, p["color"], (cx+6+i*5, cy+4), 3)
                pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (cx+6+i*5, cy+4), 3, 1)
        sh = pygame.Surface((r.w+8, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,100), sh.get_rect())
        self.scr.blit(sh, (r.x-4, r.bottom-5))
        body_big = pygame.Surface((r.w*4, r.h*4), pygame.SRCALPHA)
        pygame.draw.rect(body_big, c.shirt, body_big.get_rect(), border_radius=8*4)
        pygame.draw.rect(body_big, C.LOGO_OUTLINE, body_big.get_rect(), 2*4, border_radius=8*4)
        body = pygame.transform.smoothscale(body_big, (r.w, r.h))
        self.scr.blit(body, r.topleft)
        head = smooth_circle(c.skin, 9)
        self.scr.blit(head, (r.centerx-9, r.y-14))
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx, r.y-14), 9, 2)
        pygame.draw.arc(self.scr, c.hair, (r.centerx-9, r.y-14, 18, 18), 0, 3.14, 6)
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx-3, r.y-12), 2)
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx+3, r.y-12), 2)

    def _employee(self, e, ox, oy):
        r = e.rect.move(ox, oy)
        spr = SPRITES.get(e.kind.name.lower())
        if spr:
            ccx, ccy = r.centerx, r.centery
            sh = pygame.Surface((r.w+8, 7), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0,0,0,100), sh.get_rect())
            self.scr.blit(sh, (r.x-4, r.bottom-5))
            self.scr.blit(spr, (ccx - spr.get_width()//2, ccy - spr.get_height()//2))
            ly = r.y-30
            pygame.draw.circle(self.scr, e.color, (ccx, ly+5), 9)
            pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (ccx, ly+5), 9, 2)
            t = self.f_sm.render(e.label, True, C.WHITE)
            self.scr.blit(t, (ccx-t.get_width()//2, ly+5-t.get_height()//2))
            return
        sh = pygame.Surface((r.w+8, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,100), sh.get_rect())
        self.scr.blit(sh, (r.x-4, r.bottom-5))
        body_big = pygame.Surface((r.w*4, r.h*4), pygame.SRCALPHA)
        pygame.draw.rect(body_big, e.color, body_big.get_rect(), border_radius=8*4)
        pygame.draw.rect(body_big, C.LOGO_OUTLINE, body_big.get_rect(), 2*4, border_radius=8*4)
        body = pygame.transform.smoothscale(body_big, (r.w, r.h))
        self.scr.blit(body, r.topleft)
        head = smooth_circle((255, 235, 200), 9)
        self.scr.blit(head, (r.centerx-9, r.y-14))
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx, r.y-14), 9, 2)
        cap_big = pygame.Surface((20*4, 10*4), pygame.SRCALPHA)
        pygame.draw.ellipse(cap_big, C.LOGO_GREEN, (0, 0, 20*4, 9*4))
        pygame.draw.ellipse(cap_big, C.LOGO_OUTLINE, (0, 0, 20*4, 9*4), 2*4)
        cap = pygame.transform.smoothscale(cap_big, (20, 10))
        self.scr.blit(cap, (r.centerx-10, r.y-21))
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx-3, r.y-12), 2)
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx+3, r.y-12), 2)
        ly = r.y-30
        pygame.draw.circle(self.scr, e.color, (r.centerx, ly+5), 9)
        pygame.draw.circle(self.scr, C.LOGO_OUTLINE, (r.centerx, ly+5), 9, 2)
        t = self.f_sm.render(e.label, True, C.WHITE)
        self.scr.blit(t, (r.centerx-t.get_width()//2, ly+5-t.get_height()//2))

    def _hint(self, cx, y, text, color):
        t = render_ar(self.f_sm, text, color)
        bg = pygame.Surface((t.get_width()+14, t.get_height()+8), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0,0,0,200), bg.get_rect(), border_radius=6)
        self.scr.blit(bg, (cx-t.get_width()//2-7, y-4))
        self.scr.blit(t, (cx-t.get_width()//2, y))

    def _msg(self, text):
        m = render_ar(self.f_b, text, C.WHITE)
        pad = 18
        box = pygame.Rect(CFG.SW//2-m.get_width()//2-pad, CFG.SH-72,
            m.get_width()+pad*2, m.get_height()+14)
        glass_panel(self.scr, box, radius=12)
        pygame.draw.rect(self.scr, C.YELLOW, box, 2, border_radius=12)
        self.scr.blit(m, (box.centerx-m.get_width()//2, box.centery-m.get_height()//2))

    def _hud(self, gs):
        p = gs.player; lv = p.lv()
        remain = max(0, lv["day_len"]-p.day_time)
        mm = int(remain//60); ss = int(remain%60)
        st = int(round(p.rating)); stx = "★"*st + "☆"*(5-st)
        prog = p.day_time/lv["day_len"]
        gradient_rect(self.scr, HUD_RECT, (18,22,34), (28,34,52), radius=0)
        pygame.draw.rect(self.scr, (40,45,60), (0, CFG.HUD_H-4, CFG.SW, 4))
        bar = pygame.Rect(0, CFG.HUD_H-4, int(CFG.SW*prog), 4)
        gradient_rect(self.scr, bar, (100,220,140), (60,180,110))
        lv_col = (C.CYAN,C.GREEN,C.YELLOW,C.ORANGE,C.RED,C.PURPLE,C.BLUE,C.WHITE)[p.level]
        # Responsive badges (scaled)
        badges = [
            (sx(8), sx(10), sx(120), f"{tr('day')} {p.day}", C.YELLOW),
            (sx(136), sx(10), sx(130), f"{mm:02d}:{ss:02d}", C.WHITE),
            (sx(274), sx(10), sx(160), f"${p.money:.2f}", C.GREEN),
            (sx(442), sx(10), sx(170), f"${p.earned:.0f}", C.CYAN),
            (sx(620), sx(10), sx(130), f"{tr('served')} {p.served}", C.WHITE),
            (sx(758), sx(10), sx(115), f"{tr('queue')} {len(gs.queue)}", C.ORANGE),
            (sx(881), sx(10), sx(165), f"{stx} {p.rating:.1f}", C.YELLOW),
            (sx(1054), sx(10), sx(130), f"{tr('emp')} {len(gs.employees)}", C.ORANGE),
            (sx(1192), sx(10), sx(84), f"{tr('lv')} {p.level+1}", lv_col),
        ]
        for x, y, w, txt, col in badges:
            rr = pygame.Rect(x, y, w, sx(36))
            s = pygame.Surface((rr.w, rr.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (30,36,54,210), s.get_rect(), border_radius=9)
            self.scr.blit(s, rr.topleft)
            pygame.draw.rect(self.scr, (60,80,130), rr, 1, border_radius=9)
            t = render_ar(self.f_sm, txt, col)
            self.scr.blit(t, (rr.centerx-t.get_width()//2, rr.centery-t.get_height()//2))
        phase = phase_label(prog)
        info = render_ar(self.f_tiny,
            f"LV{p.level+1} {lv['name']} · {phase} · {tr('goal')}: ${CFG.DEBT_GOAL:,.0f}",
            phase_col(prog))
        self.scr.blit(info, (sx(8), CFG.HUD_H-22))
        # Quality indicator
        qname = "POTATO" if QUALITY == 0 else "NORMAL" if QUALITY == 1 else "NASA"
        q_col = C.ORANGE if QUALITY == 0 else (C.GREEN if QUALITY == 1 else C.CYAN)
        qt = render_ar(self.f_tiny, f"[{qname}]", q_col)
        self.scr.blit(qt, (CFG.SW - qt.get_width() - sx(8), CFG.HUD_H-22))
        y_off = 52
        for ev in gs.events:
            lbl = {"rush":"RUSH!","vip":"VIP","delivery":"DELIVERY","outage":"OUTAGE"}.get(ev.kind, ev.kind)
            col = {"rush":C.RED,"vip":C.YELLOW,"delivery":C.GREEN,"outage":C.ORANGE}.get(ev.kind, C.CYAN)
            t = render_ar(self.f_sm, f"{lbl} ({int(ev.tl)}s)", col)
            box = pygame.Rect(CFG.SW//2-t.get_width()//2-12, y_off, t.get_width()+24, 24)
            s = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (15,18,28,220), s.get_rect(), border_radius=8)
            self.scr.blit(s, box.topleft)
            pygame.draw.rect(self.scr, col, box, 2, border_radius=8)
            self.scr.blit(t, (box.centerx-t.get_width()//2, box.centery-t.get_height()//2))
            y_off += 28

    def _backroom(self, gs):
        r = pygame.Rect(CFG.SW-sx(240), CFG.HUD_H+10, sx(226), sx(178))
        glass_panel(self.scr, r, radius=12, bg=(15,20,32,220), border=(80,200,220,180))
        t = self.f_sm.render("BACKROOM", True, C.CYAN)
        self.scr.blit(t, (r.x+14, r.y+8))
        u = gs.player.unlocked()
        for i, pr in enumerate(u[:8]):
            row2 = i%4; col2 = i//4
            x = r.x+14+col2*sx(108); y = r.y+34+row2*sx(32)
            pygame.draw.rect(self.scr, pr["color"], (x,y+2,10,10), border_radius=2)
            self.scr.blit(self.f_tiny.render(pr["name"], True, C.WHITE), (x+14, y))
            amt = gs.player.back[pr["key"]]
            ac = C.GREEN if amt>5 else (C.YELLOW if amt>0 else C.RED)
            self.scr.blit(self.f_tiny.render(f"x{amt}", True, ac), (x+14, y+12))

    # --------------------------------------------------------
    # MENU (with progressive level unlocking)
    # --------------------------------------------------------
    def _menu(self, gs):
        self.menu_anim += 0.015
        draw_modern_bg(self.scr, self.menu_anim)

        card = pygame.Rect(CFG.SW//2-sx(460), sx(25), sx(920), sx(690))
        glass_panel(self.scr, card, radius=28,
                    bg=(16,20,36,235), border=(90,150,230,200))

        # ---- LOGO ----
        logo_bottom = card.y + sx(50)
        if LOGO:
            max_h = sx(170)
            lw = sx(200)
            lh = int(LOGO.get_height() * lw / LOGO.get_width())
            if lh > max_h:
                lh = max_h
                lw = int(LOGO.get_width() * lh / LOGO.get_height())
            logo = pygame.transform.smoothscale(LOGO, (lw, lh))
            lx = card.centerx - lw//2
            bob = int(math.sin(self.menu_anim*2) * 4)
            ly = card.y + sx(50) + bob
            for i in range(3):
                gl = pygame.transform.smoothscale(LOGO,
                                                  (lw+24+i*14, lh+24+i*14))
                gl.set_alpha(35 - i*12)
                self.scr.blit(gl, (lx-12-i*7, ly-12-i*7))
            self.scr.blit(logo, (lx, ly))
            logo_bottom = ly + lh

        # ---- TITLE ----
        title_y = logo_bottom + sx(18)
        t1 = render_ar(self.f_xxl, tr("title1"), C.LOGO_YELLOW)
        t2 = render_ar(self.f_l, tr("title2"), C.LOGO_GREEN)
        total_w = t1.get_width() + 14 + t2.get_width()
        tx = card.centerx - total_w//2
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xxl, tr("title1"), C.LOGO_YELLOW_D)
            g.set_alpha(60)
            self.scr.blit(g, (tx+dx, title_y+dy))
        self.scr.blit(t1, (tx, title_y))
        self.scr.blit(t2, (tx + t1.get_width() + 14, title_y + sx(14)))

        # ---- SUBTITLE ----
        sub_y = title_y + t1.get_height() + sx(10)
        sub = render_ar(self.f_md, tr("subtitle"), (170,185,210))
        self.scr.blit(sub, (card.centerx-sub.get_width()//2, sub_y))

        # ---- BUTTONS ----
        for b in self.menu_buttons:
            b.draw(self.scr, render_ar)

        # ---- PROGRESSION STRIP (progressive unlock) ----
        self._draw_progression_strip(gs)

        # ---- Quality info at bottom ----
        qname = "POTATO" if QUALITY == 0 else "NORMAL" if QUALITY == 1 else "NASA"
        q_col = C.ORANGE if QUALITY == 0 else (C.GREEN if QUALITY == 1 else C.CYAN)
        qt = render_ar(self.f_sm, f"Device: {qname}", q_col)
        self.scr.blit(qt, (card.centerx-qt.get_width()//2, card.bottom + sx(6)))

    def _draw_progression_strip(self, gs):
        """Progressive level strip — locked levels show a lock icon."""
        strip = pygame.Rect(CFG.SW//2-sx(500), CFG.SH-sx(50), sx(1000), sx(40))
        glass_panel(self.scr, strip, radius=12)

        t = render_ar(self.f_tiny, tr("progression"), C.GRAY)
        self.scr.blit(t, (strip.x+sx(14), strip.y+sx(4)))

        unlocked = gs.high.get("unlocked_level", 0)
        n_levels = len(LEVELS)
        # Fit all levels in the strip width
        inner_w = strip.w - sx(120)
        cell_w = inner_w // n_levels
        start_x = strip.x + sx(110)

        for i, lv in enumerate(LEVELS):
            cell_x = start_x + i * cell_w
            is_unlocked = (i <= unlocked)
            is_current = (i == unlocked)
            is_locked = (i > unlocked)

            if is_unlocked:
                # Colored gradient for unlocked levels
                col = (C.GRAY, C.CYAN, C.GREEN, C.YELLOW, C.ORANGE,
                       C.RED, C.PURPLE, C.WHITE)[i]
            else:
                col = (70, 75, 90)

            # Background cell
            cell = pygame.Rect(cell_x, strip.y+sx(12), cell_w-sx(6), sx(16))
            pygame.draw.rect(self.scr, col, cell, border_radius=5)

            # Cell content
            if is_unlocked:
                txt = f"{i+1}: {lv['name'][:7]}"
                ic_col = C.BLACK
                ln = self.f_tiny.render(txt, True, ic_col)
                self.scr.blit(ln, (cell.x + (cell.w - ln.get_width())//2,
                                   cell.y + (cell.h - ln.get_height())//2))
            else:
                # Locked — draw lock icon
                lock_cx = cell.centerx
                lock_cy = cell.centery
                # Lock body
                body_r = pygame.Rect(lock_cx-5, lock_cy-1, 10, 8)
                pygame.draw.rect(self.scr, (180,180,200), body_r,
                                 border_radius=2)
                # Lock shackle (arc)
                pygame.draw.arc(self.scr, (180,180,200),
                                (lock_cx-5, lock_cy-7, 10, 10),
                                0, 3.14, 2)
                # "?" on the lock
                q = self.f_tiny.render(str(i+1), True, (60,60,75))
                self.scr.blit(q, (lock_cx-q.get_width()//2,
                                  lock_cy+1))

            # Current level highlight
            if is_current:
                pygame.draw.rect(self.scr, C.WHITE, cell, 2, border_radius=5)
                # Small pulse
                pulse_a = int(120 + 80*math.sin(self.menu_anim*4))
                glow = pygame.Surface((cell.w+10, cell.h+10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255,255,255,pulse_a//4),
                                 glow.get_rect(), border_radius=8)
                self.scr.blit(glow, (cell.x-5, cell.y-5))

    # --- INTRO ---
    def _intro(self, gs):
        self.scr.fill((10,12,20))
        for i in range(20):
            r = int(400 - i*18)
            if r <= 0: break
            a = int(4 + i*2)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (40,60,110,a), (r,r), r)
            self.scr.blit(s, (CFG.SW//2-r, CFG.SH//2-r))
        if LOGO:
            lw = 120
            lh = int(LOGO.get_height() * lw / LOGO.get_width())
            logo = pygame.transform.smoothscale(LOGO, (lw, lh))
            self.scr.blit(logo, (CFG.SW//2 - lw//2, 40))
        story = get_story()
        idx = gs.intro_idx
        if idx >= len(story): return
        title, body = story[idx]
        fade = min(1.0, gs.intro_t/0.8)
        a = int(255*fade)
        box = pygame.Rect(CFG.SW//2-sx(460), CFG.SH//2-sx(190),
                          sx(920), sx(380))
        soft_shadow(self.scr, box, 26, spread=20, alpha=150)
        s = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (18,24,42,235), s.get_rect(), border_radius=26)
        self.scr.blit(s, box.topleft)
        pygame.draw.rect(self.scr, (90,150,230), box, 2, border_radius=26)
        acc = pygame.Rect(box.x+30, box.y+14, box.w-60, 3)
        gradient_rect(self.scr, acc, (100,180,255), (60,120,220), radius=2)
        tt = render_ar(self.f_xxl, title, (255,225,130))
        tt.set_alpha(a)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xxl, title, (255,180,60))
            g.set_alpha(int(a*0.4))
            self.scr.blit(g, (box.centerx-tt.get_width()//2+dx, box.y+56+dy))
        self.scr.blit(tt, (box.centerx-tt.get_width()//2, box.y+56))
        for i, line in enumerate(body.split("\n")):
            lt = render_ar(self.f_l, line, C.WHITE)
            lt.set_alpha(a)
            self.scr.blit(lt, (box.centerx-lt.get_width()//2, box.y+150+i*40))
        for i in range(len(story)):
            cx = box.centerx - (len(story)-1)*18//2 + i*18
            if i == idx: pygame.draw.circle(self.scr, C.YELLOW, (cx, box.bottom-40), 7)
            else: pygame.draw.circle(self.scr, C.GRAY, (cx, box.bottom-40), 4)
        pb = pygame.Rect(box.x+40, box.bottom-18, box.w-80, 4)
        pygame.draw.rect(self.scr, (40,48,70), pb, border_radius=2)
        fill = pygame.Rect(pb.x, pb.y, int(pb.w * (gs.intro_t/CFG.INTRO_SEC)), 4)
        gradient_rect(self.scr, fill, (140,220,255), (80,160,240), radius=2)
        hint = render_ar(self.f_sm,
            f"{tr('skip')}  ·  {int(CFG.INTRO_SEC-gs.intro_t)}s", (140,160,190))
        self.scr.blit(hint, (CFG.SW//2-hint.get_width()//2, CFG.SH-40))

    # --- PAUSE ---
    def _pause(self, gs):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((0,0,0,200)); self.scr.blit(ov, (0,0))
        box = pygame.Rect(CFG.SW//2-sx(280), CFG.SH//2-sx(260), sx(560), sx(560))
        glass_panel(self.scr, box, radius=24, bg=(20,26,44,240), border=(140,120,220,220))
        t = render_ar(self.f_xl, tr("pause_title"), C.PURPLE)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xl, tr("pause_title"), (120,80,180))
            g.set_alpha(80)
            self.scr.blit(g, (box.centerx-t.get_width()//2+dx, box.y+34+dy))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+34))
        for b in self.pause_buttons: b.draw(self.scr, render_ar)
        t = render_ar(self.f_tiny, tr("mouse_hint"), (140,160,190))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.bottom-30))

    # --- SETTINGS ---
    def _settings(self, gs):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((0,0,0,210)); self.scr.blit(ov, (0,0))
        box = pygame.Rect(CFG.SW//2-sx(320), CFG.SH//2-sx(300), sx(640), sx(600))
        glass_panel(self.scr, box, radius=24, bg=(20,26,44,245), border=(140,200,240,220))
        t = render_ar(self.f_xl, tr("settings_title"), C.CYAN)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xl, tr("settings_title"), (40,140,180))
            g.set_alpha(80)
            self.scr.blit(g, (box.centerx-t.get_width()//2+dx, box.y+30+dy))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+30))

        # Language option
        lang_btn = self.settings_buttons[0]
        lang_btn.rect = pygame.Rect(box.x+30, box.y+sx(140), box.w-60, sx(64))
        lbl = render_ar(self.f_md, tr("language"), C.WHITE)
        self.scr.blit(lbl, (lang_btn.rect.x+10, lang_btn.rect.y-28))
        lang_val = "العربية" if SET.lang == "ar" else "English"
        lang_txt = f"{tr('language')}:  {lang_val}"
        soft_shadow(self.scr, lang_btn.rect, 14, 10, 90)
        s = pygame.Surface((lang_btn.rect.w, lang_btn.rect.h), pygame.SRCALPHA)
        bg = (30,70,90)
        if lang_btn.hovered: bg = tuple(min(255,c+20) for c in bg)
        pygame.draw.rect(s, bg, s.get_rect(), border_radius=14)
        self.scr.blit(s, lang_btn.rect.topleft)
        pygame.draw.rect(self.scr, C.CYAN, lang_btn.rect, 2, border_radius=14)
        t = render_ar(self.f_b, lang_txt, C.WHITE)
        self.scr.blit(t, (lang_btn.rect.centerx-t.get_width()//2,
                          lang_btn.rect.centery-t.get_height()//2))

        # Fullscreen option
        fs_btn = self.settings_buttons[1]
        fs_btn.rect = pygame.Rect(box.x+30, box.y+sx(240), box.w-60, sx(64))
        lbl = render_ar(self.f_md, tr("fullscreen"), C.WHITE)
        self.scr.blit(lbl, (fs_btn.rect.x+10, fs_btn.rect.y-28))
        fs_val = tr("on") if SET.fullscreen else tr("off")
        fs_txt = f"{tr('fullscreen')}:  {fs_val}"
        soft_shadow(self.scr, fs_btn.rect, 14, 10, 90)
        s = pygame.Surface((fs_btn.rect.w, fs_btn.rect.h), pygame.SRCALPHA)
        bg = (30,80,55)
        if fs_btn.hovered: bg = tuple(min(255,c+20) for c in bg)
        pygame.draw.rect(s, bg, s.get_rect(), border_radius=14)
        self.scr.blit(s, fs_btn.rect.topleft)
        pygame.draw.rect(self.scr, C.GREEN, fs_btn.rect, 2, border_radius=14)
        t = render_ar(self.f_b, fs_txt, C.WHITE)
        self.scr.blit(t, (fs_btn.rect.centerx-t.get_width()//2,
                          fs_btn.rect.centery-t.get_height()//2))

        # Back button
        back_btn = self.settings_buttons[2]
        back_btn.rect = pygame.Rect(box.x+30, box.bottom-90, box.w-60, 60)
        back_btn.draw(self.scr, render_ar)

        # Quality info
        qname = "POTATO" if QUALITY == 0 else "NORMAL" if QUALITY == 1 else "NASA"
        q_col = C.ORANGE if QUALITY == 0 else (C.GREEN if QUALITY == 1 else C.CYAN)
        qt = render_ar(self.f_tiny, f"Device: {qname}  ({', '.join(_DEVICE_INFO)})", q_col)
        self.scr.blit(qt, (box.centerx-qt.get_width()//2, box.y + sx(430)))

        # Hint
        t = render_ar(self.f_tiny, tr("mouse_hint"), (140,160,190))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.bottom-24))

    # --- SUPPLIER ---
    def _supplier(self, gs):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((0,0,0,210)); self.scr.blit(ov, (0,0))
        box = pygame.Rect(CFG.SW//2-sx(400), CFG.SH//2-sx(310), sx(800), sx(620))
        glass_panel(self.scr, box, radius=24, bg=(18,26,44,240), border=(90,220,140,220))
        t = render_ar(self.f_xl, tr("supplier_title"), C.GREEN)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xl, tr("supplier_title"), (40,160,90))
            g.set_alpha(80)
            self.scr.blit(g, (box.centerx-t.get_width()//2+dx, box.y+24+dy))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+24))
        u = gs.player.unlocked()
        for i, pr in enumerate(u):
            y = box.y+110+i*56
            row = pygame.Rect(box.x+34, y, box.w-68, 48)
            can = gs.player.afford(pr["cost"]*10)
            bg = (34,46,68) if can else (28,32,44)
            s = pygame.Surface((row.w, row.h), pygame.SRCALPHA)
            pygame.draw.rect(s, bg, s.get_rect(), border_radius=10)
            self.scr.blit(s, row.topleft)
            if can: pygame.draw.rect(self.scr, (90,160,120), row, 1, border_radius=10)
            pygame.draw.rect(self.scr, pr["color"], (row.x+12, row.y+10, 28, 28), border_radius=6)
            pygame.draw.rect(self.scr, C.BLACK, (row.x+12, row.y+10, 28, 28), 2, border_radius=6)
            col = C.WHITE if can else C.GRAY
            self.scr.blit(self.f_b.render(f"[{i+1}]  {pr['name']}", True, col),
                          (row.x+52, row.y+6))
            self.scr.blit(self.f_sm.render(f"10 x ${pr['cost']*10:.0f}", True, C.YELLOW),
                          (row.x+52, row.y+26))
        money = self.f_b.render(f"${gs.player.money:.2f}", True, C.YELLOW)
        self.scr.blit(money, (box.x+34, box.bottom-42))

    # --- HIRE ---
    def _hire(self, gs):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((0,0,0,210)); self.scr.blit(ov, (0,0))
        box = pygame.Rect(CFG.SW//2-sx(420), CFG.SH//2-sx(270), sx(840), sx(540))
        glass_panel(self.scr, box, radius=24, bg=(22,26,44,240), border=(255,165,80,220))
        t = render_ar(self.f_xl, tr("hire_title"), C.ORANGE)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xl, tr("hire_title"), (200,110,40))
            g.set_alpha(80)
            self.scr.blit(g, (box.centerx-t.get_width()//2+dx, box.y+24+dy))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+24))
        lv = gs.player.lv()
        options = [
            ("1", EKind.CASHIER, "Scans customers"),
            ("2", EKind.STOCKER, "Restocks shelves"),
            ("3", EKind.GUARD,   "Reduces lost customers"),
            ("4", EKind.CLEANER, "Boosts rating"),
        ]
        for i, (num, kind, desc) in enumerate(options):
            info = EINFO[kind]
            cost = {"CASHIER":lv["c_cost"],"STOCKER":lv["s_cost"],
                    "GUARD":int(lv["c_cost"]*0.7),"CLEANER":int(lv["s_cost"]*0.5)}[kind.name]
            y = box.y+110+i*90
            row = pygame.Rect(box.x+34, y, box.w-68, 78)
            can = gs.player.afford(cost) and len(gs.employees) < lv["max_emp"]
            bg = (34,46,68) if can else (28,32,44)
            s = pygame.Surface((row.w, row.h), pygame.SRCALPHA)
            pygame.draw.rect(s, bg, s.get_rect(), border_radius=12)
            self.scr.blit(s, row.topleft)
            if can: pygame.draw.rect(self.scr, (255,165,80), row, 1, border_radius=12)
            pygame.draw.rect(self.scr, info["color"], (row.x+14, row.y+14, 50, 50), border_radius=8)
            pygame.draw.rect(self.scr, C.BLACK, (row.x+14, row.y+14, 50, 50), 2, border_radius=8)
            tl = self.f_l.render(info["label"], True, C.WHITE)
            self.scr.blit(tl, (row.x+39-tl.get_width()//2, row.y+39-tl.get_height()//2))
            col = C.WHITE if can else C.GRAY
            self.scr.blit(self.f_b.render(f"[{num}]  {info['name']}", True, col),
                          (row.x+78, row.y+14))
            self.scr.blit(self.f_sm.render(desc, True, (200,215,235)), (row.x+78, row.y+38))
            self.scr.blit(self.f_sm.render(f"${cost}", True, C.YELLOW), (row.x+78, row.y+56))
            owned = sum(1 for e in gs.employees if e.kind == kind)
            self.scr.blit(self.f_sm.render(f"x{owned}", True, C.CYAN), (row.right-60, row.y+56))

    # --- END OF DAY ---
    def _end_day(self, gs):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((0,0,0,225)); self.scr.blit(ov, (0,0))
        box = pygame.Rect(CFG.SW//2-sx(400), CFG.SH//2-sx(320), sx(800), sx(640))
        glass_panel(self.scr, box, radius=24, bg=(20,26,44,240), border=(255,215,90,220))
        s = gs.end_summary
        title = tr("you_won") if gs.game_won else f"{tr('day_end')} {s['day']}"
        tcol = C.GREEN if gs.game_won else C.YELLOW
        t = render_ar(self.f_xl, title, tcol)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            g = render_ar(self.f_xl, title, (200,150,40)); g.set_alpha(80)
            self.scr.blit(g, (box.centerx-t.get_width()//2+dx, box.y+26+dy))
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+26))
        st = int(round(s.get("rating",3.0))); stx = "★"*st + "☆"*(5-st)
        t = render_ar(self.f_l, f"{tr('rating')}: {stx} {s.get('rating',3.0):.1f}", C.YELLOW)
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+80))
        lines = [
            (tr("customers_served"), str(s['served']), C.WHITE),
            (tr("customers_lost"), str(s['lost']), C.RED),
            (tr("thieves_caught"), str(gs.player.caught), C.GREEN),
            (tr("revenue"), f"${s['earned']:.2f}", C.GREEN),
            (tr("purchases"), f"${s['spent']:.2f}", C.RED),
            (tr("salaries"), f"${s.get('salaries',0):.2f}", C.ORANGE),
            (tr("profit"), f"${s['profit']:.2f}", C.GREEN if s['profit']>=0 else C.RED),
            (tr("total"), f"${s['money']:.2f}", C.YELLOW),
            (tr("level"), f"{s['level']+1} - {LEVELS[s['level']]['name']}", C.CYAN),
        ]
        for i, (label, val, col) in enumerate(lines):
            y = box.y+140+i*34
            self.scr.blit(render_ar(self.f_b, label, (200,215,235)), (box.x+60, y))
            self.scr.blit(self.f_b.render(val, True, col), (box.x+440, y))
        for b in self.end_buttons:
            b.rect = pygame.Rect(CFG.SW//2-sx(170), box.bottom-90, sx(340), sx(56))
            b.draw(self.scr, render_ar)

    def _lvl_flash(self, alpha, progress):
        ov = pygame.Surface((CFG.SW, CFG.SH), pygame.SRCALPHA)
        ov.fill((60,220,100,alpha)); self.scr.blit(ov, (0,0))
        scale = 1.0 + 0.3 * progress
        t = self.f_xxl.render("LEVEL UP!", True, C.WHITE)
        w, h = int(t.get_width()*scale), int(t.get_height()*scale)
        ts = pygame.transform.smoothscale(t, (w, h))
        ts.set_alpha(max(0, 255 - int(progress*180)))
        self.scr.blit(ts, (CFG.SW//2-w//2, CFG.SH//2-h//2))

    def _tutorial(self, gs):
        tips = [
            ("Welcome!", "Move with WASD"),
            ("Restock shelves", "Stand near shelf, press E"),
            ("Hire Cashier", "Press H"),
            ("Or scan yourself", "Stand near register, press E"),
            ("Order stock", "Stand near PC, press E"),
            ("Catch thieves!", "Get close and press E"),
        ]
        if gs.tutorial >= len(tips): return
        title, sub = tips[gs.tutorial]
        box = pygame.Rect(CFG.SW//2-sx(360), CFG.SH-sx(170), sx(720), sx(120))
        glass_panel(self.scr, box, radius=16, bg=(20,26,44,235), border=(255,215,90,220))
        t = render_ar(self.f_l, title, C.YELLOW)
        self.scr.blit(t, (box.centerx-t.get_width()//2, box.y+18))
        t2 = render_ar(self.f_b, sub, C.WHITE)
        self.scr.blit(t2, (box.centerx-t2.get_width()//2, box.y+58))
        t3 = render_ar(self.f_sm, "SPACE", (170,200,220))
        self.scr.blit(t3, (box.centerx-t3.get_width()//2, box.bottom-24))


# ============================================================
# GAME CONTROLLER
# ============================================================
class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.init(44100, -16, 1, 512)
        self.scr = None
        self.apply_display()
        pygame.display.set_caption("Supermarket Simulator 2D — v9.0")
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        self.state = GS(self.audio)
        self.renderer = Renderer(self.scr)
        self.renderer._action_cb = self._handle_action

        global LOGO, SPRITES, TOUCH
        LOGO = load_img("logo.png")
        if LOGO:
            try: pygame.display.set_icon(LOGO)
            except Exception: pass

        # Sprite mapping
        SPRITES = {
            "player":    load_img("tile_0112.png", (40, 40)),
            "cashier":   load_img("tile_0088.png", (34, 34)),
            "stocker":   load_img("tile_0085.png", (34, 34)),
            "guard":     load_img("tile_0121.png", (34, 34)),
            "cleaner":   load_img("tile_0098.png", (34, 34)),
            "customer_1":load_img("tile_0084.png", (34, 34)),
            "customer_2":load_img("tile_0086.png", (34, 34)),
            "customer_3":load_img("tile_0087.png", (34, 34)),
            "customer_4":load_img("tile_0096.png", (34, 34)),
            "customer_5":load_img("tile_0097.png", (34, 34)),
            "customer_6":load_img("tile_0111.png", (34, 34)),
        }
        loaded = sum(1 for s in SPRITES.values() if s)
        print(f"[Assets] Loaded {loaded}/{len(SPRITES)} sprites")
        self.running = True
        pygame.mouse.set_visible(True)
        _fp = os.path.join(ASSET_DIR, "font.ttf")
        self.touch = None
        if TouchControls is not None:
            try:
                self.touch = TouchControls(CFG.SW, CFG.SH, SCALE, CFG.HUD_H,
                                           enabled=IS_ANDROID,
                                           font_path=_fp if os.path.exists(_fp) else None)
                TOUCH = self.touch
            except Exception as ex:
                print("[Touch] init failed:", ex)

    def apply_display(self):
        if IS_WEB:
            self.scr = pygame.display.set_mode((CFG.SW, CFG.SH))
        elif IS_ANDROID or SET.fullscreen:
            self.scr = pygame.display.set_mode(
                (CFG.SW, CFG.SH), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.scr = pygame.display.set_mode((CFG.SW, CFG.SH))

    def _handle_action(self, name):
        st = self.state
        if name == "new_game": st.new_game()
        elif name == "load":
            if st.load():
                st.show(tr("welcome"), 1.5)
                st.audio.play("daystart")
                st.state = "PLAY"
            else: st.show("No save!", 1.5)
        elif name == "settings":
            st.prev_state = st.state if st.state in ("MENU","PAUSE") else "MENU"
            st.state = "SETTINGS"
        elif name == "quit": self.running = False
        elif name == "resume": st.state = "PLAY"
        elif name == "save":
            if st.save(): st.show("Saved!", 1.5)
            st.state = "PLAY"
        elif name == "menu": st.state = "MENU"
        elif name == "toggle_lang": SET.toggle_lang()
        elif name == "toggle_fs":
            SET.toggle_fullscreen()
            self.apply_display()
            self.renderer.scr = self.scr
        elif name == "settings_back":
            st.state = st.prev_state or "MENU"
        elif name == "next_day": st.next_day()

    async def run(self):
        while self.running:
            dt = min(self.clock.tick(CFG.FPS)/1000.0, 0.1)
            self._events()
            if not self.running: break
            self.state.update(dt)
            self.renderer.draw(self.state)
            if self.touch is not None:
                self.touch.draw(self.scr, self.state)
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()
        if not IS_WEB: sys.exit()

    def _events(self):
        mp = pygame.mouse.get_pos()
        btns = self._active_buttons()
        for b in btns: b.update_hover(mp)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: self.running = False; return
            if self.touch is not None and ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                k = self.touch.process(ev, self.state)
                if k is not None: self._key(k)
                continue
            if ev.type == pygame.KEYDOWN and ev.key == getattr(pygame, "K_AC_BACK", -1):
                self._key(pygame.K_ESCAPE); continue
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                for b in btns:
                    if b.handle_event(ev, self.audio):
                        return
            if ev.type == pygame.KEYDOWN: self._key(ev.key)

    def _active_buttons(self):
        s = self.state.state
        if s == "MENU": return self.renderer.menu_buttons
        if s == "PAUSE": return self.renderer.pause_buttons
        if s == "SETTINGS": return self.renderer.settings_buttons
        if s == "END_OF_DAY": return self.renderer.end_buttons
        return []

    def _key(self, key):
        st = self.state
        if key == pygame.K_F5:
            if st.save(): st.show("Saved!",1.5)
            return
        if key == pygame.K_F9:
            if st.load(): st.show("Loaded!",1.5)
            else: st.show("No save!",1.5)
            return
        if st.state == "MENU":
            if key == pygame.K_SPACE: st.new_game()
            elif key == pygame.K_l:
                if st.load(): st.state = "PLAY"
            elif key == pygame.K_ESCAPE: self.running = False
        elif st.state == "INTRO":
            if key in (pygame.K_SPACE, pygame.K_RETURN): st._advance_intro()
        elif st.state == "PAUSE":
            if key in (pygame.K_p, pygame.K_ESCAPE): st.state = "PLAY"
        elif st.state == "SETTINGS":
            if key == pygame.K_ESCAPE:
                st.state = st.prev_state or "MENU"
        elif st.state == "PLAY":
            if st.tutorial < 6 and key == pygame.K_SPACE:
                st.tutorial += 1; return
            if key in (pygame.K_ESCAPE, pygame.K_p): st.state = "PAUSE"
            elif key == pygame.K_h: st.state = "HIRE"
            elif key == pygame.K_e: st.interact()
            elif key == pygame.K_n: st.player.day_time = st.player.lv()["day_len"]
        elif st.state == "SUPPLIER":
            if key == pygame.K_ESCAPE: st.state = "PLAY"
            elif pygame.K_1 <= key <= pygame.K_8: st.order(key - pygame.K_1)
        elif st.state == "HIRE":
            if key == pygame.K_ESCAPE: st.state = "PLAY"
            elif key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4):
                kinds = [EKind.CASHIER, EKind.STOCKER, EKind.GUARD, EKind.CLEANER]
                st.hire(kinds[key - pygame.K_1])
        elif st.state == "END_OF_DAY":
            if key == pygame.K_SPACE: st.next_day()


# ============================================================
# ENTRY
# ============================================================
async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
