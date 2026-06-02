# -*- coding: utf-8 -*-
"""
Static page generator for putkprofessii.ru SEO catalog.
Reads data/institutions.py, emits hub + detail pages and sitemap.xml.
Run:  /c/Python314/python scripts/gen.py
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'data'))
import institutions as D
import faculties as F

CSS_VER = '20260603'
SITE = 'https://putkprofessii.ru'

COLOR_CYCLE = ['blue', 'green', 'purple', 'amber']


def head(title, desc, canonical):
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="{SITE}{canonical}"/>
<meta name="robots" content="index,follow"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="{SITE}{canonical}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:image" content="{SITE}/hero.png"/>
<meta property="og:locale" content="ru_RU"/>
<link rel="shortcut icon" href="/favicon.ico"/>
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png"/>
<link rel="apple-touch-icon" sizes="180x180" href="/favicon.png"/>
<meta name="theme-color" content="#1F66FF"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@1,6..72,500&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/styles.css?v={CSS_VER}"/>
</head>
<body>
'''


NAV = '''<nav class="nav" role="navigation" aria-label="Главное меню">
  <a href="/" class="brand" aria-label="Путь к профессии — главная">
    <span class="brand__mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg></span>
    <span class="brand__text"><strong>Путь к профессии</strong><em>поступление 2026</em></span>
  </a>
  <nav class="nav__menu" aria-label="Разделы сайта">
    <a href="/vuzy-moskvy/">Вузы</a>
    <a href="/kolledzhi-moskvy/">Колледжи</a>
    <a href="/fakultety/">Факультеты</a>
    <a href="/kuda-postupit-posle-9-klassa/">После 9 класса</a>
    <a href="/postuplenie-2026/">Поступление 2026</a>
    <a href="/blog/">Блог</a>
  </nav>
  <div class="nav__cta"><a href="#" data-apply="" class="btn btn--primary">Получить консультацию →</a></div>
  <button class="nav__burger" id="burger" aria-label="Открыть меню" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<nav class="nav__mobile" id="mobileMenu" aria-label="Мобильное меню">
  <a href="/vuzy-moskvy/">🎓 Вузы Москвы и МО</a>
  <a href="/kolledzhi-moskvy/">🏫 Колледжи</a>
  <a href="/fakultety/">🧭 Факультеты</a>
  <a href="/kuda-postupit-posle-9-klassa/">📚 После 9 класса</a>
  <a href="/postuplenie-2026/">📅 Поступление 2026</a>
  <a href="/pomoshch-s-postupleniem/">🤝 Помощь</a>
  <a href="/blog/">✍️ Блог</a>
  <a href="#" data-apply="" class="btn btn--primary">Получить консультацию →</a>
</nav>
'''


FOOTER = '''<footer class="footer" role="contentinfo">
  <div class="footer__inner">
    <div class="footer__brand"><div class="footer__logo"><span class="mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg></span><strong>Путь к профессии</strong></div><p class="footer__desc">Бесплатная помощь с поступлением в Москве и МО. С 2022 года.</p></div>
    <div class="footer__col"><h4>Вузы</h4><ul><li><a href="/vuzy-moskvy/">Вузы Москвы</a></li><li><a href="/vuzy-moskovskoy-oblasti/">Вузы Московской области</a></li><li><a href="/postuplenie-2026/">Поступление 2026</a></li></ul></div>
    <div class="footer__col"><h4>Колледжи</h4><ul><li><a href="/kolledzhi-moskvy/">Колледжи Москвы</a></li><li><a href="/kolledzhi-pri-vuze/">Колледжи при вузах</a></li><li><a href="/kuda-postupit-posle-9-klassa/">После 9 класса</a></li></ul></div>
    <div class="footer__col"><h4>Сервис</h4><ul><li><a href="/pomoshch-s-postupleniem/">Помощь</a></li><li><a href="/blog/">Блог</a></li><li><a href="#" data-apply="">Консультация</a></li></ul></div>
  </div>
  <div class="footer__bottom"><span>© 2026 Путь к профессии · <a href="/" style="color:inherit">putkprofessii.ru</a></span><span>Москва и МО</span></div>
</footer>
<div class="sticky-cta" aria-hidden="true"><a href="#" data-apply="" class="btn btn--primary btn--full">Получить бесплатную консультацию →</a></div>
<script src="/app.js?v={ver}"></script>
</body>
</html>'''.replace('{ver}', CSS_VER)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def card(inst, base_url):
    """Compact hub card linking to detail page + apply button."""
    color = inst.get('color') or 'blue'
    badge_cls = 'inst-card__badge--top' if inst['type'] == 'Государственный' else 'inst-card__badge--choice'
    detail = f"{inst.get('_base', base_url)}{inst['slug']}/"
    budget = 'Бюджет есть' if inst.get('budget') else 'Платно'
    loc = inst.get('city', 'Москва')
    name = esc(inst['name'])
    return f'''    <article class="inst-card inst-card--{color}">
      <div class="inst-card__head">
        <div class="inst-card__logo"><span class="inst-card__logo-text">{esc(inst['abbr'])}</span></div>
        <div class="inst-card__headmain">
          <span class="inst-card__badge {badge_cls}">{inst['type']}</span>
          <h4><a class="inst-card__namelink" href="{detail}">{name}</a></h4>
          <div class="inst-card__loc">{loc} · {budget} · {esc(inst['dirs'])}</div>
        </div>
      </div>
      <div class="inst-card__divider"></div>
      <div class="inst-card__actions">
        <a href="{detail}" class="btn btn--white">Подробнее</a>
        <button type="button" class="btn btn--primary" data-apply="{name}">Поступить →</button>
      </div>
    </article>'''


def hub_page(cfg, items, alt_links):
    """cfg: dict with url, title, desc, h1, eyebrow, lede, kind. alt_links: list of (url,label,active)."""
    toggle = ''.join(
        f'<a href="{u}" class="toggle__btn{" toggle__btn--active" if a else ""}">{l}</a>'
        for (u, l, a) in alt_links
    )
    cards = '\n\n'.join(card(it, cfg['base_url']) for it in items)
    html = head(cfg['title'], cfg['desc'], cfg['url'])
    html += NAV
    html += f'''
<section class="section" aria-labelledby="page-h1" style="padding-bottom:0">
  <nav class="breadcrumbs" aria-label="Навигационная цепочка">
    <a href="/">Главная</a><span class="sep">›</span><span aria-current="page">{cfg['crumb']}</span>
  </nav>
  <div class="pill" style="margin-bottom:20px"><span class="pill__dot" aria-hidden="true"></span>{cfg['eyebrow']}</div>
  <h1 class="display" id="page-h1" style="max-width:20ch">{cfg['h1']}</h1>
  <p class="lede" style="margin-top:20px;max-width:64ch">{cfg['lede']}</p>
  <div class="toggle" role="tablist" style="margin-top:24px">{toggle}</div>
</section>

<section class="section" id="catalog" style="padding-top:24px">
  <div class="inst-grid">
{cards}
  </div>
  <p style="font-size:13px;color:var(--ink-mute);margin-top:20px">Не нашли нужное заведение? <a href="#" data-apply="" class="consent-link">Оставьте заявку</a> — подберём вариант под ваши баллы бесплатно.</p>
</section>

<section class="section" id="form" aria-labelledby="form-h2" style="padding-top:0">
  <div class="cta-band">
    <h2>{cfg['cta_h']}</h2>
    <p>Бесплатно подберём учебные заведения под ваши баллы и расскажем о поступлении за 15 минут.</p>
    <a href="#" data-apply="" class="btn btn--white btn--lg" style="margin-top:18px">Получить подбор →</a>
  </div>
</section>
'''
    html += FOOTER
    return html


def detail_page(inst, ctx):
    """ctx: dict with base_url, region_label, hub_url, hub_label, kind, related (list)."""
    name = inst['name']
    full = inst.get('full', name)
    city = inst.get('city', 'Москва')
    budget = 'Есть' if inst.get('budget') else 'Нет'
    kind_word = ctx['kind_word']  # 'вуз' / 'колледж'
    url = f"{ctx['base_url']}{inst['slug']}/"
    title = f"{esc(name)} — поступление 2026: направления, баллы, бюджет"
    desc = f"{esc(full)} ({esc(inst['abbr'])}), {city}. {esc(inst['dirs'])}. {('Есть бюджетные места.' if inst.get('budget') else 'Обучение платное.')} Как поступить, направления подготовки — бесплатная консультация."
    # related links
    rel = ''.join(
        f'<li><a href="{ctx["base_url"]}{r["slug"]}/">{esc(r["name"])}</a></li>'
        for r in ctx['related']
    )
    facts = f'''<div class="card" style="max-width:none;margin:0 0 28px">
    <dl class="inst-card__specs">
      <div class="inst-card__spec"><dt>Тип</dt><dd>{inst['type']}</dd></div>
      <div class="inst-card__spec"><dt>Бюджетные места</dt><dd>{budget}</dd></div>
      <div class="inst-card__spec"><dt>Город</dt><dd>{city}</dd></div>
      <div class="inst-card__spec"><dt>Направления</dt><dd>{esc(inst['dirs'])}</dd></div>
    </dl>
  </div>'''
    intro = inst.get('desc', '')
    html = head(title, desc, url)
    html += NAV
    html += f'''
<section class="section" aria-labelledby="page-h1" style="padding-bottom:0">
  <nav class="breadcrumbs" aria-label="Навигационная цепочка">
    <a href="/">Главная</a><span class="sep">›</span><a href="{ctx['hub_url']}">{ctx['hub_label']}</a><span class="sep">›</span><span aria-current="page">{esc(inst['abbr'])}</span>
  </nav>
  <div class="inst-detail-head">
    <div class="inst-card__logo inst-card--{inst['color']}" style="width:84px;height:84px"><span class="inst-card__logo-text">{esc(inst['abbr'])}</span></div>
    <div>
      <h1 class="display--md" id="page-h1" style="max-width:22ch">{esc(full)}</h1>
      <div class="inst-card__loc" style="margin-top:8px;font-size:14px">{city} · {inst['type']}{' · Бюджетные места есть' if inst.get('budget') else ' · Платное обучение'}</div>
    </div>
  </div>
  <p class="lede" style="margin-top:18px;max-width:66ch">{intro}</p>
  <div style="margin-top:22px">
    <button type="button" class="btn btn--primary btn--lg" data-apply="{esc(name)}">Поступить в {esc(inst['abbr'])} →</button>
  </div>
</section>

<section class="section" style="padding-top:28px">
  {facts}
  <h2 class="display--sm" style="margin-bottom:14px">Как поступить в {esc(name)} в 2026 году</h2>
  <p style="font-size:15px;color:var(--ink-soft);line-height:1.65;max-width:68ch">Поступление в {kind_word} проходит по {('результатам ЕГЭ и внутренним испытаниям' if ctx['kind'] == 'vuz' else 'среднему баллу аттестата — без ЕГЭ')}. Подаём документы, проверяем шансы на бюджет и платное, расставляем приоритеты. Эксперты «Путь к профессии» помогут с поступлением в {esc(name)} бесплатно — подберём направление, рассчитаем шансы и подготовим документы.</p>
  <div style="margin-top:20px">
    <button type="button" class="btn btn--primary" data-apply="{esc(name)}">Оставить заявку →</button>
  </div>
</section>

<section class="section" style="padding-top:0" aria-labelledby="rel-h2">
  <h2 class="display--sm" id="rel-h2" style="margin-bottom:14px">Похожие учебные заведения</h2>
  <nav class="link-grid"><ul style="display:contents">{rel}</ul></nav>
  <p style="margin-top:18px"><a href="{ctx['hub_url']}" class="btn btn--white">← Все {ctx['hub_label_low']}</a></p>
</section>
'''
    html += FOOTER
    return html


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)


def assign_colors(items):
    for i, it in enumerate(items):
        it.setdefault('color', COLOR_CYCLE[i % len(COLOR_CYCLE)])


def related_for(items, idx, n=4):
    out = []
    k = len(items)
    for j in range(1, k):
        out.append(items[(idx + j) % k])
        if len(out) >= n:
            break
    return out


def build_index():
    """slug -> inst dict, with _base (detail URL prefix) attached."""
    idx = {}
    for items, base in [
        (D.VUZY_MSK, '/vuzy-moskvy/'),
        (D.VUZY_MO, '/vuzy-moskovskoy-oblasti/'),
        (D.KOLLEDZHI_MSK, '/kolledzhi-moskvy/'),
        (D.KOLLEDZHI_PRI_VUZE, '/kolledzhi-pri-vuze/'),
    ]:
        for it in items:
            it['_base'] = base
            idx[it['slug']] = it
    return idx


def fac_hub(faculties, idx):
    title = 'Факультеты и направления вузов и колледжей Москвы — куда поступить'
    desc = 'Все факультеты и направления подготовки: IT, медицина, экономика, юриспруденция, дизайн и другие. Выберите направление — покажем вузы и колледжи Москвы и области, где этому учат.'
    cards = []
    for f in faculties:
        cnt = sum(1 for s in f['members'] if s in idx)
        cards.append(
            f'''    <a class="fac-card" href="/fakultety/{f['slug']}/">
      <span class="fac-card__icon" aria-hidden="true">{f['icon']}</span>
      <span class="fac-card__name">{esc(f['name'])}</span>
      <span class="fac-card__count">{cnt} заведений</span>
    </a>''')
    html = head(title, desc, '/fakultety/') + NAV
    html += f'''
<section class="section" aria-labelledby="page-h1" style="padding-bottom:0">
  <nav class="breadcrumbs" aria-label="Навигационная цепочка">
    <a href="/">Главная</a><span class="sep">›</span><span aria-current="page">Факультеты</span>
  </nav>
  <div class="pill" style="margin-bottom:20px"><span class="pill__dot" aria-hidden="true"></span>Направления подготовки · 2026</div>
  <h1 class="display" id="page-h1" style="max-width:20ch">Факультеты и направления</h1>
  <p class="lede" style="margin-top:20px;max-width:64ch">Выберите направление подготовки — покажем вузы и колледжи Москвы и Московской области, где на него учат, с бюджетными местами. Поможем поступить бесплатно.</p>
</section>

<section class="section" style="padding-top:24px">
  <div class="fac-grid">
{chr(10).join(cards)}
  </div>
</section>

<section class="section" id="form" style="padding-top:0">
  <div class="cta-band">
    <h2>Не знаете, какое направление выбрать?</h2>
    <p>Поможем определиться с факультетом и подберём учебные заведения под ваши баллы — бесплатно за 15 минут.</p>
    <a href="#" data-apply="" class="btn btn--white btn--lg" style="margin-top:18px">Получить консультацию →</a>
  </div>
</section>
'''
    html += FOOTER
    return html


def fac_detail(f, idx, faculties):
    members = [idx[s] for s in f['members'] if s in idx]
    title = f"{esc(f['name'])} — вузы и колледжи Москвы, куда поступить в 2026"
    desc = f"{esc(f['desc'])}"
    cards = '\n\n'.join(card(it, it['_base']) for it in members)
    # other faculties for internal linking
    others = [x for x in faculties if x['slug'] != f['slug']][:8]
    other_links = ''.join(f'<a href="/fakultety/{o["slug"]}/">{o["icon"]} {esc(o["name"])}</a>' for o in others)
    html = head(title, desc, f"/fakultety/{f['slug']}/") + NAV
    html += f'''
<section class="section" aria-labelledby="page-h1" style="padding-bottom:0">
  <nav class="breadcrumbs" aria-label="Навигационная цепочка">
    <a href="/">Главная</a><span class="sep">›</span><a href="/fakultety/">Факультеты</a><span class="sep">›</span><span aria-current="page">{esc(f['name'])}</span>
  </nav>
  <div class="inst-detail-head">
    <div class="inst-card__logo" style="width:84px;height:84px;font-size:38px;background:linear-gradient(135deg,#1F66FF,#5b8cff)"><span style="font-size:40px">{f['icon']}</span></div>
    <div>
      <h1 class="display--md" id="page-h1" style="max-width:24ch">{esc(f['name'])}</h1>
      <div class="inst-card__loc" style="margin-top:8px;font-size:14px">{len(members)} учебных заведений Москвы и области</div>
    </div>
  </div>
  <p class="lede" style="margin-top:18px;max-width:66ch">{esc(f['desc'])}</p>
  <div style="margin-top:22px">
    <button type="button" class="btn btn--primary btn--lg" data-apply="Направление: {esc(f['name'])}">Поступить на «{esc(f['name'])}» →</button>
  </div>
</section>

<section class="section" id="catalog" style="padding-top:28px">
  <h2 class="display--sm" style="margin-bottom:16px">Где учат: {esc(f['name'])}</h2>
  <div class="inst-grid">
{cards}
  </div>
</section>

<section class="section" style="padding-top:0" aria-labelledby="other-h2">
  <h2 class="display--sm" id="other-h2" style="margin-bottom:14px">Другие направления</h2>
  <nav class="link-grid">{other_links}</nav>
  <p style="margin-top:18px"><a href="/fakultety/" class="btn btn--white">← Все факультеты</a></p>
</section>
'''
    html += FOOTER
    return html


def main():
    urls = []  # for sitemap (loc, priority)

    # ---------------- VUZY ----------------
    assign_colors(D.VUZY_MSK)
    assign_colors(D.VUZY_MO)

    vuz_alt = lambda active: [
        ('/vuzy-moskvy/', 'Москва', active == 'msk'),
        ('/vuzy-moskovskoy-oblasti/', 'Московская область', active == 'mo'),
    ]

    # Moscow vuzy hub
    write('vuzy-moskvy/index.html', hub_page({
        'url': '/vuzy-moskvy/', 'crumb': 'Вузы Москвы',
        'title': 'Вузы Москвы 2026 — список университетов, баллы, бюджет, поступление',
        'desc': 'Все вузы Москвы 2026: МГУ, МФТИ, ВШЭ, МГТУ, МГИМО, Сеченова и другие. Направления, бюджетные места, как поступить. Бесплатный подбор вуза под ваши баллы.',
        'eyebrow': 'Вузы Москвы · Поступление 2026',
        'h1': 'Вузы Москвы 2026',
        'lede': 'Список ведущих университетов Москвы: направления подготовки, бюджетные места, тип вуза. Выберите учебное заведение или оставьте заявку — подберём вуз под ваши баллы ЕГЭ бесплатно.',
        'base_url': '/vuzy-moskvy/',
        'cta_h': 'Узнайте, в какой вуз Москвы вы проходите по баллам',
    }, D.VUZY_MSK, vuz_alt('msk')))
    urls.append(('/vuzy-moskvy/', '0.9'))

    # MO vuzy hub
    write('vuzy-moskovskoy-oblasti/index.html', hub_page({
        'url': '/vuzy-moskovskoy-oblasti/', 'crumb': 'Вузы Московской области',
        'title': 'Вузы Московской области 2026 — университеты Подмосковья, поступление',
        'desc': 'Вузы Московской области 2026: Дубна, Технологический университет, ГСГУ, таможенная академия и другие. Направления, бюджет, как поступить. Бесплатный подбор.',
        'eyebrow': 'Вузы Московской области · 2026',
        'h1': 'Вузы Московской области 2026',
        'lede': 'Университеты Подмосковья: Дубна, Королёв, Коломна, Химки, Люберцы и другие города. Направления, бюджетные места и помощь с поступлением — бесплатно.',
        'base_url': '/vuzy-moskovskoy-oblasti/',
        'cta_h': 'Подберём вуз Московской области под ваши баллы',
    }, D.VUZY_MO, vuz_alt('mo')))
    urls.append(('/vuzy-moskovskoy-oblasti/', '0.8'))

    # Vuzy detail pages
    for region, items, base, hub_url, hub_label in [
        ('msk', D.VUZY_MSK, '/vuzy-moskvy/', '/vuzy-moskvy/', 'Вузы Москвы'),
        ('mo', D.VUZY_MO, '/vuzy-moskovskoy-oblasti/', '/vuzy-moskovskoy-oblasti/', 'Вузы Московской области'),
    ]:
        for idx, inst in enumerate(items):
            ctx = {'base_url': base, 'hub_url': hub_url, 'hub_label': hub_label,
                   'hub_label_low': hub_label.lower(), 'kind': 'vuz', 'kind_word': 'вуз',
                   'related': related_for(items, idx)}
            write(f"{base.strip('/')}/{inst['slug']}/index.html", detail_page(inst, ctx))
            urls.append((f"{base}{inst['slug']}/", '0.7'))

    # ---------------- KOLLEDZHI ----------------
    assign_colors(D.KOLLEDZHI_MSK)
    assign_colors(D.KOLLEDZHI_PRI_VUZE)

    kol_alt = lambda active: [
        ('/kolledzhi-moskvy/', 'Колледжи Москвы', active == 'msk'),
        ('/kolledzhi-pri-vuze/', 'Колледжи при вузах', active == 'vuz'),
    ]

    write('kolledzhi-moskvy/index.html', hub_page({
        'url': '/kolledzhi-moskvy/', 'crumb': 'Колледжи Москвы',
        'title': 'Колледжи Москвы 2026 — список, специальности, бюджет, поступление после 9',
        'desc': 'Колледжи Москвы 2026: специальности, бюджетные места, средний балл. Поступление после 9 и 11 класса без ЕГЭ. Бесплатный подбор колледжа под ваши оценки.',
        'eyebrow': 'Колледжи Москвы · 2026',
        'h1': 'Колледжи Москвы 2026',
        'lede': 'Список колледжей Москвы по специальностям: IT, транспорт, строительство, медицина, экономика. Поступление по среднему баллу аттестата — без ЕГЭ. Подберём колледж бесплатно.',
        'base_url': '/kolledzhi-moskvy/',
        'cta_h': 'Подберём колледж Москвы под ваши оценки',
    }, D.KOLLEDZHI_MSK, kol_alt('msk')))
    urls.append(('/kolledzhi-moskvy/', '0.9'))

    write('kolledzhi-pri-vuze/index.html', hub_page({
        'url': '/kolledzhi-pri-vuze/', 'crumb': 'Колледжи при вузах',
        'title': 'Колледжи при вузах Москвы 2026 — поступление без ЕГЭ, переход в вуз',
        'desc': 'Колледжи при вузах Москвы: Синергия, РАНХиГС, Плеханова, МТИ. Поступление без ЕГЭ по аттестату, переход в вуз по упрощённой процедуре. Бесплатный подбор.',
        'eyebrow': 'Колледжи при вузах · 2026',
        'h1': 'Колледжи при вузах Москвы',
        'lede': 'Учитесь в колледже при московском вузе и переходите на высшее образование без ЕГЭ по упрощённой процедуре. Список колледжей при вузах и помощь с поступлением — бесплатно.',
        'base_url': '/kolledzhi-pri-vuze/',
        'cta_h': 'Подберём колледж при вузе под ваши оценки',
    }, D.KOLLEDZHI_PRI_VUZE, kol_alt('vuz')))
    urls.append(('/kolledzhi-pri-vuze/', '0.8'))

    for region, items, base, hub_url, hub_label in [
        ('msk', D.KOLLEDZHI_MSK, '/kolledzhi-moskvy/', '/kolledzhi-moskvy/', 'Колледжи Москвы'),
        ('vuz', D.KOLLEDZHI_PRI_VUZE, '/kolledzhi-pri-vuze/', '/kolledzhi-pri-vuze/', 'Колледжи при вузах'),
    ]:
        for idx, inst in enumerate(items):
            ctx = {'base_url': base, 'hub_url': hub_url, 'hub_label': hub_label,
                   'hub_label_low': hub_label.lower(), 'kind': 'college', 'kind_word': 'колледж',
                   'related': related_for(items, idx)}
            write(f"{base.strip('/')}/{inst['slug']}/index.html", detail_page(inst, ctx))
            urls.append((f"{base}{inst['slug']}/", '0.7'))

    # ---------------- FACULTIES ----------------
    idx = build_index()
    write('fakultety/index.html', fac_hub(F.FACULTIES, idx))
    urls.append(('/fakultety/', '0.9'))
    for f in F.FACULTIES:
        write(f"fakultety/{f['slug']}/index.html", fac_detail(f, idx, F.FACULTIES))
        urls.append((f"/fakultety/{f['slug']}/", '0.7'))

    # ---------------- SITEMAP ----------------
    static_urls = [
        ('/', '1.0'),
        ('/postuplenie-2026/', '0.7'),
        ('/pomoshch-s-postupleniem/', '0.7'),
        ('/kuda-postupit-posle-9-klassa/', '0.7'),
        ('/it-kolledzh-moskva/', '0.6'),
        ('/meditsinskie-kolledzhi-moskvy/', '0.6'),
        ('/blog/', '0.6'),
    ]
    all_urls = static_urls + urls
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in all_urls:
        sm.append(f'  <url><loc>{SITE}{loc}</loc><priority>{pr}</priority></url>')
    sm.append('</urlset>')
    write('sitemap.xml', '\n'.join(sm) + '\n')

    print(f'Generated {len(urls)} catalog pages + 4 hubs. Sitemap: {len(all_urls)} urls.')


if __name__ == '__main__':
    main()
