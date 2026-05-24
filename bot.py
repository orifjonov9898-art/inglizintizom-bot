import logging
import os
import threading
from datetime import datetime, time, date, timedelta
from calendar import monthrange
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN", "8617890120:AAHtbC7tSfqC5MiMWPNZPv9nGJBY5yb63Vo")

_web_app_url = os.environ.get("WEB_APP_URL", "")
if not _web_app_url:
    _domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
    _web_app_url = f"https://{_domain}" if _domain else ""
WEB_APP_BASE = _web_app_url.rstrip("/")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================
# MOTIVATSIYA
# =====================
MOTIVATIONS = [
    "💪 Har bir so'z — yangi imkoniyat!",
    "🔥 Bugun qilgan harakat ertangi muvaffaqiyat!",
    "🌟 Ingliz tili — dunyo eshigi!",
    "🚀 Siz har kundan kuchliroqsiz!",
    "🎯 Maqsadga qadam-qadam yetiladi!",
    "⚡ Ertalab o'qigan odam — g'olib!",
    "🌍 Ingliz tili bilgan odam hamma joyda erkin!",
    "💡 Bilim — hech kim tortib ololmaydigan boylik!",
    "🌅 Erta turgan odam imkoniyatlarni birinchi ko'radi!",
    "📚 Kitob o'qigan odam mingta hayot yashaydi!",
    "🏋️ Sog'lom tana — sog'lom fikr!",
    "🎵 Intizom — ozodlikning kaliti!",
]

# =====================
# KUNLIK ODATLAR
# =====================
HABITS = [
    {"id": "wake",    "icon": "🌅", "name": "Erta turish",          "desc": "04:30 da turish"},
    {"id": "english", "icon": "📚", "name": "Ingliz tili",           "desc": "2 soat o'rganish"},
    {"id": "book",    "icon": "📖", "name": "Kitob o'qish",          "desc": "30 daqiqa kitob"},
    {"id": "sport",   "icon": "🏋️", "name": "Sport / mashq",         "desc": "30 daqiqa harakat"},
    {"id": "water",   "icon": "💧", "name": "Suv ichish",            "desc": "8 stakan suv"},
    {"id": "nophone", "icon": "📵", "name": "Telefonsiz vaqt",       "desc": "1 soat telefonsiz"},
    {"id": "plan",    "icon": "📝", "name": "Kun rejasini tuzish",   "desc": "Kecha tuzish"},
    {"id": "reflect", "icon": "🌙", "name": "Kunlik tahlil",         "desc": "Kechqurun yozish"},
]

HABIT_IDS = [h["id"] for h in HABITS]
HABIT_MAP = {h["id"]: h for h in HABITS}

