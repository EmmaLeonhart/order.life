import json
file_path = 'content/gaian_days.json'
try:
    with open(file_path, 'rb') as f:
        content_bytes = f.read()
    text = content_bytes.decode('utf-8-sig')
    replacements = {
        'ã‚¢ãƒ­ãƒ©ãƒªã‚¢': 'アロラリア',
        'ã‚¹ãƒãƒ¼ãƒ„ã®æ—¥ãƒ»ã‚«ãƒŠãƒ€æ„Ÿè¬ç¥­': 'スポーツの日・カナダ感謝祭',
        'æ–°å˜—ç¥­': '新嘗祭',
        'æˆäººã®æ—¥': '成人の日',
        'å…ƒæ—¦ï¼ˆã‚¢ã‚¹ã‚¿ãƒ¼æ—¥ï¼‰': '元旦（アスター日）',
        'å¾©æ´»ç¥­': '復活祭',
        'ä¸­å…ƒç¯€': '中元節',
        'ç›‚è˜­ç›†ä¼š': '盂蘭盆会',
        'ä¸­ç§‹ç¯€': '中秋節',
        'ç¥žæ®¿ç¥­': '神殿祭',
        'ã‚¯ãƒªã‚¹ãƒžã‚¹ãƒ»å†¬è‡³': 'クリスマス・冬至'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    data = json.loads(text)
    with open(file_path, 'w', encoding='utf-8', newline='
') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Fixed mojibake.")
except Exception as e:
    print(f"Error: {e}")
