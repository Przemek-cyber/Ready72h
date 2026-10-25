"""Builds the ready72h.com website (EN + PL) around the app at /app/.

Pages: landing (/ and /pl/), guides (site/guides/*.json → /guides/<slug>/, /pl/poradniki/<slug>/),
free calculators (water, cash), sitemap.xml, robots.txt, llms.txt.
Run: python scripts/build_site.py
"""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "site" / "guides"
SITE = "https://ready72h.com"
BUY_URL = "https://przemek.lemonsqueezy.com/checkout/buy/4ebf56da-3b44-4d2f-9928-e9aaaa581d5b"


def esc(s) -> str:
    return html.escape(str(s), quote=True)


L = {
    "en": {
        "home": "/", "guides": "/guides/", "guide": "/guides/{slug}/",
        "water": "/tools/water-calculator/", "cash": "/tools/emergency-cash-calculator/",
        "nav_guides": "Guides", "nav_tools": "Calculators", "open": "Open the app", "other": "PL", "other_name": "Polski",
        "buy": "Get Ready72h", "have": "Already have access? Open the app",
        "price": "Pay what you want, from 2 PLN · PDF planner + offline app · PL / EN / DE / ES",
        "cta_h": "Get your household's full 72-hour plan",
        "cta_p": "Ready72h turns official guidance from Sweden (MSB), Germany (BBK) and Poland (RCB) into a calm, practical plan: a complete 72-hour supply checklist, a family communication plan for when phones go down, and a “15 minutes to leave the house” go-bag list. Apartment and house versions, printable PDF plus an offline app that tracks your progress.",
        "sources": "Sources", "faq": "FAQ", "more": "More guides", "tools_h": "Free calculators",
        "foot": "General, educational information. Always follow current guidance from your local authorities and emergency services.",
        "hero_h": "Be ready for the first 72 hours of any crisis",
        "hero_p": "Power cut, flood, network blackout – the first three days are on you. Ready72h is a calm, practical household plan based on official guidance from Sweden, Germany and Poland.",
        "feats": [("checklist-water-supplies.jpg", "A 72-hour supply checklist", "Water, food, medicine, cash, light and documents – ticked off as you go, with progress you can see."),
                  ("family-communication-plan.jpg", "A family communication plan", "Meeting points, an out-of-area contact and who does what – for when phones and internet go down."),
                  ("go-bag-15-minutes.jpg", "A 15-minute go-bag", "What to pack in advance so you can leave the house in 15 minutes if you have to.")],
        "guides_h": "Guides", "guides_p": "Short, sourced answers to the questions people ask before a crisis.",
        "updated": "Updated",
    },
    "pl": {
        "home": "/pl/", "guides": "/pl/poradniki/", "guide": "/pl/poradniki/{slug}/",
        "water": "/pl/narzedzia/kalkulator-wody/", "cash": "/pl/narzedzia/kalkulator-gotowki/",
        "nav_guides": "Poradniki", "nav_tools": "Kalkulatory", "open": "Otwórz aplikację", "other": "EN", "other_name": "English",
        "buy": "Kup Ready72h", "have": "Masz już dostęp? Otwórz aplikację",
        "price": "Płacisz, ile chcesz, od 2 zł · planer PDF + aplikacja offline · PL / EN / DE / ES",
        "cta_h": "Pełny plan na 72 godziny dla Twojego domu",
        "cta_p": "Ready72h zamienia oficjalne zalecenia Szwecji (MSB), Niemiec (BBK) i Polski (RCB) w spokojny, praktyczny plan: kompletną listę zapasów na 72 godziny, rodzinny plan łączności na wypadek awarii telefonów i listę „15 minut na wyjście z domu”. Wersje dla mieszkania i domu, PDF do druku i aplikacja offline, która śledzi postęp.",
        "sources": "Źródła", "faq": "Najczęstsze pytania", "more": "Więcej poradników", "tools_h": "Darmowe kalkulatory",
        "foot": "Informacje ogólne i edukacyjne. Zawsze stosuj się do aktualnych zaleceń lokalnych władz i służb ratunkowych.",
        "hero_h": "Bądź gotowy na pierwsze 72 godziny kryzysu",
        "hero_p": "Brak prądu, powódź, awaria sieci – przez pierwsze trzy dni jesteś zdany na siebie. Ready72h to spokojny, praktyczny plan dla domu oparty na oficjalnych zaleceniach Szwecji, Niemiec i Polski.",
        "feats": [("checklist-water-supplies.jpg", "Lista zapasów na 72 godziny", "Woda, jedzenie, leki, gotówka, światło i dokumenty – odhaczasz na bieżąco i widzisz postęp."),
                  ("family-communication-plan.jpg", "Rodzinny plan łączności", "Miejsca spotkań, osoba kontaktowa spoza regionu i kto co robi – na wypadek, gdy telefony i internet nie działają."),
                  ("go-bag-15-minutes.jpg", "Plecak na 15 minut", "Co spakować wcześniej, żeby w razie potrzeby wyjść z domu w 15 minut.")],
        "guides_h": "Poradniki", "guides_p": "Krótkie odpowiedzi ze źródłami na pytania, które warto zadać przed kryzysem.",
        "updated": "Aktualizacja",
    },
}

