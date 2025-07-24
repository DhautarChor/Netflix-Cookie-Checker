# bot.py

import json
import os
import random
import asyncio
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
from checker import check_cookie, parse_cookie
from datetime import datetime

# === CONFIG ===
CONFIG_FILE = "config.json"
USERS_FILE = "users.json"
CODES_FILE = "codes.json"
VALID_FILE = "valid.txt"
LOG_FILE = "logs.txt"
RATE_LIMIT = 5

# === BOT TOKEN ===
BOT_TOKEN = "YOUR_BOT_TOKEN"

# === Ensure required files ===
for file, default in [
    (USERS_FILE, {}),
    (CODES_FILE, {}),
    (CONFIG_FILE, {"admins": ["YOUR_USER_ID"]})
]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)

def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# === AUTH ===
def is_admin(user_id):
    config = load_json(CONFIG_FILE)
    return str(user_id) in config.get("admins", [])

def is_authorized(user_id):
    users = load_json(USERS_FILE)
    return str(user_id) in users

# === COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🔒 Send your redeem code using /redeem <code>")
    else:
        await update.message.reply_text("✅ You are authorized. Send your Netflix cookie file (.txt) now.")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /redeem <code>")
        return

    code = args[0]
    codes = load_json(CODES_FILE)
    users = load_json(USERS_FILE)

    if code in codes:
        user_id = str(update.effective_user.id)
        users[user_id] = {"redeemed": code}
        save_json(USERS_FILE, users)
        codes.pop(code)
        save_json(CODES_FILE, codes)
        await update.message.reply_text("✅ Code accepted! Send your .txt cookie file now.")
        log(f"[REDEEM] User {user_id} used code {code}")
    else:
        await update.message.reply_text("❌ Invalid or already used code.")

# === ADMIN COMMANDS ===
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admins only.")
        return

    count = int(context.args[0]) if context.args else 1
    codes = load_json(CODES_FILE)

    new_codes = []
    for _ in range(count):
        code = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=10))
        codes[code] = {"generated_by": update.effective_user.id}
        new_codes.append(code)

    save_json(CODES_FILE, codes)
    await update.message.reply_text("🎟️ Generated codes:\n" + "\n".join(new_codes))
    log(f"[ADMIN] Generated {count} codes by {update.effective_user.id}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = load_json(USERS_FILE)
    codes = load_json(CODES_FILE)
    await update.message.reply_text(
        f"👤 Users: {len(users)}\n🎟️ Codes remaining: {len(codes)}"
    )

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = load_json(USERS_FILE)
    msg = "\n".join([f"{uid} -> {info['redeemed']}" for uid, info in users.items()])
    await update.message.reply_text(msg or "No users.")

async def codes_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    codes = load_json(CODES_FILE)
    await update.message.reply_text("\n".join(codes.keys()) or "No codes left.")

# === COOKIE FILE HANDLER ===
async def handle_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You're not authorized. Use /redeem <code>")
        return

    doc: Document = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❗ Please send a .txt file only.")
        return

    path = f"cookies/{user_id}.txt"
    os.makedirs("cookies", exist_ok=True)
    await doc.get_file().download_to_drive(path)
    await update.message.reply_text("⏳ Checking your cookies...")

    valid_count = 0
    total_checked = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if total_checked >= RATE_LIMIT:
                break
            cookie = parse_cookie(line.strip())
            if not cookie:
                continue
            if check_cookie(cookie):
                valid_count += 1
                with open(VALID_FILE, "a") as v:
                    v.write(line.strip() + "\n")
            total_checked += 1
            await asyncio.sleep(1)

    await update.message.reply_text(f"✅ Checked {total_checked} cookies.\n🟩 Valid: {valid_count}\n❌ Invalid: {total_checked - valid_count}")
    log(f"[CHECK] {user_id} checked {total_checked} cookies, {valid_count} valid.")

# === MAIN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("codes", codes_list))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("txt"), handle_doc))

    print("✅ Bot is running...")
    app.run_polling()
