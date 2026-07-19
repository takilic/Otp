import asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
import unicodedata
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest

try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== EMOJI CONFIGURATION ENGINE ====================

EMOJI_ID_MAP = {
    "telegram": "5271801931814165886",
    "instagram": "5269682734820777950",
    "facebook": "5269427536453984598",
    "tiktok": "5271527792641595125",
    "x": "5269500885905468781",
    "whatsapp": "5271536803482981220",
    "discord": "5807892405306791778",
    "uber": "5298715455316303708",
    "up": "5244837092042750681",
    "down": "5246762912428603768",
    "add": "5397916757333654639",
    "setting": "5341715473882955310",
    "1st": "5440539497383087970",
    "2st": "5447203607294265305",
    "3rd": "5453902265922376865",
    "free": "5406756500108501710",
    "msg": "5253742260054409879",
    "link": "5271604874419647061",
    "status": "5231200819986047254",
    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",
    "delete": "5422557736330106570",
    "refer_btn": "5420396762189831222",
    "get_number_btn": "5382357040008021292",
    "cross": "5420130255174145507",
    "stop": "5956074558044770726",
    "ban": "5420323339723881652",
    "done": "6298670698948724690",
    "nagad": "5352985330628730418",
    "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",
    "binance": "5348212415077064131",
    "live": "5355102594886833928",
    "channel": "6215074610845585917",
    "admin": "5350396951407895212",
    "waiting": "6217721388736712699",
    "back": "5267490665117275176",
    "leader_board": "5280769763398671636",
    "money": "6233367447789899509",
    "change_number": "5402186569006210455"
}

