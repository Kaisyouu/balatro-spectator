import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://balatrowiki.org"
API_URL = f"{BASE_URL}/api.php"
USER_AGENT = "balatro-spectator/0.1 (local scraper)"

REQUEST_DELAY = 0.15
MAX_RETRIES = 3

KINDS = [
    {
        "kind": "jokers",
        "categories": ["Category:Jokers by number"],
        "templates": ["Joker info"],
    },
    {
        "kind": "consumables",
        "categories": [
            "Category:Tarot Cards",
            "Category:Planet Cards",
            "Category:Spectral Cards",
        ],
        "templates": ["Consumable info"],
    },
    {
        "kind": "vouchers",
        "categories": ["Category:Vouchers"],
        "templates": ["Voucher info"],
    },
    {
        "kind": "tags",
        "categories": ["Category:Tags"],
        "templates": ["Tag info"],
    },
    {
        "kind": "blinds",
        "categories": ["Category:Boss Blinds"],
        "templates": ["Blind info"],
        "extra_titles": ["Small Blind", "Big Blind"],
    },
    {
        "kind": "decks",
        "categories": ["Category:Decks", "Category:Challenge Decks"],
        "templates": ["Deck info"],
    },
    {
        "kind": "booster_packs",
        "categories": ["Category:Booster Packs"],
        "templates": ["Booster Pack info", "Booster pack info"],
    },
    {
        "kind": "stakes",
        "categories": ["Category:Stakes"],
        "templates": ["Stake info"],
    },
    {
        "kind": "poker_hands",
        "categories": ["Category:Poker Hands"],
        "templates": ["Poker hand info", "Hand info"],
    },
    {
        "kind": "card_modifiers",
        "categories": ["Category:Card Modifiers"],
        "templates": ["Card modifier info", "Card Modifiers info"],
    },
]


def api_get(params):
    query = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query}"
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504):
                time.sleep(1.0 + attempt)
                continue
            raise
        except urllib.error.URLError:
            time.sleep(1.0 + attempt)
            continue
    raise RuntimeError(f"Failed API request after {MAX_RETRIES} retries: {url}")


def get_category_members(category_title):
    members = []
    cont = None
    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmlimit": "500",
        }
        if cont:
            params["cmcontinue"] = cont
        data = api_get(params)
        for entry in data.get("query", {}).get("categorymembers", []):
            if entry.get("ns") == 0:
                members.append(entry["title"])
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
        time.sleep(REQUEST_DELAY)
    return members


def fetch_page(title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "content|ids|timestamp",
        "rvslots": "main",
        "redirects": "1",
        "titles": title,
    }
    data = api_get(params)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), None)
    if not page or "missing" in page:
        return None
    revisions = page.get("revisions")
    if not revisions:
        return None
    rev = revisions[0]
    slot = rev.get("slots", {}).get("main", {})
    content = slot.get("*") or slot.get("content") or ""
    return {
        "pageid": page.get("pageid"),
        "title": page.get("title"),
        "revid": rev.get("revid"),
        "timestamp": rev.get("timestamp"),
        "content": content,
    }


def find_template(wikitext, template_names):
    if not wikitext:
        return None, None
    names = {name.lower(): name for name in template_names}
    i = 0
    length = len(wikitext)
    while i < length - 1:
        if wikitext[i : i + 2] == "{{":
            j = i + 2
            while j < length and wikitext[j].isspace():
                j += 1
            name_start = j
            while j < length and wikitext[j] not in "|}":
                j += 1
            name = wikitext[name_start:j].strip()
            match = names.get(name.lower())
            if match:
                depth = 0
                k = i
                end = None
                while k < length - 1:
                    chunk = wikitext[k : k + 2]
                    if chunk == "{{":
                        depth += 1
                        k += 2
                        continue
                    if chunk == "}}":
                        depth -= 1
                        k += 2
                        if depth == 0:
                            end = k
                            break
                        continue
                    k += 1
                if end is not None:
                    content_start = j
                    if content_start < length and wikitext[content_start] == "|":
                        content_start += 1
                    content = wikitext[content_start : end - 2]
                    return match, content
            i = j
        i += 1
    return None, None


