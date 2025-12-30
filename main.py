import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from stats_logger import log_search, get_stats, log_snapshot
from config import Config
from apis.freesound_api import FreeSoundAPI

# ================= ADMIN =================
ADMIN_ID = 5954057500

# ================= LOGGING SETUP =================
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/audix.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AudixBot")

# ================= INIT =================
freesound = FreeSoundAPI(Config.FREESOUND_API_KEY)

CACHE = {}
PAGE_SIZE = 5


def get_user_id(update: Update):
    return update.effective_user.id


# ================= SNAPSHOT LOOP =================
async def snapshot_loop():
    while True:
        try:
            log_snapshot()
            logger.info("📸 Snapshot saved")
        except Exception as e:
            logger.error("Snapshot error", exc_info=e)

        await asyncio.sleep(300)  # 5 minutes


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "there"
    logger.info(f"/start by {user_name}")

    await update.message.reply_text(
        f"Hey {user_name} 👋\n\n"
        "Welcome to *Audix* 🎧\n\n"
        "Find **high-quality sound effects** fast ⚡ and clean ✨\n\n"
        "What you can do 👇\n"
        "🎵 Search pro sound effects\n"
        "▶️ Preview audio instantly\n"
        "🔗 Download from original source\n\n"
        "Try searching like:\n"
        "• whoosh transition\n"
        "• cinematic background\n"
        "• mouse click sound\n\n"
        "Quality over quantity 🎯\n\n"
        "_Made by Yassu ❤️_",
        parse_mode="Markdown"
    )


# ================= HELP =================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *How to use Audix*\n\n"
        "1️⃣ Type the sound you need\n"
        "2️⃣ Tap ▶️ Preview\n"
        "3️⃣ Open Source 🔗 to download\n\n"
        "💡 Tips:\n"
        "• Keep keywords simple\n"
        "• Try different words\n"
        "• Preview before download\n\n"
        "Audix focuses on quality ✨",
        parse_mode="Markdown"
    )


# ================= ABOUT =================
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 *Audix — Sound Finder Bot*\n\n"
        "Find clean, usable sound effects without wasting time.\n\n"
        "Useful for:\n"
        "• Content creators\n"
        "• Video editors\n"
        "• Developers\n\n"
        "📢 Updates & tools:\n"
        "@yassu_tech_tools\n\n"
        "🤖 Bot:\n"
        "@audixsound_bot\n\n"
        "_Created by Yassu_",
        )


# ================= MESSAGE HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    user_id = get_user_id(update)

    logger.info(f"Search from {user_id}: {user_text}")

    user_name = update.effective_user.first_name or "Unknown"
    log_search(user_id, user_name, user_text.lower())

    if len(user_text) < 3:
        await update.message.reply_text(
            "✍️ Please add more detail.\n"
            "Example: `button click`, `cinematic whoosh`",
            parse_mode="Markdown"
        )
        return

    loading_msg = await update.message.reply_text(
        "🔍 Searching best quality sounds…\n"
        "Please wait ⏳"
    )

    try:
        results = await freesound.search(user_text)

        if not results:
            await loading_msg.edit_text(
                "😕 No good results found.\n\n"
                "Try simpler keywords like:\n"
                "`click`, `impact`, `transition`",
                parse_mode="Markdown"
            )
            return

        CACHE[user_id] = {"results": results, "page": 0}
        await show_page(loading_msg, user_id)

    except Exception as e:
        logger.error("Search error", exc_info=e)
        await loading_msg.edit_text(
            "❌ Something went wrong.\n"
            "Please try again later."
        )


# ================= SHOW RESULTS =================
async def show_page(message, user_id):
    data = CACHE.get(user_id)
    if not data:
        return

    results = data["results"]
    page = data["page"]

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = results[start:end]

    text = "🎧 *Search Results*\n\n"

    buttons = []

    for index, sound in enumerate(page_items):
        global_index = start + index

        text += f"🎵 *{sound.title}*\n🌐 {sound.source}\n\n"

        buttons.append([
            InlineKeyboardButton("▶️ Preview", callback_data=f"preview_{global_index}"),
            InlineKeyboardButton("🔗 Open Source", url=sound.page_url)
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data="prev"))
    if end < len(results):
        nav.append(InlineKeyboardButton("Next ➡️", callback_data="next"))

    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("🔄 New Search", callback_data="new")])

    await message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACKS =================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = get_user_id(update)
    data = query.data

    try:
        if data == "next":
            CACHE[user_id]["page"] += 1
            await show_page(query.message, user_id)

        elif data == "prev":
            CACHE[user_id]["page"] -= 1
            await show_page(query.message, user_id)

        elif data == "new":
            await query.message.edit_text("✍️ Type a new sound to search")

        elif data.startswith("preview_"):
            index = int(data.split("_")[1])
            sound = CACHE[user_id]["results"][index]

            try:
                await query.message.reply_audio(
                    audio=sound.preview_url,
                    title=sound.title,
                    caption="🎧 Preview\nSave directly from Telegram 📥",
                    connect_timeout=30,
                    read_timeout=30,
                    write_timeout=30
                )
            except Exception:
                await query.message.reply_text(
                    "⏳ Preview slow.\n"
                    f"Open source instead 🔗\n{sound.page_url}"
                )

    except Exception as e:
        logger.error("Callback error", exc_info=e)


# ================= STATS =================
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    active_users, keywords = get_stats(24)

    text = f"📊 *Audix Stats (24h)*\n\n👥 Active users: {active_users}\n\n"

    if not keywords:
        text += "No searches yet."
    else:
        for k, v in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]:
            text += f"• {k} → {v}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# ================= ERROR HANDLER =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled error", exc_info=context.error)


# ================= STARTUP HOOK =================
async def on_startup(app: Application):
    app.create_task(snapshot_loop())
    logger.info("📸 Snapshot loop started (every 5 minutes)")


# ================= MAIN =================
def main():
    app = (
        Application.builder()
        .token(Config.TELEGRAM_TOKEN)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("stats", stats_cmd))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_error_handler(error_handler)

    logger.info("🚀 Audix Bot started successfully")
    app.run_polling()


if __name__ == "__main__":
    main()