LOGO = ('<svg class="mark" viewBox="0 0 100 100" aria-hidden="true"><polygon points="50,6 6,94 50,94" fill="#16514e"/>'
        '<polygon points="50,6 94,94 50,94" fill="#c9702c"/></svg>')


def head(lang: str, title: str, desc: str, path: str, alt: str | None, extra: str = "") -> str:
    t = L[lang]
    other = "pl" if lang == "en" else "en"
    alts = ""
    if alt:
        en_p, pl_p = (path, alt) if lang == "en" else (alt, path)
        alts = (f'<link rel="alternate" hreflang="en" href="{SITE}{en_p}"><link rel="alternate" hreflang="pl" href="{SITE}{pl_p}">'
                f'<link rel="alternate" hreflang="x-default" href="{SITE}{en_p}">')
    switch = f'<a class="lang" href="{alt or L[other]["home"]}" hreflang="{other}" title="{t["other_name"]}">{t["other"]}</a>'
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
{alts}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/icons/icon-512.png">
<meta name="theme-color" content="#16514e">
<link rel="icon" href="/icons/icon-192.png">
<link rel="stylesheet" href="/site/site.css">
{extra}
</head>
<body>
<header class="top"><div class="wrap topin"><a class="brand" href="{t['home']}">{LOGO}<span>Ready72h</span></a>
<nav><a class="hide-s" href="{t['guides']}">{t['nav_guides']}</a><a class="hide-s" href="{t['water']}">{t['nav_tools']}</a>{switch}<a class="pill" href="/app/">{t['open']}</a></nav></div></header>
<main class="wrap">
"""


def foot(lang: str) -> str:
    t = L[lang]
    return f"""</main>
<footer class="foot"><div class="wrap">
<p><a href="{t['home']}">Ready72h</a> · <a href="{t['guides']}">{t['nav_guides']}</a> · <a href="{t['water']}">{t['nav_tools']}</a> · <a href="/app/">{t['open']}</a></p>
<p class="muted">{t['foot']}</p>
</div></footer>
</body>
</html>
"""


def cta(lang: str) -> str:
    t = L[lang]
    return f"""<section class="cta"><h2>{t['cta_h']}</h2><p>{t['cta_p']}</p>
