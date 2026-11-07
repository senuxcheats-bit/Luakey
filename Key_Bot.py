# bot_key_manager.py
import json
import os
import datetime
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

# ==================== KONFIGURASI ====================
TOKEN = "9085193011:AAEnEog3AtVWvAZWRNAUqh3kRnhexRYDcSI"
ADMIN_IDS = [7772844841]  # ID Telegram admin
CONFIG_FILE = "keylist.json"
KEY_FILE_URL = "https://your-server.com/keylist.json"  # Link publik file

# ==================== FUNGSI BACA/TULIS ====================
def load_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(CONFIG_FILE, "w") as f:
        json.dump(keys, f, indent=2)

# ==================== GENERATE KEY ====================
def generate_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

# ==================== HANDLER PERINTAH ====================
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 *Key Manager Bot*\n\n"
        "Perintah untuk admin:\n"
        "/addkey <key> <hari> - Tambah key\n"
        "/genkey <hari> - Generate key otomatis\n"
        "/delkey <key> - Hapus key\n"
        "/listkeys - Lihat semua key\n"
        "/ban <key> - Ban key\n"
        "/unban <key> - Unban key\n"
        "/getconfig - Dapatkan link download config\n\n"
        "Format key: KEY|DEVICE_ID (opsional binding device)",
        parse_mode="Markdown"
    )

async def addkey(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ Gunakan: /addkey <KEY> <HARI>")
        return
    
    key = args[0].upper()
    days = int(args[1])
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
    
    keys = load_keys()
    if key in keys:
        await update.message.reply_text(f"❌ Key `{key}` sudah ada!", parse_mode="Markdown")
        return
    
    keys[key] = {
        "expiry": expiry,
        "active": True,
        "device": None,  # akan diisi saat binding
        "created": datetime.datetime.now().isoformat()
    }
    save_keys(keys)
    await update.message.reply_text(f"✅ Key `{key}` berhasil ditambahkan! Expiry: {expiry}", parse_mode="Markdown")

async def genkey(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❌ Gunakan: /genkey <HARI>")
        return
    
    days = int(args[0])
    key = generate_key(12)
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
    
    keys = load_keys()
    keys[key] = {
        "expiry": expiry,
        "active": True,
        "device": None,
        "created": datetime.datetime.now().isoformat()
    }
    save_keys(keys)
    await update.message.reply_text(f"✅ Key baru: `{key}`\nExpiry: {expiry}\nDurasi: {days} hari", parse_mode="Markdown")

async def delkey(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❌ Gunakan: /delkey <KEY>")
        return
    
    key = args[0].upper()
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text(f"❌ Key `{key}` tidak ditemukan!", parse_mode="Markdown")
        return
    
    del keys[key]
    save_keys(keys)
    await update.message.reply_text(f"✅ Key `{key}` berhasil dihapus!", parse_mode="Markdown")

async def listkeys(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    keys = load_keys()
    if not keys:
        await update.message.reply_text("📭 Belum ada key.")
        return
    
    msg = "📋 *Daftar Key*\n\n"
    for k, v in keys.items():
        status = "✅ Aktif" if v["active"] else "❌ Diblokir"
        device = v["device"] or "Belum terikat"
        msg += f"`{k}`\n  Status: {status}\n  Expiry: {v['expiry']}\n  Device: {device}\n\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ban(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❌ Gunakan: /ban <KEY>")
        return
    
    key = args[0].upper()
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text(f"❌ Key `{key}` tidak ditemukan!", parse_mode="Markdown")
        return
    
    keys[key]["active"] = False
    save_keys(keys)
    await update.message.reply_text(f"🚫 Key `{key}` berhasil diblokir!", parse_mode="Markdown")

async def unban(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❌ Gunakan: /unban <KEY>")
        return
    
    key = args[0].upper()
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text(f"❌ Key `{key}` tidak ditemukan!", parse_mode="Markdown")
        return
    
    keys[key]["active"] = True
    save_keys(keys)
    await update.message.reply_text(f"✅ Key `{key}` berhasil diaktifkan!", parse_mode="Markdown")

async def getconfig(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    
    await update.message.reply_text(
        f"📥 *Download konfigurasi key terbaru:*\n{KEY_FILE_URL}\n\n"
        "Simpan file ke folder:\n"
        "`/storage/emulated/0/Android/data/com.tencent.ig/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks/keylist.json`",
        parse_mode="Markdown"
    )

# ==================== MAIN ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addkey", addkey))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("delkey", delkey))
    app.add_handler(CommandHandler("listkeys", listkeys))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("getconfig", getconfig))
    
    print("🤖 Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()