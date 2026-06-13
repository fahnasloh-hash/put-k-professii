# -*- coding: utf-8 -*-
"""SEO content plan for putkprofessii.ru.

Generated topics are limited to Moscow and Moscow Region.
"""

INTENTS = [
    ("Как выбрать", "объяснить критерии выбора и привести к консультации"),
    ("Куда поступить", "закрыть коммерческий запрос и показать варианты маршрута"),
    ("Сколько стоит", "снять ценовое возражение и отправить на подбор"),
    ("Какие документы нужны", "закрыть процедурный вопрос и предложить помощь"),
    ("Как поступить без ЕГЭ", "показать альтернативный маршрут через колледж или СПО"),
]

AUDIENCES = [
    ("после 9 класса", "/postuplenie-posle-9-klassa/"),
    ("после 11 класса", "/postuplenie-posle-11-klassa/"),
    ("с низкими баллами", "/postuplenie-bez-ege/"),
    ("для родителей", "/pomoshch-s-postupleniem/"),
]

TOPICS = [
    ("IT и программирование", "/professii/programmist/"),
    ("веб-разработка", "/professii/web-razrabotchik/"),
    ("анализ данных", "/professii/analitik/"),
    ("маркетинг", "/professii/marketolog/"),
    ("реклама и PR", "/professii/reklamist/"),
    ("дизайн", "/professii/dizayner/"),
    ("психология", "/professii/psiholog/"),
    ("юриспруденция", "/professii/yurist/"),
    ("экономика и финансы", "/professii/ekonomist/"),
    ("бухгалтерия", "/professii/buhgalter/"),
    ("менеджмент", "/professii/menedzher/"),
    ("предпринимательство", "/professii/predprinimatel/"),
    ("логистика", "/professii/logist/"),
    ("педагогика", "/professii/pedagog/"),
    ("HR", "/professii/hr-specialist/"),
    ("медицина", "/fakultety/meditsina/"),
    ("фармация", "/fakultety/farmaciya/"),
    ("стоматология", "/fakultety/stomatologiya/"),
    ("транспорт", "/fakultety/transport/"),
    ("инженерия", "/fakultety/inzheneriya/"),
]


def _slug(text):
    table = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
        "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    out = "".join(table.get(ch, ch) for ch in text.lower())
    keep = []
    prev_dash = False
    for ch in out:
        if ch.isalnum():
            keep.append(ch)
            prev_dash = False
        elif not prev_dash:
            keep.append("-")
            prev_dash = True
    return "".join(keep).strip("-")


CONTENT_PLAN = []
for topic, topic_url in TOPICS:
    for intent, goal in INTENTS:
        for audience, audience_url in AUDIENCES:
            title = f"{intent}: {topic} в Москве и Московской области {audience}"
            CONTENT_PLAN.append({
                "title": title,
                "main_query": f"{topic} {audience} Москва",
                "cluster": topic,
                "goal": goal,
                "url": f"/blog/{_slug(title)}/",
                "internal_links": [topic_url, audience_url, "/kolledzhi-moskvy/", "/vuzy-moskvy/"],
                "region": "Москва и Московская область",
                "cta": "Получить консультацию по поступлению",
            })

# Keep a practical publication queue while still exceeding the PDF requirement.
CONTENT_PLAN = CONTENT_PLAN[:120]