# =====================
# HAFTALIK INGLIZ REJA
# =====================
WEEK_PLAN = [
    {
        "focus": "So'z yodlash + Grammatika",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Kechagi 10 so'zni takrorlash",
                "Yangi 10 so'z o'rganish (used to, would, have been)",
                "Har bir so'zdan gap yozish",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Zamonlar jadvalini ko'zdan kechirish",
                "Fill in the blanks — 15 ta gap",
                "Xatolarni tahlil qilish",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Matn o'qish — zamonlar mavzusida",
                "Matndagi zamonlarni belgilash",
                "5 ta savolga javob yozish",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Podcast tinglash — 15 daqiqa",
                "Eshitgan zamonlarni yozib olish",
                "Qisqacha xulosa yozish",
            ]},
        ]
    },
    {
        "focus": "Present Tenses chuqurlash",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Kechagi so'zlarni test qilish",
                "Yangi 10 so'z: always, often, now, currently",
                "So'zlarni sinonim bilan yozish",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Present Simple vs Continuous farqlash",
                "20 ta gap mashqi",
                "O'z hayotingizdan 5 misol",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Qisqa matn o'qish (150-200 so'z)",
                "Present zamonlarini rang bilan belgilash",
                "Matn mazmunini o'z so'zlaringiz bilan yozish",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Dialog tinglash (YouTube: English with Lucy)",
                "Dialogni takrorlash — shadowing",
                "Yangi 5 ta ibora yozib olish",
            ]},
        ]
    },
    {
        "focus": "Past Tenses takrorlash",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Irregular verbs — 15 ta fe'l (go-went-gone)",
                "Yangi 10 so'z: yesterday, ago, last",
                "Kechagi kun haqida 5 gap yozish",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Past Simple vs Past Continuous farqlash",
                "While/When bilan 10 ta gap tuzish",
                "Past Perfect mashqi",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Tarixiy matn o'qish",
                "Voqealar ketma-ketligini yozish",
                "8 ta savolga Past zamonida javob",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Hikoya tinglash — Past zamonlarda",
                "Asosiy 5-7 voqeani yozib olish",
                "Hikoyani og'zaki qayta so'zlash",
            ]},
        ]
    },
    {
        "focus": "Future Tenses + Will/Going to",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Kelajak so'zlar: tomorrow, soon, next, eventually",
                "Yangi 10 so'z yodlash",
                "Rejalaring haqida 5 gap yozish",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Will vs Going to farqi",
                "Future Simple va Continuous — 15 ta gap",
                "Future Perfect: Will have done — 5 misol",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Kelgusiga oid matn o'qish",
                "Will va Going to ni toping",
                "O'z kelajak rejangizni xat shaklida yozish",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "TED Talk qisqasi tinglash",
                "Kelajak zamonlarni yozib olish",
                "2 daqiqa o'z rejalari haqida gapirish",
            ]},
        ]
    },
    {
        "focus": "Perfect Tenses — Have/Has/Had",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Past participle fe'llar — 15 ta (eaten, gone, written)",
                "Yangi 10 so'z yodlash",
                "Tajribalaringiz haqida 5 gap (I have never...)",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Present Perfect vs Simple Past",
                "Since/For bilan mashq",
                "Past Perfect — Had done: 5 misol",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Biography yoki maqola o'qish",
                "Have/Has/Had ni 3 xil rang bilan belgilash",
                "Matn haqida 6 savol yozish",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Hayot hikoyasi tinglash",
                "Have/Has/Had gaplarni yozish",
                "O'zingizning qisqa tarjimai holingizni yozish",
            ]},
        ]
    },
    {
        "focus": "Aralash zamonlar — Takrorlash",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Haftalik barcha so'zlarni tekshirish (70 ta)",
                "Eng qiyin 10 so'zni qayta yodlash",
                "So'zlardan mini-hikoya yozish",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Aralash zamonlar testi — 20 ta gap",
                "Xatolarni tahlil qilish",
                "Eng qiyin mavzuni qayta o'qish",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Uzun matn o'qish — 300 so'z",
                "Zamonlar jadvalini to'ldirish",
                "Matn bo'yicha 150 so'zlik essay",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Suhbat tinglash — 20 daqiqa",
                "Qaysi zamon ko'p uchraganini sanash",
                "Suhbatni yozma qayta tiklash",
            ]},
        ]
    },
    {
        "focus": "Mustahkamlash + Yakuniy amaliyot",
        "blocks": [
            {"time": "04:30–05:00", "label": "📚 So'z yodlash", "tasks": [
                "Haftalik barcha so'zlardan YAKUNIY TEST",
                "So'zlar bilan o'yinli takrorlash",
                "Keyingi hafta uchun 10 yangi so'z tanlash",
            ]},
            {"time": "05:00–05:30", "label": "✏️ Grammatika", "tasks": [
                "Haftalik grammatika yakuniy testi — 25 savol",
                "Natijani foiz hisobida baholash",
                "Keyingi hafta maqsadini yozish",
            ]},
            {"time": "05:30–06:00", "label": "📖 Reading", "tasks": [
                "Sevimli mavzuda matn tanlash",
                "Matnni baland ovozda o'qish",
                "Matn haqida fikr yozish",
            ]},
            {"time": "06:00–06:30", "label": "🎧 Listening", "tasks": [
                "Sevimli inglizcha kontent tinglash",
                "Haftalik nima o'rgandim — yozish",
                "Kelgusi hafta rejasini tuzish",
            ]},
        ]
    },
]

