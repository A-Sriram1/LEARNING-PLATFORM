import re
import httpx
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="SkillForge AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from app.routers import topics, coding, mcq, interview
    app.include_router(topics.router)
    app.include_router(coding.router)
    app.include_router(mcq.router)
    app.include_router(interview.router)
except Exception:
    pass


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── YouTube video search ───────────────────────────────────────────────────
@app.get("/demo/videos")
async def demo_videos(topic: str, lang: str = "tamil"):
    import urllib.parse
    query = f"{topic} tutorial {lang}" if lang == "tamil" else f"{topic} tutorial"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}&sp=CAM%253D"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True, verify=False) as client:
            resp = await client.get(url, headers=headers)
            html = resp.text
        ids      = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        titles   = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
        channels = re.findall(r'"ownerText":\{"runs":\[\{"text":"([^"]+)"', html)
        seen, videos = set(), []
        for i, vid in enumerate(ids):
            if vid in seen: continue
            seen.add(vid)
            videos.append({
                "videoId": vid,
                "title":   titles[i]   if i < len(titles)   else f"{topic} Tutorial",
                "channel": channels[i] if i < len(channels) else "YouTube",
            })
            if len(videos) >= 5: break
        return JSONResponse({"videos": videos})
    except Exception as e:
        return JSONResponse({"videos": [], "error": str(e)})