<div class="row"><a class="btn" href="{BUY_URL}" rel="nofollow">{t['buy']}</a><a class="btn ghost" href="/app/">{t['have']}</a></div>
<p class="muted small">{t['price']}</p></section>"""


# ---------- calculators ----------
TOOLS = {
    "water": {
        "en": {"title": "Emergency water calculator: how much water for 72 hours?",
               "desc": "Free calculator: how much drinking water your household needs for 72 hours or longer, in litres and bottles.",
               "h1": "Emergency water calculator", "lead": "How much water should your household store? Enter your household and see litres, bottles and canisters.",
               "people": "People in the household", "days": "Days", "level": "Amount per person per day",
               "lv": [("2", "2 l – drinking and cooking (minimum)"), ("3", "3 l – with basic hygiene")],
               "out": "You need", "bottles": "bottles of 1.5 l", "cans": "canisters of 5 l", "or": "or",
               "note": "Based on the RCB recommendation of 2 litres per person per day; 3 litres includes basic hygiene. Add water for pets.",
               "guide": "Read the guide: how much water for 72 hours"},
        "pl": {"title": "Kalkulator wody na 72 godziny: ile wody na zapas?",
               "desc": "Darmowy kalkulator: ile wody pitnej potrzebuje Twój dom na 72 godziny lub dłużej – w litrach i butelkach.",
               "h1": "Kalkulator zapasu wody", "lead": "Ile wody powinien mieć Twój dom? Wpisz liczbę osób i zobacz litry, butelki i kanistry.",
               "people": "Liczba osób w domu", "days": "Liczba dni", "level": "Ilość na osobę dziennie",
               "lv": [("2", "2 l – picie i gotowanie (minimum)"), ("3", "3 l – z podstawową higieną")],
               "out": "Potrzebujesz", "bottles": "butelek 1,5 l", "cans": "kanistrów 5 l", "or": "albo",
               "note": "Na podstawie zalecenia RCB: 2 litry na osobę dziennie; 3 litry obejmują podstawową higienę. Dolicz wodę dla zwierząt.",
               "guide": "Przeczytaj poradnik: ile wody na 72 godziny"},
        "guide_slug": "water-72-hours",
    },
    "cash": {
        "en": {"title": "Emergency cash calculator: how much cash to keep at home?",
               "desc": "Free calculator based on central-bank benchmarks: how much cash your household should keep for the first 72 hours of a blackout.",
               "h1": "Emergency cash calculator", "lead": "How much cash should you keep at home for a power or network outage?",
               "adults": "Adults", "children": "Children",
               "out": "Dutch central bank benchmark for 72 hours", "swe": "Swedish Riksbank example",
               "note": "De Nederlandsche Bank: €70 per adult and €30 per child for 72 hours. Riksbank: for example 1,000 kronor per adult. Convert to your own currency.",
               "guide": "Read the guide: how much cash for a blackout"},
        "pl": {"title": "Kalkulator gotówki na blackout: ile gotówki trzymać w domu?",
               "desc": "Darmowy kalkulator według zaleceń banków centralnych: ile gotówki trzymać w domu na pierwsze 72 godziny awarii.",
               "h1": "Kalkulator gotówki na kryzys", "lead": "Ile gotówki trzymać w domu na wypadek awarii prądu lub sieci?",
               "adults": "Dorośli", "children": "Dzieci",
               "out": "Zalecenie banku centralnego Holandii na 72 godziny", "swe": "Przykład szwedzkiego Riksbanku",
               "note": "De Nederlandsche Bank: 70 € na dorosłego i 30 € na dziecko na 72 godziny. Riksbank: np. 1000 koron na dorosłego. Przelicz na swoją walutę.",
               "guide": "Przeczytaj poradnik: ile gotówki na blackout"},
        "guide_slug": "emergency-cash",
    },
}


def tool_page(kind: str, lang: str, guides: dict) -> str:
    t, x = L[lang], TOOLS[kind][lang]
    path, alt = t[kind], L["pl" if lang == "en" else "en"][kind]
    g = guides.get(TOOLS[kind]["guide_slug"])
    guide_link = f'<p><a href="{t["guide"].format(slug=g[lang]["slug"])}">{esc(x["guide"])} →</a></p>' if g else ""
    if kind == "water":
        opts = "".join(f'<option value="{v}">{esc(lbl)}</option>' for v, lbl in x["lv"])
        body = f"""<div class="calc">
<label>{x['people']}<input id="p" type="number" min="1" max="30" value="4"></label>
<label>{x['days']}<input id="d" type="number" min="1" max="30" value="3"></label>
<label>{x['level']}<select id="l">{opts}</select></label>
<div class="result"><span class="k">{x['out']}</span><span class="v" id="r">–</span><span class="d" id="r2"></span></div>
</div>
<script>(function(){{function u(){{var p=+document.getElementById('p').value||0,d=+document.getElementById('d').value||0,l=+document.getElementById('l').value;
var t=p*d*l;document.getElementById('r').textContent=t.toLocaleString('{lang}')+' l';
document.getElementById('r2').textContent=Math.ceil(t/1.5)+' {x['bottles']} {x['or']} '+Math.ceil(t/5)+' {x['cans']}';}}
['p','d','l'].forEach(function(i){{document.getElementById(i).addEventListener('input',u);}});u();}})();</script>"""
    else:
        body = f"""<div class="calc">