PREMIUM_FLAGS = {
    "🇺🇸": "5913463998522592692",
    "🇺🇦": "5911406692007941050",
    "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323",
    "🇨🇳": "5913779335021466780",
    "🇦🇿": "5911197578640233518",
    "🇪🇺": "5911106310585193018",
    "🇦🇲": "5913272455866093666",
    "🇷🇺": "5913274246867456342",
    "🇺🇿": "5911051846104912282",
    "🇩🇪": "5911096835887337583",
    "🇯🇵": "5913293711659241040",
    "🇹🇷": "5910995113881901195",
    "🇧🇾": "5911011185649521599",
    "🇬🇧": "5913443365499703513",
    "🇮🇳": "5913754823643107921",
    "🇧🇷": "5911148568768418614",
    "🇿🇲": "5913564754160389778",
    "🇾🇪": "5913346492512341993",
    "🇻🇳": "5913428887164949581",
    "🇨🇲": "5911172109484167745",
    "🇨🇮": "5222233374948602940",
    "🇲🇬": "5913766918271012920",
    "🇷🇴": "5913460373570195273",
    "🇨🇫": "5913443245240619222",
    "🇹🇬": "5913423260757790970",
    "🇧🇯": "5913735869952430547",
    "🇸🇱": "5911210450657218661",
    "🇧🇩": "5911365056594973179",
    "🇰🇷": "5913371673905598425",
    "🇬🇶": "5911306279967529251",
    "🇬🇱": "5292014752283774878",
    "🇫🇴": "5296469342039327674",
    "🇧🇳": "5911336409163109113",
    "🇧🇬": "5294329219965272288",
    "🇧🇫": "5913407764515786948",
    "🇪🇷": "5433723401464198287",
    "🇲🇼": "5433968339154122439",
    "🇲🇷": "5433859405898594234",
    "🇳🇷": "5434131139889478358",
    "🇸🇦": "4985897134424328239",
    "🇹🇴": "5433640100573491806",
    "🇹🇻": "5433684690923961019",
    "🇹🇼": "5366187256937726720",
    "🇭🇰": "5292166459118606932",
    "🇲🇴": "6323557758096377611",
    "🇨🇺": "5431551436502611633",
    "🇰🇵": "5434142701941437163",
    "🇻🇪": "5434009132753499322",
    "🇸🇾": "5433910876786670092",
    "🇲🇲": "5433666360003540231",
    "🇳🇮": "5334807849418003620",
    "🇬🇳": "5913471858312744319",
    "🇰🇪": "5222279743415531561",
    "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "5911297801702084799",
    "🇻🇦": "5911211932420938860",
    "🇻🇺": "5913511535220625585",
    "🇺🇾": "5913623088406204470",
    "🇦🇪": "5913726554168365343",
    "🇺🇬": "5913488939397681980",
    "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671",
    "🇹🇹": "5911228635548750294",
    "🇹🇭": "5913617968805187987",
    "🇹🇿": "5911418949844603556",
    "🇹🇯": "5911287639809463107",
    "🇨🇭": "5913271227505448072",
    "🇸🇪": "5911156510162949403",
    "🇸🇿": "5913374525763883286",
    "🇸🇷": "5913275539652611719",
    "🇸🇩": "5911387497799094470",
    "🇪🇸": "5911193287967904547",
    "🇱🇰": "5911293163137406640",
    "🇸🇸": "5911406262511211744",
    "🇿🇦": "5911203119148044594",
    "🇸🇴": "5911397852965244436",
    "🇸🇧": "5911482712929080608",
    "🇸🇮": "5913431983836368644",
    "🇸🇰": "5913751666842145020",
    "🇸🇬": "5911531460808051849",
    "🇸🇨": "5911185183364616913",
    "🇷🇸": "5913592598433369871",
    "🇸🇳": "5910995302860461643",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "5911460091336331851",
    "🇸🇹": "5913574331937462345",
    "🇸🇲": "5913587968458625465",
    "🇼🇸": "5913325971158602854",
    "🇰🇳": "5913691898077253637",
    "🇻🇨": "5911318941531116255",
    "🇱🇨": "5911243659344351824",
    "🇵🇸": "5913684768431541668",
    "🇷🇼": "5911455229433352234",
    "🇶🇦": "5911260864983339619",
    "🇵🇷": "5911504350974317480",
    "🇵🇹": "5911023653939581472",
    "🇵🇭": "5911268638874145162",
    "🇵🇪": "5911207993935925780",
    "🇵🇾": "5911014265141072316",
    "🇵🇬": "5911107251183030903",
    "🇵🇦": "5913428968769327174",
    "🇵🇼": "5911283903187915549",
    "🇵🇰": "5913705895375672082",
    "🇴🇲": "5913570801474343473",
    "🇳🇴": "5913617397574537046",
    "🇳🇬": "5911143844304393105",
    "🇳🇪": "5911270086278124251",
    "🇳🇿": "5913640044937089340",
    "🇳🇱": "5913367645226275100",
    "🇳🇵": "5913496520014958723",
    "🇳🇦": "5911108535378252443",
    "🇲🇿": "5911333419865871464",
    "🇲🇦": "5911482111633658301",
    "🇲🇪": "5913239436157522151",
    "🇲🇳": "5911041383564580038",
    "🇲🇨": "5911245347266500057",
    "🇲🇩": "5913456847402045950",
    "🇲🇻": "5913501399097806832",
    "🇲🇱": "5911305266355245916",
    "🇲🇹": "5911023714069123567",
    "🇧🇲": "5913680005312811090",
    "🇲🇶": "5911378005921370347",
    "🇲🇭": "5913235935759175692",
    "🇲🇺": "5913291113204027321",
    "🇲🇽": "5913687302462246518",
    "🇫🇲": "5911271104185373336",
    "🇲🇾": "5913654360063087453",
    "🇲🇰": "5913394029210374721",
    "🇱🇺": "5913390842344640293",
    "🇱🇹": "5911172315642597775",
    "🇱🇮": "5911166650580734660",
    "🇱🇾": "5911236989260140996",
    "🇱🇷": "5913324167272337727",
    "🇰🇮": "5911294443037660118",
    "🇽🇰": "5911433681582429010",
    "🇰🇼": "5913290705182134003",
    "🇰🇬": "5911202161370337549",
    "🇱🇦": "5913718526874489279",
    "🇱🇻": "5913738489882480243",
    "🇱🇧": "5911504273664905447",
    "🇱🇸": "5911059881988723711",
    "🇮🇩": "5913479361620611038",
    "🇮🇷": "5911308891307643032",
    "🇮🇶": "5911382442622587735",
    "🇮🇪": "5913440715504881532",
    "🇮🇱": "5911471936856134692",
    "🇮🇹": "5913688444923547525",
    "🇯🇲": "5913232280742006526",
    "🇯🇴": "5913234136167878475",
    "🇮🇸": "5911047899029967246",
    "🇭🇺": "5913767635530551104",
    "🇭🇳": "5911406889576436289",
    "🇭🇹": "5913459789454643194",
    "🇬🇾": "5913579412883771480",
    "🇬🇼": "5911398694778836149",
    "🇬🇹": "5913324858762072330",
    "🇬🇩": "5913228063084121946",
    "🇬🇷": "5911210399117611448",
    "🇬🇭": "5913391155877252952",
    "🇬🇪": "5913434771270144023",
    "🇬🇲": "5913657267755945883",
    "🇬🇦": "5911037896051137264",
    "🇫🇷": "5913605586414473124",
    "🇫🇮": "5911041344909873378",
    "🇫🇯": "5911393832875856716",
    "🇪🇹": "5911078333168227043",
    "🇩🇴": "5911152099231536123",
    "🇩🇲": "5911377121158107430",
    "🇩🇯": "5911407709915190157",
    "🇩🇰": "5911206009661034712",
    "🇨🇾": "5911023550860366409",
    "🇭🇷🇨🇷": "5913692684056269311",
    "🇨🇷": "5911261745451635030",
    "🇨🇬": "5911338788574990168",
    "🇨🇩": "5913770362834783827",
    "🇰🇲": "5911338582416560604",
    "🇰🇭": "5913699998385573485",
    "🇨🇦": "5913623736946265914",
    "🇨🇻": "5913571501554012193",
    "🇹🇩": "5913299849167507310",
    "🇨🇿": "5911198691036764307",
    "🇨🇱": "5911470957603592832",
    "🇨🇴": "5913773060074246009",
    "🇧🇮": "5913766441529642752",
    "🇧🇼": "5911513782722499475",
    "🇧🇦": "5913700002680541032",
    "🇧🇴": "5913638795101606133",
    "🇧🇹": "5913236734623093021",
    "🇦🇷": "5913573356979884082",
    "🇦🇺": "5913632326880858455",
    "🇦🇹": "5911338831524664592",
    "🇧🇸": "5911451643135660214",
    "🇧🇭": "5913581663446634403",
    "🇧🇧": "5911016996740272263",
    "🇧🇪": "5913529642802745141",
    "🇧🇿": "5913355005137522807",
    "🇦🇬": "5913389025573475085",
    "🇦🇴": "5913753316109586411",
    "🇦🇩": "5911314702398396902",
    "🇩🇿": "5913782968563800236",
    "🇦🇱": "5911357458797826163",
    "🇦𝒇": "5913492040364068694",
    "🇿🇼": "5911092502265336396"
}

