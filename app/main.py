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


# ── Theory content — Wikipedia REST summary + HTML scrape ─────────────────
@app.get("/api/theory")
async def get_theory(topic: str):
    import urllib.parse

    hdrs = {
        # Wikipedia policy requires a descriptive User-Agent, not a browser UA.
        # Generic browser strings get 403'd. See: https://meta.wikimedia.org/wiki/User-Agent_policy
        "User-Agent": (
            "SkillForgeAI/1.0 "
            "(https://github.com/RSAKTHISABARISH/LEARNING-PLATFORM; "
            "skillforge-ai-app) python-httpx/0.27"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # CS-related categories/keywords that confirm an article is about computing
    CS_CONFIRM_KEYWORDS = [
        "programming language", "software", "computer science", "computing",
        "algorithm", "data structure", "framework", "library", "runtime",
        "compiler", "interpreter", "operating system", "database", "network",
        "machine learning", "artificial intelligence", "web", "api",
        "object-oriented", "functional programming", "syntax", "semantics",
        "open-source", "open source", "source code", "developer", "codebase",
    ]

    def is_cs_article(summary: dict) -> bool:
        """Return True only if the Wikipedia summary looks like a CS article."""
        text = (summary.get("extract", "") + " " + summary.get("description", "")).lower()
        return any(kw in text for kw in CS_CONFIRM_KEYWORDS)

    # Smart search candidates: try programming/CS-specific title first
    tech_suffixes = [
        " (programming language)",
        " (software)",
        " (computer science)",
        " (programming)",
        " (data structure)",
        " (algorithm)",
        " (computing)",
        " (framework)",
        "",
    ]

    async def fetch_wiki_summary(title: str, client) -> dict:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)
        r = await client.get(url, headers=hdrs)
        if r.status_code == 200:
            return r.json()
        return {}

    async def fetch_wiki_html_paras(title: str, client) -> list:
        url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        r = await client.get(url, headers={**hdrs, "Accept": "text/html,application/xhtml+xml"})
        if r.status_code != 200:
            return []

        html = r.text

        # ── Cut at the first non-CS section ───────────────────────────────
        skip_sections = [
            "History", "Etymology", "Reception", "Awards", "Legacy",
            "Naming", "Language development", "Languages influenced",
            "Controversy", "Cultural", "Biography", "Personal life",
            "Early life", "See also", "References", "Notes",
            "Further reading", "External links",
        ]
        earliest_cut = len(html)
        for sec in skip_sections:
            m = re.search(
                rf'<h2[^>]*>\s*{re.escape(sec)}\s*</h2>',
                html, re.IGNORECASE
            )
            if m and m.start() < earliest_cut:
                earliest_cut = m.start()

        html_trimmed = html[:earliest_cut]

        raw = re.findall(r"<p[^>]*>(.*?)</p>", html_trimmed, re.DOTALL)
        paras = []

        # Signals that a paragraph is about history/biography, not CS
        history_signals = [
            "was born", "in the late 1980s", "in the 1990s", "in the 2000s",
            "created by", "invented by", "developed by", "designed by",
            "named after", "named for", "released in 19", "released in 20",
            "first appeared", "initial release", "version 1.", "version 2.",
            "van Rossum", "Guido", "Bjarne", "James Gosling",
        ]

        for p in raw:
            clean = re.sub(r"<[^>]+>", "", p)
            clean = re.sub(r"\[[\d\w\s,]+\]", "", clean)
            clean = re.sub(r"\s+", " ", clean).strip()
            if len(clean) < 100:
                continue
            if any(sig.lower() in clean.lower() for sig in history_signals):
                continue
            paras.append(clean)

        # ── Fallback: if History cut left too few paras, scrape CS sections ──
        # Pull paragraphs from specifically technical sections only.
        if len(paras) < 4:
            cs_section_names = [
                "Design philosophy", "Features", "Syntax", "Semantics",
                "Libraries", "Standard library", "Implementations",
                "Development environment", "Typing", "Memory management",
                "Concurrency", "Object-oriented", "Functional", "Modules",
                "Data structures", "Algorithms", "Performance",
                "Applications", "Use cases", "Frameworks", "Tools",
            ]
            for sec_name in cs_section_names:
                # Find the section in the full HTML
                m_start = re.search(
                    rf'<h[23][^>]*>\s*{re.escape(sec_name)}[^<]*</h[23]>',
                    html, re.IGNORECASE
                )
                if not m_start:
                    continue
                # Find where the next h2 starts (end of this section)
                m_end = re.search(r'<h2[^>]*>', html[m_start.end():], re.IGNORECASE)
                end_pos = m_start.end() + (m_end.start() if m_end else len(html))
                section_html = html[m_start.start():end_pos]
                for p in re.findall(r"<p[^>]*>(.*?)</p>", section_html, re.DOTALL):
                    clean = re.sub(r"<[^>]+>", "", p)
                    clean = re.sub(r"\[[\d\w\s,]+\]", "", clean)
                    clean = re.sub(r"\s+", " ", clean).strip()
                    if len(clean) > 100 and clean not in paras:
                        paras.append(clean)
                if len(paras) >= 8:
                    break

        return paras

    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True, verify=False) as client:
            summary = {}
            used_title = topic

            # Try tech-specific titles first to avoid disambiguation
            for suffix in tech_suffixes:
                candidate = topic + suffix
                summary = await fetch_wiki_summary(candidate, client)
                if (
                    summary.get("type") == "standard"
                    and len(summary.get("extract", "")) > 80
                    and is_cs_article(summary)
                ):
                    used_title = summary.get("title", candidate)
                    break
            else:
                # No CS article found — return empty so the frontend shows a helpful message
                return JSONResponse({
                    "sections": [],
                    "title": topic,
                    "error": f"No computer science article found for '{topic}'. Try a more specific term like 'Python programming language'."
                })

            # Fetch full HTML paragraphs for depth
            wiki_paras = await fetch_wiki_html_paras(used_title, client)

        # Build sections
        sections = []
        intro = summary.get("extract", "").strip()
        if intro:
            sections.append({
                "heading": f"What is {used_title}?",
                "body": intro,
            })

        # Fill remaining sections from HTML paragraphs (skip first if it duplicates intro)
        depth_paras = [p for p in wiki_paras if p not in intro][:14]

        # CS-specific section headings
        cs_headings = [
            "Core concepts",
            "How it works",
            "Key features",
            "Syntax & structure",
            "Standard library & tools",
            "Performance & use cases",
            "Best practices",
        ]
        for i, heading in enumerate(cs_headings):
            start = i * 2
            chunk = " ".join(depth_paras[start:start + 2])
            if len(chunk) > 80:
                sections.append({"heading": heading, "body": chunk})

        if not sections:
            return JSONResponse({"sections": [], "title": topic})

        wiki_url = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        return JSONResponse({
            "title": used_title,
            "sections": sections,
            "source_url": wiki_url,
        })

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
