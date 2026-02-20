"""One-off script: add sacred_land translation keys to all i18n JSON files."""
import json
from pathlib import Path

I18N_DIR = Path(__file__).parent / "content" / "i18n"

STRINGS = {
    "en": {
        "finding": "Finding your sacred land\u2026",
        "read_fudoki": "Read local fudoki \u2192",
        "not_hallowed": "Land not yet hallowed \u00b7 browse all realms",
        "precise": "precise location",
        "getting_location": "Getting precise location\u2026",
        "denied": "Location access denied.",
        "find": "\u2295 Find your sacred land",
    },
    "ja": {
        "finding": "\u3042\u306a\u305f\u306e\u8056\u57df\u3092\u63a2\u3057\u3066\u3044\u307e\u3059\u2026",
        "read_fudoki": "\u5730\u57df\u306e\u98a8\u571f\u8a18\u3092\u8aad\u3080 \u2192",
        "not_hallowed": "\u3053\u306e\u5730\u306f\u307e\u3060\u8056\u5316\u3055\u308c\u3066\u3044\u307e\u305b\u3093 \u00b7 \u3059\u3079\u3066\u306e\u8056\u57df\u3092\u898b\u308b",
        "precise": "\u6b63\u78ba\u306a\u4f4d\u7f6e\u3092\u4f7f\u7528",
        "getting_location": "\u6b63\u78ba\u306a\u4f4d\u7f6e\u3092\u53d6\u5f97\u3057\u3066\u3044\u307e\u3059\u2026",
        "denied": "\u4f4d\u7f6e\u60c5\u5831\u3078\u306e\u30a2\u30af\u30bb\u30b9\u304c\u62d2\u5426\u3055\u308c\u307e\u3057\u305f\u3002",
        "find": "\u2295 \u3042\u306a\u305f\u306e\u8056\u57df\u3092\u63a2\u3059",
    },
    "zh": {
        "finding": "\u6b63\u5728\u5bfb\u627e\u60a8\u7684\u5723\u5730\u2026",
        "read_fudoki": "\u9605\u8bfb\u672c\u5730\u98a8\u571f\u8a18 \u2192",
        "not_hallowed": "\u6b64\u5730\u5c1a\u672a\u88ab\u795e\u5723\u5316 \u00b7 \u6d4f\u89c8\u6240\u6709\u5723\u57df",
        "precise": "\u7cbe\u786e\u5b9a\u4f4d",
        "getting_location": "\u6b63\u5728\u83b7\u53d6\u7cbe\u786e\u4f4d\u7f6e\u2026",
        "denied": "\u4f4d\u7f6e\u8bbf\u95ee\u88ab\u62d2\u7edd\u3002",
        "find": "\u2295 \u5bfb\u627e\u60a8\u7684\u5723\u5730",
    },
    "es": {
        "finding": "Encontrando tu tierra sagrada\u2026",
        "read_fudoki": "Leer fudoki local \u2192",
        "not_hallowed": "Tierra a\u00fan no consagrada \u00b7 explorar todos los reinos",
        "precise": "ubicaci\u00f3n precisa",
        "getting_location": "Obteniendo ubicaci\u00f3n precisa\u2026",
        "denied": "Acceso a ubicaci\u00f3n denegado.",
        "find": "\u2295 Encontrar tu tierra sagrada",
    },
    "hi": {
        "finding": "\u0906\u092a\u0915\u0940 \u092a\u0935\u093f\u0924\u094d\u0930 \u092d\u0942\u092e\u093f \u0916\u094b\u091c\u0940 \u091c\u093e \u0930\u0939\u0940 \u0939\u0948\u2026",
        "read_fudoki": "\u0938\u094d\u0925\u093e\u0928\u0940\u092f \u092b\u093c\u0941\u0926\u094b\u0915\u093f \u092a\u095d\u0947\u0902 \u2192",
        "not_hallowed": "\u092f\u0939 \u092d\u0942\u092e\u093f \u0905\u092d\u0940 \u092a\u0935\u093f\u0924\u094d\u0930 \u0928\u0939\u0940\u0902 \u0915\u0940 \u0917\u0908 \u00b7 \u0938\u092d\u0940 \u0930\u093e\u091c\u094d\u092f \u0926\u0947\u0916\u0947\u0902",
        "precise": "\u0938\u091f\u0940\u0915 \u0938\u094d\u0925\u093e\u0928",
        "getting_location": "\u0938\u091f\u0940\u0915 \u0938\u094d\u0925\u093e\u0928 \u092a\u094d\u0930\u093e\u092a\u094d\u0924 \u0915\u093f\u092f\u093e \u091c\u093e \u0930\u0939\u093e \u0939\u0948\u2026",
        "denied": "\u0938\u094d\u0925\u093e\u0928 \u092a\u0939\u0941\u0901\u091a \u0905\u0938\u094d\u0935\u0940\u0915\u0943\u0924\u0964",
        "find": "\u2295 \u0905\u092a\u0928\u0940 \u092a\u0935\u093f\u0924\u094d\u0930 \u092d\u0942\u092e\u093f \u0916\u094b\u091c\u0947\u0902",
    },
    "ar": {
        "finding": "\u062c\u0627\u0631\u064d \u0627\u0644\u0628\u062d\u062b \u0639\u0646 \u0623\u0631\u0636\u0643 \u0627\u0644\u0645\u0642\u062f\u0633\u0629\u2026",
        "read_fudoki": "\u2190 \u0627\u0642\u0631\u0623 \u0627\u0644\u0641\u0648\u062f\u0648\u0643\u064a \u0627\u0644\u0645\u062d\u0644\u064a",
        "not_hallowed": "\u0647\u0630\u0647 \u0627\u0644\u0623\u0631\u0636 \u0644\u0645 \u062a\u064f\u0642\u062f\u0651\u0633 \u0628\u0639\u062f \u00b7 \u062a\u0635\u0641\u062d \u062c\u0645\u064a\u0639 \u0627\u0644\u0623\u0631\u0627\u0636\u064a",
        "precise": "\u0627\u0644\u0645\u0648\u0642\u0639 \u0627\u0644\u062f\u0642\u064a\u0642",
        "getting_location": "\u062c\u0627\u0631\u064d \u0627\u0644\u062d\u0635\u0648\u0644 \u0639\u0644\u0649 \u0627\u0644\u0645\u0648\u0642\u0639 \u0627\u0644\u062f\u0642\u064a\u0642\u2026",
        "denied": "\u062a\u0645 \u0631\u0641\u0636 \u0627\u0644\u0648\u0635\u0648\u0644 \u0625\u0644\u0649 \u0627\u0644\u0645\u0648\u0642\u0639.",
        "find": "\u2295 \u0627\u0628\u062d\u062b \u0639\u0646 \u0623\u0631\u0636\u0643 \u0627\u0644\u0645\u0642\u062f\u0633\u0629",
    },
    "fr": {
        "finding": "Recherche de votre terre sacr\u00e9e\u2026",
        "read_fudoki": "Lire le fudoki local \u2192",
        "not_hallowed": "Terre pas encore consacr\u00e9e \u00b7 parcourir tous les royaumes",
        "precise": "localisation pr\u00e9cise",
        "getting_location": "Obtention de la localisation pr\u00e9cise\u2026",
        "denied": "Acc\u00e8s \u00e0 la localisation refus\u00e9.",
        "find": "\u2295 Trouver votre terre sacr\u00e9e",
    },
    "ru": {
        "finding": "\u041f\u043e\u0438\u0441\u043a \u0432\u0430\u0448\u0435\u0439 \u0441\u0432\u044f\u0449\u0435\u043d\u043d\u043e\u0439 \u0437\u0435\u043c\u043b\u0438\u2026",
        "read_fudoki": "\u0427\u0438\u0442\u0430\u0442\u044c \u043c\u0435\u0441\u0442\u043d\u044b\u0439 \u0444\u0443\u0434\u043e\u043a\u0438 \u2192",
        "not_hallowed": "\u042d\u0442\u0430 \u0437\u0435\u043c\u043b\u044f \u0435\u0449\u0451 \u043d\u0435 \u043e\u0441\u0432\u044f\u0449\u0435\u043d\u0430 \u00b7 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0432\u0441\u0435 \u0437\u0435\u043c\u043b\u0438",
        "precise": "\u0442\u043e\u0447\u043d\u043e\u0435 \u043c\u0435\u0441\u0442\u043e\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435",
        "getting_location": "\u041f\u043e\u043b\u0443\u0447\u0435\u043d\u0438\u0435 \u0442\u043e\u0447\u043d\u043e\u0433\u043e \u043c\u0435\u0441\u0442\u043e\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u044f\u2026",
        "denied": "\u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0433\u0435\u043e\u043b\u043e\u043a\u0430\u0446\u0438\u0438 \u0437\u0430\u043f\u0440\u0435\u0449\u0451\u043d.",
        "find": "\u2295 \u041d\u0430\u0439\u0442\u0438 \u0432\u0430\u0448\u0443 \u0441\u0432\u044f\u0449\u0435\u043d\u043d\u0443\u044e \u0437\u0435\u043c\u043b\u044e",
    },
    "uk": {
        "finding": "\u041f\u043e\u0448\u0443\u043a \u0432\u0430\u0448\u043e\u0457 \u0441\u0432\u044f\u0449\u0435\u043d\u043d\u043e\u0457 \u0437\u0435\u043c\u043b\u0456\u2026",
        "read_fudoki": "\u0427\u0438\u0442\u0430\u0442\u0438 \u043c\u0456\u0441\u0446\u0435\u0432\u0438\u0439 \u0444\u0443\u0434\u043e\u043a\u0456 \u2192",
        "not_hallowed": "\u0426\u044f \u0437\u0435\u043c\u043b\u044f \u0449\u0435 \u043d\u0435 \u043e\u0441\u0432\u044f\u0447\u0435\u043d\u0430 \u00b7 \u043f\u0435\u0440\u0435\u0433\u043b\u044f\u043d\u0443\u0442\u0438 \u0432\u0441\u0456 \u0437\u0435\u043c\u043b\u0456",
        "precise": "\u0442\u043e\u0447\u043d\u0435 \u043c\u0456\u0441\u0446\u0435\u0437\u043d\u0430\u0445\u043e\u0434\u0436\u0435\u043d\u043d\u044f",
        "getting_location": "\u041e\u0442\u0440\u0438\u043c\u0430\u043d\u043d\u044f \u0442\u043e\u0447\u043d\u043e\u0433\u043e \u043c\u0456\u0441\u0446\u0435\u0437\u043d\u0430\u0445\u043e\u0434\u0436\u0435\u043d\u043d\u044f\u2026",
        "denied": "\u0414\u043e\u0441\u0442\u0443\u043f \u0434\u043e \u0433\u0435\u043e\u043b\u043e\u043a\u0430\u0446\u0456\u0457 \u0437\u0430\u0431\u043e\u0440\u043e\u043d\u0435\u043d\u043e.",
        "find": "\u2295 \u0417\u043d\u0430\u0439\u0442\u0438 \u0432\u0430\u0448\u0443 \u0441\u0432\u044f\u0449\u0435\u043d\u043d\u0443 \u0437\u0435\u043c\u043b\u044e",
    },
    "de": {
        "finding": "Ihre heilige Erde wird gesucht\u2026",
        "read_fudoki": "Lokales Fudoki lesen \u2192",
        "not_hallowed": "Dieses Land ist noch nicht geheiligt \u00b7 alle Reiche durchsuchen",
        "precise": "genauen Standort",
        "getting_location": "Genauen Standort wird ermittelt\u2026",
        "denied": "Standortzugriff verweigert.",
        "find": "\u2295 Ihre heilige Erde finden",
    },
    "he": {
        "finding": "\u05de\u05d7\u05e4\u05e9 \u05d0\u05ea \u05d0\u05d3\u05de\u05ea\u05da \u05d4\u05e7\u05d3\u05d5\u05e9\u05d4\u2026",
        "read_fudoki": "\u2190 \u05e7\u05e8\u05d0 \u05d0\u05ea \u05d4\u05e4\u05d5\u05d3\u05d5\u05e7\u05d9 \u05d4\u05de\u05e7\u05d5\u05de\u05d9",
        "not_hallowed": "\u05d0\u05d3\u05de\u05d4 \u05d6\u05d5 \u05d8\u05e8\u05dd \u05e7\u05d5\u05d3\u05e9\u05d4 \u00b7 \u05e2\u05d9\u05d9\u05df \u05d1\u05db\u05dc \u05d4\u05de\u05de\u05dc\u05db\u05d5\u05ea",
        "precise": "\u05de\u05d9\u05e7\u05d5\u05dd \u05de\u05d3\u05d5\u05d9\u05e7",
        "getting_location": "\u05de\u05e7\u05d1\u05dc \u05de\u05d9\u05e7\u05d5\u05dd \u05de\u05d3\u05d5\u05d9\u05e7\u2026",
        "denied": "\u05d4\u05d2\u05d9\u05e9\u05d4 \u05dc\u05de\u05d9\u05e7\u05d5\u05dd \u05e0\u05d3\u05d7\u05ea\u05d4.",
        "find": "\u2295 \u05de\u05e6\u05d0 \u05d0\u05ea \u05d0\u05d3\u05de\u05ea\u05da \u05d4\u05e7\u05d3\u05d5\u05e9\u05d4",
    },
    "pt": {
        "finding": "Encontrando sua terra sagrada\u2026",
        "read_fudoki": "Ler fudoki local \u2192",
        "not_hallowed": "Terra ainda n\u00e3o consagrada \u00b7 explorar todos os reinos",
        "precise": "localiza\u00e7\u00e3o precisa",
        "getting_location": "Obtendo localiza\u00e7\u00e3o precisa\u2026",
        "denied": "Acesso \u00e0 localiza\u00e7\u00e3o negado.",
        "find": "\u2295 Encontrar sua terra sagrada",
    },
}

updated = []
for lang_file in sorted(I18N_DIR.glob("*.json")):
    lang = lang_file.stem
    if lang not in STRINGS:
        print(f"  Skipping {lang} (no translations defined)")
        continue
    data = json.loads(lang_file.read_text(encoding="utf-8"))
    data["sacred_land"] = STRINGS[lang]
    lang_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    updated.append(lang)
    print(f"  Updated {lang}.json")

print(f"\nDone. Updated {len(updated)} files.")