def p_em(key: str, fallback: str = "⭐") -> str:
    key_clean = str(key).strip().lower()
    if key_clean in EMOJI_ID_MAP:
        return f'<tg-emoji emoji-id="{EMOJI_ID_MAP[key_clean]}">{fallback}</tg-emoji>'
    if key in PREMIUM_FLAGS:
        return f'<tg-emoji emoji-id="{PREMIUM_FLAGS[key]}">{fallback}</tg-emoji>'
    return fallback

def strip_html_tags(text: str) -> str:
    return re.sub(r'<[^>]*>', '', str(text))

# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8436137039:AAFJDtiKNN6XfQbsHLG_ElkXNDl_0i4lETc"
API_KEY = "api_key_by_mino"  
BASE_URL = "https://mino-sms-panel.xyz"      

# --- SYSTEM IDS & ADMINS ---
ADMINS = [7060497904]
OTP_GROUP_ID = -1004469841752

# --- SYSTEM LINKS & USERNAME SETTINGS ---
DEFAULT_WELCOME_MESSAGE = f"{p_em('live')} <b>MINO NUMBER BOT</b> {p_em('live')}\n━━━━━━━━━━━━━━━━━━━━━━━━\n{p_em('status')} <b>START INSTANT OTP RECEPTION NOW!</b> {p_em('status')}\n━━━━━━━━━━━━━━━━━━━━━━━━"
DEFAULT_OTP_GROUP_URL = "https://t.me/zusotpgr"
DEFAULT_CHANNEL_URL = "https://t.me/zusotp"
DEFAULT_SUPPORT_USERNAME = "@opzus69"
FORCE_JOIN_CHANNELS = ["@zusotp"]

# --- WITHDRAWAL & STATS LIMITS ---
DEFAULT_MIN_WITHDRAW = 0.5
DEFAULT_MAX_WITHDRAW = 100.0
DEFAULT_COOLDOWN_TIME = 1.0
DEFAULT_OTP_REWARD = 0.0020
DEFAULT_REFER_BONUS = 0.050
DEFAULT_NUMBERS_PER_REQUEST = 3
MAX_NUMBERS_PER_USER = 10000

# --- DATA FILES ---
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"
ACTIVE_NUMBERS_FILE = "active_numbers.json"
MANUAL_RANGES_FILE = "manual_ranges.json"

# ========================================================