<label>{x['adults']}<input id="a" type="number" min="0" max="20" value="2"></label>
<label>{x['children']}<input id="c" type="number" min="0" max="20" value="2"></label>
<div class="result"><span class="k">{x['out']}</span><span class="v" id="r">–</span><span class="d" id="r2"></span></div>
</div>
<script>(function(){{function u(){{var a=+document.getElementById('a').value||0,c=+document.getElementById('c').value||0;
document.getElementById('r').textContent='€'+(a*70+c*30).toLocaleString('{lang}');
document.getElementById('r2').textContent='{x['swe']}: '+(a*1000).toLocaleString('{lang}')+' SEK';}}
['a','c'].forEach(function(i){{document.getElementById(i).addEventListener('input',u);}});u();}})();</script>"""
    return head(lang, x["title"], x["desc"], path, alt) + f"""
<h1>{esc(x['h1'])}</h1><p class="lead">{esc(x['lead'])}</p>
{body}
<p class="muted small">{esc(x['note'])}</p>
{guide_link}
{cta(lang)}
""" + foot(lang)


# ---------- guides ----------
def guide_page(g: dict, lang: str, all_guides: list[dict]) -> str:
    t, c = L[lang], g[lang]
    other = "pl" if lang == "en" else "en"
    path, alt = t["guide"].format(slug=c["slug"]), L[other]["guide"].format(slug=g[other]["slug"])
    secs = "".join(f"<h2>{esc(s['h'])}</h2>" + "".join(f"<p>{esc(p)}</p>" for p in s["p"]) for s in c["sections"])
    faq = "".join(f"<details><summary>{esc(f['q'])}</summary><p>{esc(f['a'])}</p></details>" for f in c["faq"])
    src = "".join(f'<li><a href="{esc(s["url"])}" rel="nofollow noopener" target="_blank">{esc(s["title"])}</a></li>' for s in g["sources"])
    tool = ""
    if g.get("tool") in TOOLS:
        x = TOOLS[g["tool"]][lang]
        tool = f'<p class="toolbox"><a href="{t[g["tool"]]}">{esc(x["h1"])} →</a></p>'
    more = "".join(f'<li><a href="{t["guide"].format(slug=o[lang]["slug"])}">{esc(o[lang]["title"])}</a></li>'
                   for o in all_guides if o["slug"] != g["slug"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": c["title"], "description": c["description"], "inLanguage": lang,
         "mainEntityOfPage": f"{SITE}{path}", "dateModified": dt.date.today().isoformat(),
         "author": {"@type": "Organization", "name": "Ready72h"}, "publisher": {"@type": "Organization", "name": "Ready72h"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in c["faq"]]}]}
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return head(lang, f"{c['title']} | Ready72h", c["description"], path, alt, extra) + f"""
<nav class="crumbs"><a href="{t['guides']}">{t['nav_guides']}</a> › {esc(c['title'])}</nav>
<article>
<h1>{esc(c['title'])}</h1>
<p class="lead answer">{esc(c['summary'])}</p>
{tool}
{secs}
{cta(lang)}
<h2>{t['faq']}</h2><div class="faq">{faq}</div>
<h2>{t['sources']}</h2><ol class="sources">{src}</ol>
{f"<h2>{t['more']}</h2><ul>{more}</ul>" if more else ""}
</article>
""" + foot(lang)


def guide_list(lang: str, guides: list[dict]) -> str:
    t = L[lang]
    return "".join(f'<a class="gcard" href="{t["guide"].format(slug=g[lang]["slug"])}"><h3>{esc(g[lang]["title"])}</h3>'
                   f'<p>{esc(g[lang]["summary"])}</p></a>' for g in guides)


def guides_hub(lang: str, guides: list[dict]) -> str:
    t = L[lang]
    other = "pl" if lang == "en" else "en"
    return head(lang, f"{t['guides_h']} | Ready72h", t["guides_p"], t["guides"], L[other]["guides"]) + f"""