DAYS_UZ = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
DAYS_SHORT = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]

# =====================
# FOYDALANUVCHI MA'LUMOTLARI
# =====================
user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "done": set(),       # ingliz tili topshiriqlari
            "habits": {},        # {"2024-05-23": {"wake": True, "book": False, ...}}
            "chat_id": user_id,
            "subscribed": False,
            "joined": date.today().isoformat(),
        }
    return user_data[user_id]

def today_str():
    return date.today().isoformat()

def get_habit_day(uid, day_str=None):
    user = get_user(uid)
    d = day_str or today_str()
    if d not in user["habits"]:
        user["habits"][d] = {}
    return user["habits"][d]

def get_today_plan():
    day_idx = datetime.now().weekday()
    plan_idx = day_idx % 7
    return plan_idx, WEEK_PLAN[plan_idx]

def get_motivation():
    idx = datetime.now().day % len(MOTIVATIONS)
    return MOTIVATIONS[idx]

def get_day_name():
    weekday = datetime.now().weekday()
    day_name_idx = (weekday + 1) % 7
    return DAYS_UZ[day_name_idx]

def habit_pct(habit_day: dict) -> int:
    if not HABITS:
        return 0
    done = sum(1 for h in HABITS if habit_day.get(h["id"]))
    return int(done / len(HABITS) * 100)

def mini_bar(pct, length=5):
    filled = round(pct / 100 * length)
    return "🟩" * filled + "⬜" * (length - filled)

# =====================
# ASOSIY MENYU
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    get_user(uid)
    await update.message.reply_text(
        f"Salom, {user.first_name}! 👋\n\n"
        "🌟 *Shaxsiy Rivojlanish Boti*ga xush kelibsiz!\n\n"
        "Men sizga har kuni ingliz tili, kitob o'qish, erta turish "
        "va boshqa odatlaringizni kuzatishga yordam beraman.\n\n"
        "Quyidan bo'limni tanlang 👇",
        reply_markup=main_menu_markup(),
        parse_mode="Markdown"
    )

def webapp_button(label: str, path: str = "") -> InlineKeyboardButton:
    url = f"{WEB_APP_BASE}{path}" if WEB_APP_BASE else None
    if url:
        return InlineKeyboardButton(label, web_app=WebAppInfo(url=url))
    return InlineKeyboardButton(label, callback_data="noop")

def main_menu_markup():
    keyboard = [
        [webapp_button("🌐 Web App'da ochish", "/")],
        [InlineKeyboardButton("📅 Ingliz tili rejasi", callback_data="today"),
         InlineKeyboardButton("📊 Haftalik reja", callback_data="weekly")],
        [InlineKeyboardButton("✅ Kunlik odatlar", callback_data="habits_today"),
         InlineKeyboardButton("📈 Ko'rsatkichlar", callback_data="stats_menu")],
        [InlineKeyboardButton("💪 Motivatsiya", callback_data="motivation"),
         InlineKeyboardButton("🔔 Eslatma", callback_data="subscribe")],
    ]
    return InlineKeyboardMarkup(keyboard)

# =====================
# BUTTON HANDLER
# =====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data == "noop":
        return
    elif data == "menu":
        await query.edit_message_text(
            "🏠 *Asosiy menyu*",
            reply_markup=main_menu_markup(),
            parse_mode="Markdown"
        )
    elif data == "today":
        await send_today(query, uid)
    elif data == "weekly":
        await send_weekly(query)
    elif data == "motivation":
        await send_motivation(query)
    elif data == "progress":
        await send_progress(query, uid)
    elif data == "subscribe":
        await toggle_subscribe(query, uid, context)
    elif data == "habits_today":
        await send_habits(query, uid, today_str())
    elif data == "stats_menu":
        await send_stats_menu(query, uid)
    elif data == "stats_week":
        await send_weekly_stats(query, uid)
    elif data == "stats_month":
        await send_monthly_stats(query, uid)
    elif data == "stats_habits":
        await send_habit_stats(query, uid)
    elif data.startswith("tasks_"):
        await send_tasks(query, uid, data)
    elif data.startswith("t_"):
        await toggle_done(query, uid, data)
    elif data.startswith("h_"):
        await toggle_habit(query, uid, data)

