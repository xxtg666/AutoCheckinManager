TG_HEADER = '<b>自动签到通知</b>\n<b>{datetime}</b>'
TG_USER = '\n\n━━━━━━━━━━━━━━━━\n<b>{user}</b>'
TG_SERVICE = '\n\n<b>· {service}</b>\n<blockquote>{output}</blockquote>'


def _escapeHtml(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def genTelegramMessage(datetime_str, content):
    return TG_HEADER.replace('{datetime}', _escapeHtml(datetime_str)) + content


def genTelegramUser(user):
    return TG_USER.replace('{user}', _escapeHtml(user))


def genTelegramService(service, output):
    output = _escapeHtml(output).strip() or '(无输出)'
    return TG_SERVICE.replace('{service}', _escapeHtml(service)).replace('{output}', output)