<h1>{t['guides_h']}</h1><p class="lead">{t['guides_p']}</p>
<div class="grid">{guide_list(lang, guides)}</div>
{cta(lang)}
""" + foot(lang)


def landing(lang: str, guides: list[dict]) -> str:
    t = L[lang]
    other = "pl" if lang == "en" else "en"
    feats = "".join(f'<div class="feat"><img src="/img/{i}" alt="{esc(h)}" loading="lazy" width="420"><h3>{esc(h)}</h3><p>{esc(p)}</p></div>'
                    for i, h, p in t["feats"])
    tools = "".join(f'<a class="gcard tool" href="{t[k]}"><h3>{esc(TOOLS[k][lang]["h1"])}</h3><p>{esc(TOOLS[k][lang]["lead"])}</p></a>' for k in TOOLS)
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Ready72h", "applicationCategory": "LifestyleApplication",
          "operatingSystem": "Web (installable, works offline)", "description": t["hero_p"], "url": SITE + t["home"], "inLanguage": ["pl", "en", "de", "es"],
          "offers": {"@type": "Offer", "price": "2", "priceCurrency": "PLN"}}
    redirect = ("<script>(function(){if(matchMedia('(display-mode: standalone)').matches){location.replace('/app/');}"
                "if('serviceWorker' in navigator){navigator.serviceWorker.getRegistrations().then(function(rs){rs.forEach(function(r){"
                "if(new URL(r.scope).pathname==='/'){r.update();}});});}})();</script>")
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>{redirect}'
    title = ("Ready72h – household plan for the first 72 hours of a crisis" if lang == "en"
             else "Ready72h – plan dla domu na pierwsze 72 godziny kryzysu")
    return head(lang, title, t["hero_p"], t["home"], L[other]["home"], extra) + f"""
<section class="hero"><h1>{t['hero_h']}</h1><p class="lead">{t['hero_p']}</p>
<div class="row"><a class="btn" href="{BUY_URL}" rel="nofollow">{t['buy']}</a><a class="btn ghost" href="/app/">{t['have']}</a></div>
<p class="muted small">{t['price']}</p></section>
<section class="feats">{feats}</section>
<h2>{t['tools_h']}</h2><div class="grid">{tools}</div>
<h2>{t['guides_h']}</h2><p>{t['guides_p']}</p><div class="grid">{guide_list(lang, guides[:6])}</div>
<p><a href="{t['guides']}">{t['guides_h']} →</a></p>
{cta(lang)}
""" + foot(lang)


def write(path: str, content: str) -> None:
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def main() -> None:
    guides = sorted((json.loads(f.read_text()) for f in GUIDES.glob("*.json")), key=lambda g: g["slug"])
    by_slug = {g["slug"]: g for g in guides}
    urls = []
    for lang in ("en", "pl"):
        t = L[lang]
        write(t["home"], landing(lang, guides))
        write(t["guides"], guides_hub(lang, guides))
        urls += [t["home"], t["guides"]]
        for k in TOOLS:
            write(t[k], tool_page(k, lang, by_slug))
            urls.append(t[k])
        for g in guides:
            p = t["guide"].format(slug=g[lang]["slug"])
            write(p, guide_page(g, lang, guides))
            urls.append(p)
    today = dt.date.today().isoformat()
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /app/\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    lines = ["# Ready72h", "", "> Household preparedness planner for the first 72 hours of a crisis (power outage, flood, network blackout), based on official "
             "guidance from Sweden (MSB), Germany (BBK) and Poland (RCB). Printable PDF + offline app, PL/EN/DE/ES, pay what you want from 2 PLN.", "",
             "## Free calculators", f"- [Emergency water calculator]({SITE}{L['en']['water']})", f"- [Emergency cash calculator]({SITE}{L['en']['cash']})", "",
             "## Guides"] + [f"- [{g['en']['title']}]({SITE}{L['en']['guide'].format(slug=g['en']['slug'])}): {g['en']['summary']}" for g in guides]
    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Built site: {len(urls)} pages")


if __name__ == "__main__":
    main()