def split_top_level(text):
    parts = []
    buf = []
    curly = 0
    square = 0
    i = 0
    length = len(text)
    while i < length:
        chunk = text[i : i + 2]
        if chunk == "{{":
            curly += 1
            buf.append(chunk)
            i += 2
            continue
        if chunk == "}}":
            curly = max(0, curly - 1)
            buf.append(chunk)
            i += 2
            continue
        if chunk == "[[":
            square += 1
            buf.append(chunk)
            i += 2
            continue
        if chunk == "]]":
            square = max(0, square - 1)
            buf.append(chunk)
            i += 2
            continue
        if text[i] == "|" and curly == 0 and square == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(text[i])
        i += 1
    parts.append("".join(buf))
    return parts


def parse_params(content):
    params = {}
    positional_index = 1
    for part in split_top_level(content):
        if not part.strip():
            continue
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key:
                params[key] = value
        else:
            params[str(positional_index)] = part.strip()
            positional_index += 1
    return params


def extract_languages(wikitext):
    lang_name, lang_content = find_template(wikitext, ["Languages"])
    if not lang_name:
        return None
    return parse_params(lang_content)


def write_text(path, text, encoding="utf-8"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2), encoding="utf-8")


def main():
    repo_root = Path(__file__).resolve().parents[1]
    wiki_root = repo_root / "data" / "wiki"
    raw_root = wiki_root / "raw"
    parsed_root = wiki_root / "parsed"

    fetched_at = datetime.now(timezone.utc).isoformat()
    meta = {
        "source": {
            "base_url": BASE_URL,
            "api_url": API_URL,
            "license": "CC BY-NC-SA 3.0",
        },
        "fetched_at": fetched_at,
        "counts": {},
        "pages": [],
        "missing_pages": [],
        "missing_templates": [],
    }

    license_text = (
        "Data sourced from Balatro Wiki (https://balatrowiki.org/)\n"
        "License: CC BY-NC-SA 3.0\n"
    )
    write_text(wiki_root / "LICENSE.txt", license_text, encoding="ascii")

    for kind_cfg in KINDS:
        kind = kind_cfg["kind"]
        categories = kind_cfg.get("categories", [])
        templates = kind_cfg.get("templates", [])
        extra_titles = kind_cfg.get("extra_titles", [])

        titles = set(extra_titles)
        for category in categories:
            for title in get_category_members(category):
                titles.add(title)

        items = []
        for title in sorted(titles):
            page = fetch_page(title)
            if not page:
                meta["missing_pages"].append({"kind": kind, "title": title})
                continue

            wikitext = page["content"]
            raw_path = raw_root / kind / f"{page['pageid']}.wiki"
            write_text(raw_path, wikitext)

            template_name, template_content = find_template(wikitext, templates)
            if not template_name:
                meta["missing_templates"].append(
                    {
                        "kind": kind,
                        "title": page["title"],
                        "pageid": page["pageid"],
                        "templates": templates,
                    }
                )
            else:
                params = parse_params(template_content)
                languages = extract_languages(wikitext)
                record = {
                    "kind": kind,
                    "title": page["title"],
                    "pageid": page["pageid"],
                    "revid": page["revid"],
                    "timestamp": page["timestamp"],
                    "url": f"{BASE_URL}/w/{page['title'].replace(' ', '_')}",
                    "template": template_name,
                    "params": params,
                }
                if languages:
                    record["languages"] = languages
                    if "internal" in languages:
                        record["internal_id"] = languages["internal"]
                items.append(record)

            meta["pages"].append(
                {
                    "kind": kind,
                    "title": page["title"],
                    "pageid": page["pageid"],
                    "revid": page["revid"],
                    "raw_path": str(raw_path.relative_to(repo_root)),
                    "template": template_name,
                }
            )
            time.sleep(REQUEST_DELAY)

        write_json(parsed_root / f"{kind}.json", items)
        meta["counts"][kind] = len(items)

    write_json(wiki_root / "meta.json", meta)


if __name__ == "__main__":
    main()