# -- Theory content: Wikipedia REST summary + structured HTML scrape ----------
@app.get("/api/theory")
async def get_theory(topic: str):
    import urllib.parse

    hdrs = {
        "User-Agent": (
            "SkillForgeAI/1.0 "
            "(https://github.com/A-Sriram1/LEARNING-PLATFORM; "
            "skillforge-ai-app) python-httpx/0.27"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # ── Normalise the topic ────────────────────────────────────────────────
    # Strip redundant words users type: "Python Programming Language Tutorial"
    # becomes "Python" before the Wikipedia search.
    _strip = re.compile(
        r"\s+(programming\s+language|language|tutorial|course|basics?"
        r"|introduction|intro|guide|explained?|crash\s+course"
        r"|for\s+beginners?|concepts?|overview|js|ts)$",
        re.IGNORECASE,
    )
    norm = re.sub(r"\.(js|ts)$", "", topic.strip(), flags=re.IGNORECASE)
    while True:
        t = _strip.sub("", norm).strip()
        if t == norm:
            break
        norm = t
    search_topic = norm.title()   # "python" -> "Python"

    # ── CS confirmation ────────────────────────────────────────────────────
    CS_KEYWORDS = [
        "programming language", "software", "computer science", "computing",
        "algorithm", "data structure", "framework", "library", "runtime",
        "compiler", "interpreter", "operating system", "database", "network",
        "machine learning", "artificial intelligence", "web", "api",
        "object-oriented", "functional programming", "syntax", "semantics",
        "open-source", "open source", "source code", "developer", "codebase",
    ]

    def is_cs(s: dict) -> bool:
        text = (s.get("extract", "") + " " + s.get("description", "")).lower()
        return any(k in text for k in CS_KEYWORDS)

    TECH_SUFFIXES = [
        " (programming language)", " (software)", " (computer science)",
        " (programming)", " (data structure)", " (algorithm)",
        " (computing)", " (framework)", "",
    ]

    SKIP_SECS = [
        "History", "Etymology", "Reception", "Awards", "Legacy", "Naming",
        "Language development", "Languages influenced", "Controversy",
        "Cultural", "Biography", "Personal life", "Early life",
        "See also", "References", "Notes", "Further reading", "External links",
    ]
    HIST_SIGNALS = [
        "was born", "in the late 1980s", "in the 1990s", "in the 2000s",
        "created by", "invented by", "developed by", "designed by",
        "named after", "named for", "released in 19", "released in 20",
        "first appeared", "initial release", "version 1.", "version 2.",
        "van Rossum", "Guido", "Bjarne", "James Gosling",
    ]
    CS_SECTION_NAMES = [
        "Definition", "Overview", "Design philosophy", "Features",
        "Syntax and semantics", "Syntax", "Semantics", "Code examples",
        "Standard library", "Libraries", "Typing", "Memory management",
        "Concurrency", "Object-oriented", "Functional", "Modules",
        "Data structures", "Algorithms", "Performance",
        "Applications", "Use cases", "Frameworks", "Tools",
        "Implementations", "Development environments",
    ]

    async def wiki_summary(title: str, client) -> dict:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)
        r = await client.get(url, headers=hdrs)
        return r.json() if r.status_code == 200 else {}

    def clean_paras(raw_html: str) -> list:
        out = []
        for p in re.findall(r"<p[^>]*>(.*?)</p>", raw_html, re.DOTALL):
            c = re.sub(r"<[^>]+>", "", p)
            c = re.sub(r"\[[\d\w\s,]+\]", "", c)
            c = re.sub(r"\s+", " ", c).strip()
            if len(c) < 80:
                continue
            if any(s.lower() in c.lower() for s in HIST_SIGNALS):
                continue
            out.append(c)
        return out

    async def wiki_sections(wiki_title: str, client) -> dict:
        url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(wiki_title.replace(" ", "_"))
        r = await client.get(url, headers={**hdrs, "Accept": "text/html,application/xhtml+xml"})
        if r.status_code != 200:
            return {}
        html = r.text
        # cut at first non-CS section
        cut = len(html)
        for sec in SKIP_SECS:
            m = re.search(rf'<h2[^>]*>\s*{re.escape(sec)}\s*</h2>', html, re.IGNORECASE)
            if m and m.start() < cut:
                cut = m.start()
        html_cs = html[:cut]
        # intro paragraphs (before first h2)
        fh2 = re.search(r"<h2[^>]*>", html_cs)
        result = {"__intro__": clean_paras(html_cs[:fh2.start()] if fh2 else html_cs)}
        # named CS sections
        for sname in CS_SECTION_NAMES:
            ms = re.search(rf'<h[23][^>]*>\s*{re.escape(sname)}[^<]*</h[23]>', html, re.IGNORECASE)
            if not ms:
                continue
            me = re.search(r"<h2[^>]*>", html[ms.end():], re.IGNORECASE)
            ep = ms.end() + (me.start() if me else len(html))
            ps = clean_paras(html[ms.start():ep])
            if ps:
                result[sname] = ps
        return result

    try:
        async with httpx.AsyncClient(timeout=14, follow_redirects=True, verify=False) as client:
            summary = {}
            used_title = search_topic
            for suffix in TECH_SUFFIXES:
                candidate = search_topic + suffix
                summary = await wiki_summary(candidate, client)
                if (
                    summary.get("type") == "standard"
                    and len(summary.get("extract", "")) > 80
                    and is_cs(summary)
                ):
                    used_title = summary.get("title", candidate)
                    break
            else:
                return JSONResponse({
                    "sections": [], "title": topic,
                    "error": (
                        f"No CS article found for \'{topic}\'. "
                        "Try a shorter term like \'Python\', \'React\', or \'Binary Search Tree\'."
                    ),
                })
            secs = await wiki_sections(used_title, client)

        # ── Build output sections ──────────────────────────────────────────
        sections = []
        definition = summary.get("extract", "").strip()

        # 1. Definition -- always shown
        if definition:
            sections.append({"heading": "Definition", "body": definition})

        # 2. Syntax & Types -- dedicated section
        syntax_paras = (
            secs.get("Syntax and semantics")
            or secs.get("Syntax")
            or secs.get("Semantics")
            or []
        )
        if syntax_paras:
            sections.append({
                "heading": "Syntax & Types",
                "body": " ".join(syntax_paras[:3]),
            })

        # 3. Design / Features
        design_paras = (
            secs.get("Design philosophy")
            or secs.get("Features")
            or secs.get("Overview")
            or []
        )
        if design_paras:
            sections.append({
                "heading": "Key features & design",
                "body": " ".join(design_paras[:2]),
            })

        # 4. Remaining CS content
        used = {s["body"][:60] for s in sections}
        remaining = []
        for src in [
            "__intro__", "Standard library", "Libraries", "Typing",
            "Memory management", "Concurrency", "Object-oriented",
            "Functional", "Applications", "Use cases",
            "Implementations", "Performance", "Data structures",
            "Algorithms", "Frameworks", "Tools",
        ]:
            for p in secs.get(src, []):
                k = p[:60]
                if k not in used and len(p) > 80:
                    remaining.append(p)
                    used.add(k)

        extra = [
            "Core concepts", "How it works",
            "Standard library & tools", "Performance & use cases", "Best practices",
        ]
        for i, heading in enumerate(extra):
            chunk = " ".join(remaining[i * 2: i * 2 + 2])
            if len(chunk) > 80:
                sections.append({"heading": heading, "body": chunk})

        if not sections:
            return JSONResponse({"sections": [], "title": topic})

        wiki_url = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        return JSONResponse({"title": used_title, "sections": sections, "source_url": wiki_url})

    except Exception as e:
        return JSONResponse({"sections": [], "error": str(e)})

class ForgeRequest(BaseModel):
    topic: str


@app.post("/demo/forge")
async def demo_forge(body: ForgeRequest):
    topic = body.topic.strip() or "Python"
    return HTMLResponse(content=_build_workspace_html(topic))


@app.get("/workspace")
async def workspace(topic: str = "Python"):
    return HTMLResponse(content=_build_workspace_html(topic.strip() or "Python"))


# ── Login page ─────────────────────────────────────────────────────────────
@app.get("/login")
async def login_page():
    return HTMLResponse(content=_build_login_html())


# ── Landing page ──────────────────────────────────────────────────────────
_root = Path(__file__).parent.parent


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(str(_root / "index.html"))


# ═══════════════════════════════════════════════════════════════════════════
# HTML BUILDERS  (imported from pages.py)
# ═══════════════════════════════════════════════════════════════════════════
from app.pages import _build_login_html, _build_workspace_html  # noqa: E402
