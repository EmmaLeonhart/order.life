import json
import os

path = 'content/gaian_days.json'
with open(path, 'rb') as f:
    raw = f.read()

# Try to decode what we have
try:
    text = raw.decode('utf-8')
except:
    text = raw.decode('cp1252')

# Map specific mojibake sequences to correct Japanese
# Using hex to avoid any script encoding issues
# ã‚¢ãƒ­ãƒ©ãƒªã‚¢ -> アロラリア
text = text.replace('\u00e3\u201a\u00a2\u00e3\u0192\u00ad\u00e3\u0192\u00a9\u00e3\u0192\u00aa\u00e3\u201a\u00a2', 'アロラリア')
# æ–°å˜—ç¥­ -> 新嘗祭
text = text.replace('\u00e6\u2013\u00b0\u00e5\u02dc\u2014\u00e7\u00a5\u00ad', '新嘗祭')
# å¾©æ´»ç¥­ -> 復活祭
text = text.replace('\u00e5\u00be\u00a9\u00e6\u00b4\u00bb\u00e7\u00a5\u00ad', '復活祭')
# å…ƒæ—¦ -> 元旦
text = text.replace('\u00e5\u2026\u0083\u00e6\u2014\u00a6', '元旦')

# Generic cleanup for common patterns
text = text.replace('\u00c2\u00b7', '·')
text = text.replace('\u00e2\u20ac\u201d', '—')
text = text.replace('\u00e2\u20ac\u201c', '–')

try:
    data = json.loads(text)
    with open(path, 'w', encoding='utf-8', newline='
') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Fixed mojibake successfully.")
except Exception as e:
    print(f"JSON Parse Error: {e}")
