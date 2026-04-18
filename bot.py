import os
import socket
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
TARGET_MAC = os.environ["TARGET_MAC"]       # 예: 68:1D:EF:3F:E6:97
HOME_IP = os.environ["HOME_IP"]             # 공인IP 또는 DDNS 주소
WOL_PORT = int(os.environ.get("WOL_PORT", "9"))


def send_magic_packet(mac: str, ip: str, port: int) -> None:
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    magic = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect((ip, port))
        s.send(magic)


def is_authorized(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER_ID


async def cmd_wake(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("권한 없음")
        return
    try:
        send_magic_packet(TARGET_MAC, HOME_IP, WOL_PORT)
        await update.message.reply_text("✅ WoL 패킷 전송! 30초 후 PC가 켜집니다.")
    except Exception as e:
        await update.message.reply_text(f"❌ 오류: {e}")


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    await update.message.reply_text("WoL Bot 준비됨\n\n/wake — PC 켜기")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(CommandHandler("wake", cmd_wake))
app.run_polling()
