"""
Neo-kun'yomi: one kanji form per Abrahamic or Christian name root, read as the person's own name.

The table of planning/neo-kunyomi-names.md, approved by Emma 2026-10-15 ("Apply as drafted"). Her rule: "all
versions of John are the same, all versions of David are the same"; the kanji carry the root's meaning, the
reading is the person's own name (George = 地働, read George; Iván = 神恵, read Iván).

    kanji_for("Giovanni") -> "神恵"
"""
import re

ROOTS = {
    "神恵": "john|johann|johannes|juan|jean|giovanni|ivan|iván|joao|joão|jan|hans|yahya|yohannes|iohannes|ioannes|jehan|sean|seán|ian|evan|ifan",
    "愛": "mary|maria|marie|miriam|maryam|mariam|marija|maría",
    "岩": "peter|pedro|pierre|pietro|petrus|piotr|pyotr|petr",
    "神誓": "elizabeth|isabel|isabella|elisabeth|elisabetta|isabeau|elisabet",
    "讃": "muhammad|mohammed|mohammad|mehmed|ahmad|ahmed",
    "寵": "david|dawud|daud|davit|dafydd",
    "恵": "anne|anna|ana|hannah|ann",
    "由": "francis|francisco|francesco|francois|françois|franz",
    "踵": "jacob|james|jacques|jakob|jaime|diego|giacomo|yaqub|iago|santiago|jacopo|jakub",
    "珠": "margaret|margarita|margarida|margherita|marguerite|margarethe",
    "双": "thomas|tomas|tomás|tommaso",
    "高": "ali",
    "純": "catherine|catalina|caterina|katharina|katarina|ekaterina",
    "加": "joseph|jose|josé|giuseppe|josef|yusuf|youssef|iosif|józef",
    "如神": "michael|miguel|michel|michele|mikhail|mikael",
    "地働": "george|jorge|giorgio|georg|georgios|yuri",
    "笑": "isaac|ishaq|yitzhak|isak",
    "衆父": "abraham|ibrahim|avraham|abram",
    "冠": "stephen|esteban|stefano|etienne|étienne|stefan",
    "勇": "andrew|andres|andrés|andrea|andré|andreas|andrei",
    "和": "solomon|sulayman|suleiman|süleyman|salomon",
    "神賜": "matthew|mateo|matteo|matthias|matias|mathieu",
    "神聴": "samuel",
    "小": "paul|pablo|paolo|paulo|pavel",
    "神判": "daniel",
}
_PAT = [(k, re.compile(r"^(?:" + v + r")$", re.I)) for k, v in ROOTS.items()]


def kanji_for(given):
    """The neo-kun'yomi of a given name's first word, or None."""
    if not given:
        return None
    first = given.split()[0].strip(",.")
    for k, p in _PAT:
        if p.match(first):
            return k
    return None
