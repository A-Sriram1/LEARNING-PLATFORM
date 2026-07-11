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

    # Smart search candidates: try programming/CS-specific title first
    tech_suffixes = [
        " (programming language)",
        " (software)",
        " (computer science)",
        " (programming)",
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
        raw = re.findall(r"<p[^>]*>(.*?)</p>", r.text, re.DOTALL)
        paras = []
        for p in raw:
            clean = re.sub(r"<[^>]+>", "", p)
            clean = re.sub(r"\[[\d\w\s,]+\]", "", clean)
            clean = re.sub(r"\s+", " ", clean).strip()
            if len(clean) > 100:
                paras.append(clean)
        return paras

    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True, verify=False) as client:
            summary = {}
            used_title = topic

            # Try tech-specific titles first to avoid disambiguation
            for suffix in tech_suffixes:
                candidate = topic + suffix
                summary = await fetch_wiki_summary(candidate, client)
                if summary.get("type") == "standard" and len(summary.get("extract", "")) > 100:
                    used_title = summary.get("title", candidate)
                    break

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
        depth_paras = [p for p in wiki_paras if p not in intro][:12]

        headings = [
            "Key concepts",
            "How it works",
            "Core features",
            "Applications & use cases",
            "Advantages",
            "Important considerations",
        ]
        for i, heading in enumerate(headings):
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
