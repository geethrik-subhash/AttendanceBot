from datetime import datetime
from zoneinfo import ZoneInfo

from erp_automation.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TIMEZONE

import requests


def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, data=payload, timeout=20)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def _status_icon(percent_text: str) -> str:
    try:
        value = float(percent_text)
    except ValueError:
        return "⚪"

    if value >= 90:
        return "🟢"

    if value >= 75:
        return "🟡"

    return "🔴"


def build_attendance_update_message(
    overall_percent: str,
    subjects,
    no_new_classes: bool,
    class_updates,
) -> str:
    now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%d/%m/%Y %H:%M")

    lines = [
        "📊 ATTENDANCE UPDATE",
        f"🕒 {now}",
        f"📈 Overall: {overall_percent} %",
        "",
    ]

    for item in subjects:
        icon = _status_icon(item["percent"])
        lines.append(
            f"{icon} {item['subject']} {item['present']}/{item['held']} {item['percent']}%"
        )

    lines.extend(["", "====================", ""])

    if no_new_classes:
        lines.append("➖ No new classes")
    else:
        lines.append("🆕 TODAY'S CLASS UPDATES")

    if class_updates:
        lines.append("")

        for update in class_updates:
            subject = update["subject"]

            held_before = update["held_before"]
            held_after = update["held_after"]

            present_before = update["present_before"]
            present_after = update["present_after"]

            new_classes = held_after - held_before
            attended_classes = present_after - present_before

            if attended_classes == new_classes:
                icon = "🟢"
                status = "✅ Attended"
            elif attended_classes == 0:
                icon = "🔴"
                status = "❌ Absent"
            else:
                icon = "🟡"
                status = f"⚠️ Attended {attended_classes}/{new_classes}"

            lines.append(f"{icon} {subject}")
            lines.append(f"➕ New: {new_classes} | {status}")
            lines.append("")

    return "\n".join(lines)