def load_active_numbers():
    if not os.path.exists(ACTIVE_NUMBERS_FILE):
        return {}
    try:
        with open(ACTIVE_NUMBERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_active_numbers(data):
    try:
        with open(ACTIVE_NUMBERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving active numbers: {e}")

# ==================== MANUAL RANGE STORAGE ====================

def load_manual_ranges():
    if not os.path.exists(MANUAL_RANGES_FILE):
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(MANUAL_RANGES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_manual_ranges(data):
    try:
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving manual ranges: {e}")

# ==================== BUTTON COLOR PATCH ENGINE ====================

def rbtn(text: str, style: str = None, callback_data: str = None, url: str = None, icon_custom_emoji_id: str = None):
    clean_text = strip_html_tags(text)
    kwargs = {"text": clean_text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    
    if style:
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("style", None)
        kwargs.pop("icon_custom_emoji_id", None)
        
        api_kwargs = {}
        if style:
            api_kwargs["style"] = style
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
            
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
            
        return InlineKeyboardButton(**kwargs)


def rkbtn(text: str, icon_custom_emoji_id: str = None, style: str = None):
    kwargs = {"text": text}
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    if style:
        kwargs["style"] = style
        
    try:
        return KeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        kwargs.pop("style", None)
        api_kwargs = {}
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        if style:
            api_kwargs["style"] = style
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
        return KeyboardButton(**kwargs)

# ==================== SYSTEM DYNAMIC SETTINGS ====================

def load_settings():
    default_settings = {
        "max_numbers_per_user": MAX_NUMBERS_PER_USER,
        "welcome_message": DEFAULT_WELCOME_MESSAGE,
        "otp_group_url": DEFAULT_OTP_GROUP_URL,
        "channel_url": DEFAULT_CHANNEL_URL,
        "support_username": DEFAULT_SUPPORT_USERNAME,
        "maintenance_mode": False,
        "min_withdraw": DEFAULT_MIN_WITHDRAW,
        "max_withdraw": DEFAULT_MAX_WITHDRAW,
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "cooldown_time": DEFAULT_COOLDOWN_TIME,          
        "force_join_enabled": False,   
        "force_join_channels": FORCE_JOIN_CHANNELS, 
        "join_alert_enabled": True,     
        "otp_reward": DEFAULT_OTP_REWARD,          
        "refer_bonus": DEFAULT_REFER_BONUS,          
        "numbers_per_request": DEFAULT_NUMBERS_PER_REQUEST,
        "auto_range": True      
    }

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f, indent=1)
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            
        updated = False
        
        for k, v in default_settings.items():
            if k not in data:
                data[k] = v
                updated = True
                
        if updated:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=1)
        return data
    except:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=1)

def get_api_credentials():
    settings = load_settings()
    raw_key = settings.get("api_key", API_KEY)
    raw_url = settings.get("base_url", BASE_URL)
    raw_url = str(raw_url).strip().rstrip('/')
    return raw_key, raw_url

def get_withdraw_limits():
    settings = load_settings()
    return float(settings.get("min_withdraw", DEFAULT_MIN_WITHDRAW)), float(settings.get("max_withdraw", DEFAULT_MAX_WITHDRAW))

def is_under_maintenance(uid):
    settings = load_settings()
    return settings.get("maintenance_mode", False) and not is_admin(uid)

request_queue = asyncio.Queue() 
MAX_WORKERS = 50000 

client_async = httpx.AsyncClient(
    timeout=10.0,
    verify=False,
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
)

active_numbers = load_active_numbers()
last_range = {}
last_request_time = {} 
CHECK_INTERVAL = 0.1

# ==================== GLOBAL RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_platform_icon(platform_name: str) -> str:
    name_lower = platform_name.lower().strip()
    if name_lower in EMOJI_ID_MAP:
        return p_em(name_lower)
    return ""

def make_bold_text(text: str) -> str:
    out = []
    for char in str(text):
        o = ord(char)
        if 65 <= o <= 90: 
            out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122: 
            out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57: 
            out.append(chr(o - 48 + 0x1D7EC))
        else:
            out.append(char)
    return "".join(out)

def unstyle_text(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKC', str(text))
    return normalized

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            settings = load_settings()
            if settings.get("auto_range", True) and not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, err = await fetch_top55_ranges_by_app()
                    if data:
                        import time as _time
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = _time.monotonic()
                except Exception:
                    pass
                finally:
                    _ranges_cache["fetching"] = False
        except Exception:
            pass
        await asyncio.sleep(200)

# ==================== CHECK IF USER IS ADMIN ====================

def is_admin(user_id):
    return user_id in ADMINS

# ==================== WITHDRAW DATA FUNCTIONS ====================

def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS FUNCTIONS ====================

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== DATA RANGE FILE ====================

def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    try:
        with open(DATA_RAimport asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
import unicodedata
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest

try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== EMOJI CONFIGURATION ENGINE ====================

EMOJI_ID_MAP = {
    "telegram": "5271801931814165886",
    "instagram": "5269682734820777950",
    "facebook": "5269427536453984598",
    "tiktok": "5271527792641595125",
    "x": "5269500885905468781",
    "whatsapp": "5271536803482981220",
    "discord": "5807892405306791778",
    "uber": "5298715455316303708",
    "up": "5244837092042750681",
    "down": "5246762912428603768",
    "add": "5397916757333654639",
    "setting": "5341715473882955310",
    "1st": "5440539497383087970",
    "2st": "5447203607294265305",
    "3rd": "5453902265922376865",
    "free": "5406756500108501710",
    "msg": "5253742260054409879",
    "link": "5271604874419647061",
    "status": "5231200819986047254",
    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",
    "delete": "5422557736330106570",
    "refer_btn": "5420396762189831222",
    "get_number_btn": "5382357040008021292",
    "cross": "5420130255174145507",
    "stop": "5956074558044770726",
    "ban": "5420323339723881652",
    "done": "6298670698948724690",
    "nagad": "5352985330628730418",
    "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",
    "binance": "5348212415077064131",
    "live": "5355102594886833928",
    "channel": "6215074610845585917",
    "admin": "5350396951407895212",
    "waiting": "6217721388736712699",
    "back": "5267490665117275176",
    "leader_board": "5280769763398671636",
    "money": "6233367447789899509",
    "change_number": "5402186569006210455"
}

PREMIUM_FLAGS = {
    "🇺🇸": "5913463998522592692",
    "🇺🇦": "5911406692007941050",
    "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323",
    "🇨🇳": "5913779335021466780",
    "🇦🇿": "5911197578640233518",
    "🇪🇺": "5911106310585193018",
    "🇦🇲": "5913272455866093666",
    "🇷🇺": "5913274246867456342",
    "🇺🇿": "5911051846104912282",
    "🇩🇪": "5911096835887337583",
    "🇯🇵": "5913293711659241040",
    "🇹🇷": "5910995113881901195",
    "🇧🇾": "5911011185649521599",
    "🇬🇧": "5913443365499703513",
    "🇮🇳": "5913754823643107921",
    "🇧🇷": "5911148568768418614",
    "🇿🇲": "5913564754160389778",
    "🇾🇪": "5913346492512341993",
    "🇻🇳": "5913428887164949581",
    "🇨🇲": "5911172109484167745",
    "🇨🇮": "5222233374948602940",
    "🇲🇬": "5913766918271012920",
    "🇷🇴": "5913460373570195273",
    "🇨🇫": "5913443245240619222",
    "🇹🇬": "5913423260757790970",
    "🇧🇯": "5913735869952430547",
    "🇸🇱": "5911210450657218661",
    "🇧🇩": "5911365056594973179",
    "🇰🇷": "5913371673905598425",
    "🇬🇶": "5911306279967529251",
    "🇬🇱": "5292014752283774878",
    "🇫🇴": "5296469342039327674",
    "🇧🇳": "5911336409163109113",
    "🇧🇬": "5294329219965272288",
    "🇧🇫": "5913407764515786948",
    "🇪🇷": "5433723401464198287",
    "🇲🇼": "5433968339154122439",
    "🇲🇷": "5433859405898594234",
    "🇳🇷": "5434131139889478358",
    "🇸🇦": "4985897134424328239",
    "🇹🇴": "5433640100573491806",
    "🇹🇻": "5433684690923961019",
    "🇹🇼": "5366187256937726720",
    "🇭🇰": "5292166459118606932",
    "🇲🇴": "6323557758096377611",
    "🇨🇺": "5431551436502611633",
    "🇰🇵": "5434142701941437163",
    "🇻🇪": "5434009132753499322",
    "🇸🇾": "5433910876786670092",
    "🇲🇲": "5433666360003540231",
    "🇳🇮": "5334807849418003620",
    "🇬🇳": "5913471858312744319",
    "🇰🇪": "5222279743415531561",
    "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "5911297801702084799",
    "🇻🇦": "5911211932420938860",
    "🇻🇺": "5913511535220625585",
    "🇺🇾": "5913623088406204470",
    "🇦🇪": "5913726554168365343",
    "🇺🇬": "5913488939397681980",
    "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671",
    "🇹🇹": "5911228635548750294",
    "🇹🇭": "5913617968805187987",
    "🇹🇿": "5911418949844603556",
    "🇹🇯": "5911287639809463107",
    "🇨🇭": "5913271227505448072",
    "🇸🇪": "5911156510162949403",
    "🇸🇿": "5913374525763883286",
    "🇸🇷": "5913275539652611719",
    "🇸🇩": "5911387497799094470",
    "🇪🇸": "5911193287967904547",
    "🇱🇰": "5911293163137406640",
    "🇸🇸": "5911406262511211744",
    "🇿🇦": "5911203119148044594",
    "🇸🇴": "5911397852965244436",
    "🇸🇧": "5911482712929080608",
    "🇸🇮": "5913431983836368644",
    "🇸🇰": "5913751666842145020",
    "🇸🇬": "5911531460808051849",
    "🇸🇨": "5911185183364616913",
    "🇷🇸": "5913592598433369871",
    "🇸🇳": "5910995302860461643",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "5911460091336331851",
    "🇸🇹": "5913574331937462345",
    "🇸🇲": "5913587968458625465",
    "🇼🇸": "5913325971158602854",
    "🇰🇳": "5913691898077253637",
    "🇻🇨": "5911318941531116255",
    "🇱🇨": "5911243659344351824",
    "🇵🇸": "5913684768431541668",
    "🇷🇼": "5911455229433352234",
    "🇶🇦": "5911260864983339619",
    "🇵🇷": "5911504350974317480",
    "🇵🇹": "5911023653939581472",
    "🇵🇭": "5911268638874145162",
    "🇵🇪": "5911207993935925780",
    "🇵🇾": "5911014265141072316",
    "🇵🇬": "5911107251183030903",
    "🇵🇦": "5913428968769327174",
    "🇵🇼": "5911283903187915549",
    "🇵🇰": "5913705895375672082",
    "🇴🇲": "5913570801474343473",
    "🇳🇴": "5913617397574537046",
    "🇳🇬": "5911143844304393105",
    "🇳🇪": "5911270086278124251",
    "🇳🇿": "5913640044937089340",
    "🇳🇱": "5913367645226275100",
    "🇳🇵": "5913496520014958723",
    "🇳🇦": "5911108535378252443",
    "🇲🇿": "5911333419865871464",
    "🇲🇦": "5911482111633658301",
    "🇲🇪": "5913239436157522151",
    "🇲🇳": "5911041383564580038",
    "🇲🇨": "5911245347266500057",
    "🇲🇩": "5913456847402045950",
    "🇲🇻": "5913501399097806832",
    "🇲🇱": "5911305266355245916",
    "🇲🇹": "5911023714069123567",
    "🇧🇲": "5913680005312811090",
    "🇲🇶": "5911378005921370347",
    "🇲🇭": "5913235935759175692",
    "🇲🇺": "5913291113204027321",
    "🇲🇽": "5913687302462246518",
    "🇫🇲": "5911271104185373336",
    "🇲🇾": "5913654360063087453",
    "🇲🇰": "5913394029210374721",
    "🇱🇺": "5913390842344640293",
    "🇱🇹": "5911172315642597775",
    "🇱🇮": "5911166650580734660",
    "🇱🇾": "5911236989260140996",
    "🇱🇷": "5913324167272337727",
    "🇰🇮": "5911294443037660118",
    "🇽🇰": "5911433681582429010",
    "🇰🇼": "5913290705182134003",
    "🇰🇬": "5911202161370337549",
    "🇱🇦": "5913718526874489279",
    "🇱🇻": "5913738489882480243",
    "🇱🇧": "5911504273664905447",
    "🇱🇸": "5911059881988723711",
    "🇮🇩": "5913479361620611038",
    "🇮🇷": "5911308891307643032",
    "🇮🇶": "5911382442622587735",
    "🇮🇪": "5913440715504881532",
    "🇮🇱": "5911471936856134692",
    "🇮🇹": "5913688444923547525",
    "🇯🇲": "5913232280742006526",
    "🇯🇴": "5913234136167878475",
    "🇮🇸": "5911047899029967246",
    "🇭🇺": "5913767635530551104",
    "🇭🇳": "5911406889576436289",
    "🇭🇹": "5913459789454643194",
    "🇬🇾": "5913579412883771480",
    "🇬🇼": "5911398694778836149",
    "🇬🇹": "5913324858762072330",
    "🇬🇩": "5913228063084121946",
    "🇬🇷": "5911210399117611448",
    "🇬🇭": "5913391155877252952",
    "🇬🇪": "5913434771270144023",
    "🇬🇲": "5913657267755945883",
    "🇬🇦": "5911037896051137264",
    "🇫🇷": "5913605586414473124",
    "🇫🇮": "5911041344909873378",
    "🇫🇯": "5911393832875856716",
    "🇪🇹": "5911078333168227043",
    "🇩🇴": "5911152099231536123",
    "🇩🇲": "5911377121158107430",
    "🇩🇯": "5911407709915190157",
    "🇩🇰": "5911206009661034712",
    "🇨🇾": "5911023550860366409",
    "🇭🇷🇨🇷": "5913692684056269311",
    "🇨🇷": "5911261745451635030",
    "🇨🇬": "5911338788574990168",
    "🇨🇩": "5913770362834783827",
    "🇰🇲": "5911338582416560604",
    "🇰🇭": "5913699998385573485",
    "🇨🇦": "5913623736946265914",
    "🇨🇻": "5913571501554012193",
    "🇹🇩": "5913299849167507310",
    "🇨🇿": "5911198691036764307",
    "🇨🇱": "5911470957603592832",
    "🇨🇴": "5913773060074246009",
    "🇧🇮": "5913766441529642752",
    "🇧🇼": "5911513782722499475",
    "🇧🇦": "5913700002680541032",
    "🇧🇴": "5913638795101606133",
    "🇧🇹": "5913236734623093021",
    "🇦🇷": "5913573356979884082",
    "🇦🇺": "5913632326880858455",
    "🇦🇹": "5911338831524664592",
    "🇧🇸": "5911451643135660214",
    "🇧🇭": "5913581663446634403",
    "🇧🇧": "5911016996740272263",
    "🇧🇪": "5913529642802745141",
    "🇧🇿": "5913355005137522807",
    "🇦🇬": "5913389025573475085",
    "🇦🇴": "5913753316109586411",
    "🇦🇩": "5911314702398396902",
    "🇩🇿": "5913782968563800236",
    "🇦🇱": "5911357458797826163",
    "🇦𝒇": "5913492040364068694",
    "🇿🇼": "5911092502265336396"
}

def p_em(key: str, fallback: str = "⭐") -> str:
    key_clean = str(key).strip().lower()
    if key_clean in EMOJI_ID_MAP:
        return f'<tg-emoji emoji-id="{EMOJI_ID_MAP[key_clean]}">{fallback}</tg-emoji>'
    if key in PREMIUM_FLAGS:
        return f'<tg-emoji emoji-id="{PREMIUM_FLAGS[key]}">{fallback}</tg-emoji>'
    return fallback

def strip_html_tags(text: str) -> str:
    return re.sub(r'<[^>]*>', '', str(text))

# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8436137039:AAFJDtiKNN6XfQbsHLG_ElkXNDl_0i4lETc"
API_KEY = "api_key_by_mino"  
BASE_URL = "https://mino-sms-panel.xyz"      

# --- SYSTEM IDS & ADMINS ---
ADMINS = [7060497904]
OTP_GROUP_ID = -1004469841752

# --- SYSTEM LINKS & USERNAME SETTINGS ---
DEFAULT_WELCOME_MESSAGE = f"{p_em('live')} <b>MINO NUMBER BOT</b> {p_em('live')}\n━━━━━━━━━━━━━━━━━━━━━━━━\n{p_em('status')} <b>START INSTANT OTP RECEPTION NOW!</b> {p_em('status')}\n━━━━━━━━━━━━━━━━━━━━━━━━"
DEFAULT_OTP_GROUP_URL = "https://t.me/zusotpgr"
DEFAULT_CHANNEL_URL = "https://t.me/zusotp"
DEFAULT_SUPPORT_USERNAME = "@opzus69"
FORCE_JOIN_CHANNELS = ["@zusotp"]

# --- WITHDRAWAL & STATS LIMITS ---
DEFAULT_MIN_WITHDRAW = 0.5
DEFAULT_MAX_WITHDRAW = 100.0
DEFAULT_COOLDOWN_TIME = 1.0
DEFAULT_OTP_REWARD = 0.0020
DEFAULT_REFER_BONUS = 0.050
DEFAULT_NUMBERS_PER_REQUEST = 3
MAX_NUMBERS_PER_USER = 10000

# --- DATA FILES ---
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"
ACTIVE_NUMBERS_FILE = "active_numbers.json"
MANUAL_RANGES_FILE = "manual_ranges.json"

# ========================================================

def load_active_numbers():
    if not os.path.exists(ACTIVE_NUMBERS_FILE):
        return {}
    try:
        with open(ACTIVE_NUMBERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_active_numbers(data):
    try:
        with open(ACTIVE_NUMBERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving active numbers: {e}")

# ==================== MANUAL RANGE STORAGE ====================

def load_manual_ranges():
    if not os.path.exists(MANUAL_RANGES_FILE):
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(MANUAL_RANGES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_manual_ranges(data):
    try:
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving manual ranges: {e}")

# ==================== BUTTON COLOR PATCH ENGINE ====================

def rbtn(text: str, style: str = None, callback_data: str = None, url: str = None, icon_custom_emoji_id: str = None):
    clean_text = strip_html_tags(text)
    kwargs = {"text": clean_text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    
    if style:
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("style", None)
        kwargs.pop("icon_custom_emoji_id", None)
        
        api_kwargs = {}
        if style:
            api_kwargs["style"] = style
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
            
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
            
        return InlineKeyboardButton(**kwargs)


def rkbtn(text: str, icon_custom_emoji_id: str = None, style: str = None):
    kwargs = {"text": text}
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    if style:
        kwargs["style"] = style
        
    try:
        return KeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        kwargs.pop("style", None)
        api_kwargs = {}
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        if style:
            api_kwargs["style"] = style
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
        return KeyboardButton(**kwargs)

# ==================== SYSTEM DYNAMIC SETTINGS ====================

def load_settings():
    default_settings = {
        "max_numbers_per_user": MAX_NUMBERS_PER_USER,
        "welcome_message": DEFAULT_WELCOME_MESSAGE,
        "otp_group_url": DEFAULT_OTP_GROUP_URL,
        "channel_url": DEFAULT_CHANNEL_URL,
        "support_username": DEFAULT_SUPPORT_USERNAME,
        "maintenance_mode": False,
        "min_withdraw": DEFAULT_MIN_WITHDRAW,
        "max_withdraw": DEFAULT_MAX_WITHDRAW,
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "cooldown_time": DEFAULT_COOLDOWN_TIME,          
        "force_join_enabled": False,   
        "force_join_channels": FORCE_JOIN_CHANNELS, 
        "join_alert_enabled": True,     
        "otp_reward": DEFAULT_OTP_REWARD,          
        "refer_bonus": DEFAULT_REFER_BONUS,          
        "numbers_per_request": DEFAULT_NUMBERS_PER_REQUEST,
        "auto_range": True      
    }

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f, indent=1)
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            
        updated = False
        
        for k, v in default_settings.items():
            if k not in data:
                data[k] = v
                updated = True
                
        if updated:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=1)
        return data
    except:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=1)

def get_api_credentials():
    settings = load_settings()
    raw_key = settings.get("api_key", API_KEY)
    raw_url = settings.get("base_url", BASE_URL)
    raw_url = str(raw_url).strip().rstrip('/')
    return raw_key, raw_url

def get_withdraw_limits():
    settings = load_settings()
    return float(settings.get("min_withdraw", DEFAULT_MIN_WITHDRAW)), float(settings.get("max_withdraw", DEFAULT_MAX_WITHDRAW))

def is_under_maintenance(uid):
    settings = load_settings()
    return settings.get("maintenance_mode", False) and not is_admin(uid)

request_queue = asyncio.Queue() 
MAX_WORKERS = 50000 

client_async = httpx.AsyncClient(
    timeout=10.0,
    verify=False,
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
)

active_numbers = load_active_numbers()
last_range = {}
last_request_time = {} 
CHECK_INTERVAL = 0.1

# ==================== GLOBAL RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_platform_icon(platform_name: str) -> str:
    name_lower = platform_name.lower().strip()
    if name_lower in EMOJI_ID_MAP:
        return p_em(name_lower)
    return ""

def make_bold_text(text: str) -> str:
    out = []
    for char in str(text):
        o = ord(char)
        if 65 <= o <= 90: 
            out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122: 
            out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57: 
            out.append(chr(o - 48 + 0x1D7EC))
        else:
            out.append(char)
    return "".join(out)

def unstyle_text(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKC', str(text))
    return normalized

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            settings = load_settings()
            if settings.get("auto_range", True) and not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, err = await fetch_top55_ranges_by_app()
                    if data:
                        import time as _time
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = _time.monotonic()
                except Exception:
                    pass
                finally:
                    _ranges_cache["fetching"] = False
        except Exception:
            pass
        await asyncio.sleep(200)

# ==================== CHECK IF USER IS ADMIN ====================

def is_admin(user_id):
    return user_id in ADMINS

# ==================== WITHDRAW DATA FUNCTIONS ====================

def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS FUNCTIONS ====================

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== DATA RANGE FILE ====================

def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    try:
        with open(DATA_RANGE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving range database: {e}")