# =====================
# INGLIZ TILI REJA
# =====================
async def send_today(query, uid=None):
    plan_idx, plan = get_today_plan()
    day_name = get_day_name()

    done_set = get_user(uid)["done"] if uid else set()
    total_tasks = sum(len(b["tasks"]) for b in plan["blocks"])
    done_today = sum(
        1 for bi, block in enumerate(plan["blocks"])
        for ti in range(len(block["tasks"]))
        if f"t_{plan_idx}_{bi}_{ti}" in done_set
    )

    text = f"📅 *Bugungi ingliz tili rejasi — {day_name}*\n"
    text += f"🎯 Mavzu: _{plan['focus']}_\n"
    text += f"⏰ Vaqt: 04:30 – 06:30\n"
    text += f"📊 Bajarildi: *{done_today}/{total_tasks}*\n\n"

    for block in plan["blocks"]:
        text += f"*{block['label']}* {block['time']}\n"
        for i, task in enumerate(block["tasks"], 1):
            text += f"  {i}. {task}\n"
        text += "\n"

    keyboard = [
        [InlineKeyboardButton("✅ Topshiriqlarni belgilash", callback_data=f"tasks_{plan_idx}")],
        [InlineKeyboardButton("✅ Kunlik odatlar", callback_data="habits_today"),
         InlineKeyboardButton("💪 Motivatsiya", callback_data="motivation")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def send_tasks(query, uid, data):
    parts = data.split("_")
    plan_idx = int(parts[1])
    plan = WEEK_PLAN[plan_idx]
    done_set = get_user(uid)["done"]

    total_tasks = sum(len(b["tasks"]) for b in plan["blocks"])
    done_today = sum(
        1 for bi, block in enumerate(plan["blocks"])
        for ti in range(len(block["tasks"]))
        if f"t_{plan_idx}_{bi}_{ti}" in done_set
    )

    text = f"✅ *Topshiriqlarni belgilash*\n"
    text += f"🎯 _{plan['focus']}_\n"
    text += f"📊 *{done_today}/{total_tasks}* bajarildi\n\n"
    text += "Bajargan topshiriqlaringizni bosing 👇"

    keyboard = []
    for bi, block in enumerate(plan["blocks"]):
        keyboard.append([InlineKeyboardButton(f"── {block['label']} ──", callback_data="noop")])
        for ti, task in enumerate(block["tasks"]):
            key = f"t_{plan_idx}_{bi}_{ti}"
            icon = "✅" if key in done_set else "⬜"
            short_task = task[:35] + "…" if len(task) > 35 else task
            keyboard.append([InlineKeyboardButton(f"{icon} {short_task}", callback_data=key)])

    keyboard.append([InlineKeyboardButton("📅 Rejaga qaytish", callback_data="today")])
    keyboard.append([InlineKeyboardButton("🏠 Menyu", callback_data="menu")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def toggle_done(query, uid, data):
    user = get_user(uid)
    key = data
    if key in user["done"]:
        user["done"].remove(key)
        await query.answer("❌ Bekor qilindi")
    else:
        user["done"].add(key)
        await query.answer("✅ Bajarildi!")
    parts = data.split("_")
    plan_idx = parts[1]
    await send_tasks(query, uid, f"tasks_{plan_idx}")

async def send_weekly(query):
    text = "📊 *Haftalik ingliz tili rejasi*\n"
    text += "⏰ Har kuni 04:30 – 06:30\n\n"

    days = ["Dush", "Sesh", "Chor", "Pay", "Juma", "Shan", "Yak"]
    for i, (day, plan) in enumerate(zip(days, WEEK_PLAN)):
        text += f"*{i+1}. {day}* — {plan['focus']}\n"

    text += "\n📚 So'z yodlash · ✏️ Grammatika · 📖 Reading · 🎧 Listening"

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi reja", callback_data="today")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# KUNLIK ODATLAR
# =====================
async def send_habits(query, uid, day_str):
    habit_day = get_habit_day(uid, day_str)
    done_count = sum(1 for h in HABITS if habit_day.get(h["id"]))
    total = len(HABITS)
    pct = int(done_count / total * 100) if total else 0
    bar = mini_bar(pct, 8)

    is_today = day_str == today_str()
    day_label = "Bugun" if is_today else day_str

    text = f"✅ *Kunlik odatlar — {day_label}*\n"
    text += f"{bar} *{pct}%* ({done_count}/{total})\n\n"
    text += "Har bir bajargan odatingizni belgilang 👇\n"

    keyboard = []
    for h in HABITS:
        done = habit_day.get(h["id"], False)
        icon = "✅" if done else "⬜"
        label = f"{icon} {h['icon']} {h['name']} — {h['desc']}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"h_{h['id']}_{day_str}")])

    keyboard.append([webapp_button("🌐 Web App'da to'liq ko'rish", "/")])
    keyboard.append([
        InlineKeyboardButton("📈 Ko'rsatkichlar", callback_data="stats_menu"),
        InlineKeyboardButton("🏠 Menyu", callback_data="menu"),
    ])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def toggle_habit(query, uid, data):
    parts = data.split("_", 2)
    habit_id = parts[1]
    day_str = parts[2]
    habit_day = get_habit_day(uid, day_str)

    if habit_day.get(habit_id):
        habit_day[habit_id] = False
        await query.answer(f"❌ Bekor qilindi")
    else:
        habit_day[habit_id] = True
        h = HABIT_MAP.get(habit_id, {})
        await query.answer(f"✅ {h.get('name', '')} bajarildi!")

    await send_habits(query, uid, day_str)

# =====================
# KO'RSATKICHLAR MENYUSI
# =====================
async def send_stats_menu(query, uid):
    user = get_user(uid)
    today_habits = get_habit_day(uid, today_str())
    today_pct = habit_pct(today_habits)

    text = "📈 *Ko'rsatkichlar*\n\n"
    text += f"🗓 Bugun: {mini_bar(today_pct)} *{today_pct}%*\n\n"
    text += "Batafsil ko'rish uchun tanlang:"

    keyboard = [
        [webapp_button("🌐 Web App'da batafsil ko'rish", "/weekly")],
        [InlineKeyboardButton("📅 Haftalik ko'rsatkichlar", callback_data="stats_week")],
        [InlineKeyboardButton("🗓 Oylik ko'rsatkichlar", callback_data="stats_month")],
        [InlineKeyboardButton("🏆 Odatlar reytingi", callback_data="stats_habits")],
        [InlineKeyboardButton("📊 Ingliz tili progressi", callback_data="progress")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# HAFTALIK KO'RSATKICHLAR
# =====================
async def send_weekly_stats(query, uid):
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    text = "📅 *Haftalik ko'rsatkichlar*\n"
    text += f"_Hafta: {monday.strftime('%d.%m')} – {(monday + timedelta(6)).strftime('%d.%m.%Y')}_\n\n"

    week_pcts = []
    for i in range(7):
        d = monday + timedelta(days=i)
        d_str = d.isoformat()
        day_habits = get_habit_day(uid, d_str)
        pct = habit_pct(day_habits)
        week_pcts.append(pct)
        bar = mini_bar(pct, 5)
        is_today = d == today
        marker = " ◀" if is_today else ""
        text += f"*{DAYS_SHORT[i]}* {bar} {pct}%{marker}\n"

    avg = int(sum(week_pcts) / 7) if week_pcts else 0
    best_day = DAYS_SHORT[week_pcts.index(max(week_pcts))] if week_pcts else "—"
    text += f"\n📊 O'rtacha: *{avg}%*\n"
    text += f"🏆 Eng yaxshi kun: *{best_day}*\n"

    if avg >= 80:
        text += "\n🔥 Ajoyib hafta! Siz chempionsiz!"
    elif avg >= 50:
        text += "\n💪 Yaxshi bormoqdasiz! Davom eting!"
    else:
        text += "\n🎯 Yana kuchliroq bo'lishingiz mumkin!"

    keyboard = [
        [InlineKeyboardButton("🗓 Oylik ko'rsatkichlar", callback_data="stats_month")],
        [InlineKeyboardButton("🏆 Odatlar reytingi", callback_data="stats_habits")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="stats_menu"),
         InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# OYLIK KO'RSATKICHLAR
# =====================
async def send_monthly_stats(query, uid):
    today = date.today()
    year, month = today.year, today.month
    days_in_month = monthrange(year, month)[1]

    month_names = [
        "", "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]

    text = f"🗓 *{month_names[month]} {year} — Oylik ko'rsatkichlar*\n\n"

    daily_pcts = []
    for day_num in range(1, days_in_month + 1):
        d = date(year, month, day_num)
        d_str = d.isoformat()
        day_habits = get_habit_day(uid, d_str)
        pct = habit_pct(day_habits)
        daily_pcts.append(pct)

    completed_days = sum(1 for p in daily_pcts if p >= 80)
    avg = int(sum(daily_pcts) / len(daily_pcts)) if daily_pcts else 0
    streak = _calc_streak(uid)

    text += f"📊 O'rtacha: *{avg}%*\n"
    text += f"✅ Yaxshi kunlar (≥80%): *{completed_days}/{today.day}* kun\n"
    text += f"🔥 Joriy seria: *{streak}* kun\n\n"

    text += "*Kunlik jadval:*\n"
    weeks = []
    week_row = []
    first_weekday = date(year, month, 1).weekday()
    for _ in range(first_weekday):
        week_row.append("  ")
    for day_num in range(1, days_in_month + 1):
        pct = daily_pcts[day_num - 1]
        if pct >= 80:
            icon = "🟩"
        elif pct >= 40:
            icon = "🟨"
        elif pct > 0:
            icon = "🟥"
        else:
            d = date(year, month, day_num)
            icon = "⬜" if d <= today else "░░"
        week_row.append(icon)
        if len(week_row) == 7:
            weeks.append(week_row)
            week_row = []
    if week_row:
        weeks.append(week_row)

    text += "`Du Se Ch Pa Ju Sh Ya`\n"
    for row in weeks:
        text += " ".join(row) + "\n"

    text += "\n🟩≥80% 🟨40–79% 🟥<40% ⬜0%"

    # Prev month comparison
    if month > 1:
        prev_month = month - 1
        prev_days = monthrange(year, prev_month)[1]
        prev_pcts = []
        for day_num in range(1, prev_days + 1):
            d_str = date(year, prev_month, day_num).isoformat()
            day_habits = get_habit_day(uid, d_str)
            prev_pcts.append(habit_pct(day_habits))
        prev_avg = int(sum(prev_pcts) / len(prev_pcts)) if prev_pcts else 0
        diff = avg - prev_avg
        arrow = "📈" if diff > 0 else ("📉" if diff < 0 else "➡️")
        text += f"\n\n{arrow} O'tgan oyga nisbatan: *{'+' if diff >= 0 else ''}{diff}%*"

    keyboard = [
        [InlineKeyboardButton("📅 Haftalik ko'rsatkichlar", callback_data="stats_week")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="stats_menu"),
         InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def _calc_streak(uid):
    user = get_user(uid)
    streak = 0
    d = date.today()
    while True:
        d_str = d.isoformat()
        day_habits = user["habits"].get(d_str, {})
        pct = habit_pct(day_habits)
        if pct >= 50:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak

# =====================
# ODATLAR REYTINGI
# =====================
async def send_habit_stats(query, uid):
    user = get_user(uid)
    today = date.today()
    joined_str = user.get("joined", today.isoformat())
    joined = date.fromisoformat(joined_str)
    total_days = max((today - joined).days + 1, 1)

    habit_counts = {h["id"]: 0 for h in HABITS}
    for day_str, day_habits in user["habits"].items():
        for hid in HABITS:
            if day_habits.get(hid["id"]):
                habit_counts[hid["id"]] += 1

    text = "🏆 *Odatlar reytingi*\n"
    text += f"_Kuzatilgan: {total_days} kun_\n\n"

    sorted_habits = sorted(HABITS, key=lambda h: habit_counts[h["id"]], reverse=True)
    for rank, h in enumerate(sorted_habits, 1):
        count = habit_counts[h["id"]]
        pct = int(count / total_days * 100)
        bar = mini_bar(pct, 5)
        medal = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f"{rank}."
        text += f"{medal} {h['icon']} *{h['name']}*\n"
        text += f"    {bar} {pct}% ({count}/{total_days} kun)\n"

    streak = _calc_streak(uid)
    text += f"\n🔥 *Joriy seria:* {streak} kun"

    keyboard = [
        [InlineKeyboardButton("📅 Haftalik", callback_data="stats_week"),
         InlineKeyboardButton("🗓 Oylik", callback_data="stats_month")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="stats_menu"),
         InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# MOTIVATSIYA
# =====================
async def send_motivation(query):
    mot = get_motivation()
    text = f"💫 *Motivatsiya*\n\n{mot}\n\n"
    text += "_Har kuni 2 soat — yiliga 730 soat ingliz tili! 🚀_"

    keyboard = [
        [InlineKeyboardButton("✅ Odatlarim", callback_data="habits_today"),
         InlineKeyboardButton("📈 Ko'rsatkichlar", callback_data="stats_menu")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# INGLIZ TILI PROGRESSI
# =====================
async def send_progress(query, uid):
    user = get_user(uid)
    done_count = len(user["done"])
    total = sum(len(b["tasks"]) for p in WEEK_PLAN for b in p["blocks"])
    pct = int((done_count / total) * 100) if total else 0

    bar_filled = int(pct / 10)
    bar = "🟩" * bar_filled + "⬜" * (10 - bar_filled)

    text = f"📊 *Ingliz tili — Haftalik progress*\n\n"
    text += f"{bar} {pct}%\n\n"
    text += f"✅ Bajarilgan: *{done_count}* ta\n"
    text += f"📝 Qolgan: *{total - done_count}* ta\n"
    text += f"📋 Jami: *{total}* ta topshiriq\n\n"

    if pct == 100:
        text += "🏆 AJOYIB! Hamma topshiriqni bajardingiz!"
    elif pct >= 50:
        text += "💪 Yaxshi ketayapsiz! Davom eting!"
    else:
        text += "🎯 Qani, boshlaylik! Siz qila olasiz!"

    keyboard = [
        [InlineKeyboardButton("◀️ Ko'rsatkichlar", callback_data="stats_menu"),
         InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# =====================
# ESLATMA
# =====================
async def toggle_subscribe(query, uid, context):
    user = get_user(uid)
    user["subscribed"] = not user["subscribed"]

    if user["subscribed"]:
        context.job_queue.run_daily(
            send_morning_reminder,
            time=time(hour=4, minute=25),
            chat_id=uid,
            name=f"morning_{uid}"
        )
        context.job_queue.run_daily(
            send_evening_reminder,
            time=time(hour=21, minute=0),
            chat_id=uid,
            name=f"evening_{uid}"
        )
        text = (
            "🔔 *Eslatmalar yoqildi!*\n\n"
            "⏰ *04:25* — Ertalab eslatma\n"
            "🌙 *21:00* — Kechqurun tahlil eslatmasi\n\n"
            "💪 Turing, o'qing, o'sing!"
        )
    else:
        for name in [f"morning_{uid}", f"evening_{uid}"]:
            for job in context.job_queue.get_jobs_by_name(name):
                job.schedule_removal()
        text = "🔕 *Eslatmalar o'chirildi.*\n\nQayta yoqish uchun tugmani bosing."

    keyboard = [
        [InlineKeyboardButton(
            "🔕 O'chirish" if user["subscribed"] else "🔔 Yoqish",
            callback_data="subscribe"
        )],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    mot = get_motivation()
    _, plan = get_today_plan()

    text = f"⏰ *04:30 — Vaqt keldi!*\n\n{mot}\n\n"
    text += f"📅 *Bugungi mavzu:* {plan['focus']}\n\n"
    text += "Turing, yuzingizni yuving va boshlang! 🚀"

    keyboard = [
        [InlineKeyboardButton("📅 Ingliz tili rejasi", callback_data="today")],
        [InlineKeyboardButton("✅ Odatlarni belgilash", callback_data="habits_today")],
    ]
    await context.bot.send_message(
        chat_id=chat_id, text=text,
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    uid = chat_id
    today_habits = get_habit_day(uid, today_str())
    pct = habit_pct(today_habits)
    bar = mini_bar(pct, 8)
    streak = _calc_streak(uid)

    text = f"🌙 *Kechqurun tahlil — {date.today().strftime('%d.%m.%Y')}*\n\n"
    text += f"Bugungi natija: {bar} *{pct}%*\n"
    text += f"🔥 Seria: *{streak}* kun\n\n"

    if pct == 100:
        text += "🏆 Mukammal kun! Siz g'oliblarsiz!"
    elif pct >= 60:
        text += "👍 Yaxshi kun! Ertaga yanada yaxshiroq!"
    else:
        text += "💡 Ertaga yanada kuchliroq bo'ling!\nBelgilanmagan odatlaringizni belgilang."

    keyboard = [
        [InlineKeyboardButton("✅ Odatlarni belgilash", callback_data="habits_today")],
        [InlineKeyboardButton("📈 Ko'rsatkichlar", callback_data="stats_menu")],
    ]
    await context.bot.send_message(
        chat_id=chat_id, text=text,
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# =====================
# BUYRUQLAR
# =====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Buyruqlar ro'yxati:*\n\n"
        "/start — Botni ishga tushirish\n"
        "/today — Bugungi ingliz tili rejasi\n"
        "/habits — Kunlik odatlar\n"
        "/stats — Ko'rsatkichlar\n"
        "/weekly — Haftalik reja\n"
        "/motivation — Motivatsion gap\n"
        "/help — Yordam\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    plan_idx, plan = get_today_plan()
    day_name = get_day_name()
    text = f"📅 *Bugungi reja — {day_name}*\n🎯 _{plan['focus']}_\n\n"
    for block in plan["blocks"]:
        text += f"*{block['label']}* {block['time']}\n"
        for i, task in enumerate(block["tasks"], 1):
            text += f"  {i}. {task}\n"
        text += "\n"
    keyboard = [
        [InlineKeyboardButton("✅ Topshiriqlarni belgilash", callback_data=f"tasks_{plan_idx}")],
        [InlineKeyboardButton("✅ Odatlar", callback_data="habits_today"),
         InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cmd_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    get_user(uid)
    habit_day = get_habit_day(uid, today_str())
    done_count = sum(1 for h in HABITS if habit_day.get(h["id"]))
    total = len(HABITS)
    pct = int(done_count / total * 100) if total else 0
    bar = mini_bar(pct, 8)

    text = f"✅ *Kunlik odatlar — Bugun*\n{bar} *{pct}%* ({done_count}/{total})\n\n"
    text += "Belgilash uchun /start dan foydalaning."

    keyboard = [[InlineKeyboardButton("✅ Odatlarni belgilash", callback_data="habits_today")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    get_user(uid)
    keyboard = [
        [InlineKeyboardButton("📅 Haftalik", callback_data="stats_week"),
         InlineKeyboardButton("🗓 Oylik", callback_data="stats_month")],
        [InlineKeyboardButton("🏆 Odatlar reytingi", callback_data="stats_habits")],
    ]
    await update.message.reply_text(
        "📈 *Ko'rsatkichlar*\nQuyidan tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def cmd_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💪 {get_motivation()}", parse_mode="Markdown")

# =====================
# KEEP-ALIVE SERVER (UptimeRobot uchun)
# =====================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def log_message(self, format, *args):
        pass  # ping loglarini o'chirish

def start_ping_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()

# =====================
# MAIN
# =====================
def main():
    # UptimeRobot uchun ping serverni background'da ishga tushurish
    ping_thread = threading.Thread(target=start_ping_server, daemon=True)
    ping_thread.start()
    print(f"🌐 Ping server ishga tushdi")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("habits", cmd_habits))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("motivation", cmd_motivation))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Shaxsiy Rivojlanish boti ishga tushdi!")
    print("📱 Tayyor!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
