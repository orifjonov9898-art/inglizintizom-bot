import logging
import asyncio
import threading
from datetime import datetime, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# =====================
# KEEP ALIVE (Replit uchun)
# =====================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")
    def log_message(self, format, *args):
        pass

def keep_alive():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print("✅ Keep-alive server ishga tushdi!")

# =====================
# TOKEN
# =====================
TOKEN = "8617890120:AAHtbC7tSfqC5MiMWPNZPv9nGJBY5yb63Vo"

# =====================
# LOGGING
# =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================
# MA'LUMOTLAR
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
]

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

# Foydalanuvchi ma'lumotlari (xotirada saqlanadi)
user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"done": set(), "chat_id": user_id, "subscribed": False}
    return user_data[user_id]

def get_today_plan():
    day_idx = datetime.now().weekday()  # 0=Monday
    # Dushanba=0 -> plan index 1, etc.
    plan_idx = day_idx % 7
    return plan_idx, WEEK_PLAN[plan_idx]

def get_motivation():
    idx = datetime.now().day % len(MOTIVATIONS)
    return MOTIVATIONS[idx]

# =====================
# HANDLERS
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    get_user(uid)

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi reja", callback_data="today")],
        [InlineKeyboardButton("📊 Haftalik reja", callback_data="weekly")],
        [InlineKeyboardButton("💪 Motivatsiya", callback_data="motivation")],
        [InlineKeyboardButton("✅ Bajarilganlar", callback_data="progress")],
        [InlineKeyboardButton("🔔 Kunlik eslatma", callback_data="subscribe")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Salom, {user.first_name}! 👋\n\n"
        "🎓 *Ingliz Intizom Bot*ga xush kelibsiz!\n\n"
        "Men sizga har kuni 04:30 da ingliz tili darsiga tayyorlanishga yordam beraman.\n\n"
        "Quyidan tanlang 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data == "today":
        await send_today(query)
    elif data == "weekly":
        await send_weekly(query)
    elif data == "motivation":
        await send_motivation(query)
    elif data == "progress":
        await send_progress(query, uid)
    elif data == "subscribe":
        await toggle_subscribe(query, uid, context)
    elif data == "menu":
        await send_menu(query)
    elif data.startswith("done_"):
        await toggle_done(query, uid, data)

async def send_menu(query):
    keyboard = [
        [InlineKeyboardButton("📅 Bugungi reja", callback_data="today")],
        [InlineKeyboardButton("📊 Haftalik reja", callback_data="weekly")],
        [InlineKeyboardButton("💪 Motivatsiya", callback_data="motivation")],
        [InlineKeyboardButton("✅ Bajarilganlar", callback_data="progress")],
        [InlineKeyboardButton("🔔 Kunlik eslatma", callback_data="subscribe")],
    ]
    await query.edit_message_text(
        "🏠 *Asosiy menyu*\n\nNimani ko'rmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def send_today(query):
    plan_idx, plan = get_today_plan()
    day_name = DAYS_UZ[datetime.now().weekday() + 1 if datetime.now().weekday() < 6 else 0]
    
    text = f"📅 *Bugungi reja — {day_name}*\n"
    text += f"🎯 Mavzu: _{plan['focus']}_\n"
    text += f"⏰ Vaqt: 04:30 – 06:30\n\n"
    
    for block in plan["blocks"]:
        text += f"*{block['label']}* `{block['time']}`\n"
        for i, task in enumerate(block["tasks"], 1):
            text += f"  {i}. {task}\n"
        text += "\n"

    keyboard = [
        [InlineKeyboardButton("✅ Topshiriqlarni belgilash", callback_data=f"done_today_{plan_idx}")],
        [InlineKeyboardButton("💪 Motivatsiya", callback_data="motivation")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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

async def send_motivation(query):
    mot = get_motivation()
    text = f"💫 *Motivatsiya*\n\n{mot}\n\n"
    text += "_Har kuni 2 soat — yiliga 730 soat ingliz tili! 🚀_"

    keyboard = [[InlineKeyboardButton("🏠 Menyu", callback_data="menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def send_progress(query, uid):
    user = get_user(uid)
    done_count = len(user["done"])
    total = sum(len(b["tasks"]) for p in WEEK_PLAN for b in p["blocks"])
    pct = int((done_count / total) * 100) if total else 0
    
    bar_filled = int(pct / 10)
    bar = "🟩" * bar_filled + "⬜" * (10 - bar_filled)
    
    text = f"📊 *Haftalik progress*\n\n"
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

    keyboard = [[InlineKeyboardButton("🏠 Menyu", callback_data="menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def toggle_done(query, uid, data):
    user = get_user(uid)
    # Simple done toggle
    key = data
    if key in user["done"]:
        user["done"].remove(key)
        await query.answer("❌ Bekor qilindi")
    else:
        user["done"].add(key)
        await query.answer("✅ Bajarildi!")

async def toggle_subscribe(query, uid, context):
    user = get_user(uid)
    user["subscribed"] = not user["subscribed"]
    
    if user["subscribed"]:
        # Schedule daily job at 04:25
        context.job_queue.run_daily(
            send_morning_reminder,
            time=time(hour=4, minute=25),
            chat_id=uid,
            name=f"morning_{uid}"
        )
        text = "🔔 *Kunlik eslatma yoqildi!*\n\nHar kuni *04:25* da sizga eslatma yuboraman!\n\n💪 Turing va o'qing!"
    else:
        # Remove job
        jobs = context.job_queue.get_jobs_by_name(f"morning_{uid}")
        for job in jobs:
            job.schedule_removal()
        text = "🔕 *Kunlik eslatma o'chirildi.*\n\nQayta yoqish uchun tugmani bosing."

    keyboard = [
        [InlineKeyboardButton(
            "🔕 Eslatmani o'chirish" if user["subscribed"] else "🔔 Eslatmani yoqish",
            callback_data="subscribe"
        )],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    mot = get_motivation()
    plan_idx, plan = get_today_plan()
    
    text = f"⏰ *04:30 — Vaqt keldi!*\n\n"
    text += f"{mot}\n\n"
    text += f"📅 *Bugungi mavzu:* {plan['focus']}\n\n"
    text += "Turing, yuzingizni yuving va boshlang! 🚀"

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi reja", callback_data="today")],
        [InlineKeyboardButton("💪 Yana motivatsiya", callback_data="motivation")],
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Buyruqlar ro'yxati:*\n\n"
        "/start — Botni ishga tushirish\n"
        "/today — Bugungi reja\n"
        "/weekly — Haftalik reja\n"
        "/motivation — Motivatsion gap\n"
        "/progress — Progressim\n"
        "/help — Yordam\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan_idx, plan = get_today_plan()
    day_name = DAYS_UZ[datetime.now().weekday() + 1 if datetime.now().weekday() < 6 else 0]
    text = f"📅 *Bugungi reja — {day_name}*\n🎯 _{plan['focus']}_\n\n"
    for block in plan["blocks"]:
        text += f"*{block['label']}* `{block['time']}`\n"
        for i, task in enumerate(block["tasks"], 1):
            text += f"  {i}. {task}\n"
        text += "\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💪 {get_motivation()}", parse_mode="Markdown")

# =====================
# MAIN
# =====================
def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("motivation", cmd_motivation))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ InglizIntizom bot ishga tushdi!")
    print("📱 @InglizIntizom_bot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

                
        
