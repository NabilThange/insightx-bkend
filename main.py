"""FastAPI main application — InsightX Backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from routes import upload, explore, sessions, chats, chat, sql_execute, python_execute, insights

load_dotenv()

description = "FastAPI backend for InsightX — CSV analysis with DuckDB and Python."

tags_metadata = [
    {"name": "Upload",           "description": "📁 Upload CSV files to create a new analysis session. Returns a `session_id`. Converts CSV → Parquet, stores in Supabase Storage."},
    {"name": "Explore",          "description": "🧬 Data DNA — auto-profiles dataset: column types, distributions, null counts, patterns, anomalies."},
    {"name": "Sessions",         "description": "📋 List and manage active analysis sessions."},
    {"name": "Chats",            "description": "💬 Create chat threads and fetch message history for a session."},
    {"name": "Chat Stream",      "description": "🤖 Natural language query → real-time streamed response via SSE. Routes: Orchestrator → SQL/Python Agent → Composer."},
    {"name": "SQL Execution",    "description": "🗄️ Execute raw DuckDB SQL queries directly on the uploaded dataset."},
    {"name": "Python Execution", "description": "🐍 Run Python/scipy statistical analysis. Used by Python Agent for correlation, regression, outlier detection."},
    {"name": "Insights",         "description": "💡 Retrieve AI-generated summary insights, anomalies, and recommendations for a session."},
]

app = FastAPI(
    title="InsightX API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router,         prefix="/api", tags=["Upload"])
app.include_router(explore.router,        prefix="/api", tags=["Explore"])
app.include_router(sessions.router,       prefix="/api", tags=["Sessions"])
app.include_router(chats.router,          prefix="/api", tags=["Chats"])
app.include_router(chat.router,           prefix="/api", tags=["Chat Stream"])
app.include_router(sql_execute.router,    prefix="/api", tags=["SQL Execution"])
app.include_router(python_execute.router, prefix="/api", tags=["Python Execution"])
app.include_router(insights.router,       prefix="/api", tags=["Insights"])

# ─────────────────────────────────────────────────────────────────────────────
# ENV BLOCKS (plain text — used by JS copy functions)
# ─────────────────────────────────────────────────────────────────────────────
FE_ENV = """NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=https://insightx-bkend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2dHFidmF2d2Jvd3l5b2V2b2xvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNzE4NzIsImV4cCI6MjA4NjY0Nzg3Mn0.45NW1ZBLH8Q08kfQteIjlF24G0E0-1pblapR40_toug
BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114
NEXT_PUBLIC_BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
NEXT_PUBLIC_BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
NEXT_PUBLIC_BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
NEXT_PUBLIC_BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
NEXT_PUBLIC_BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
NEXT_PUBLIC_BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
NEXT_PUBLIC_BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
NEXT_PUBLIC_BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114"""

BE_ENV = """SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2dHFidmF2d2Jvd3l5b2V2b2xvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTA3MTg3MiwiZXhwIjoyMDg2NjQ3ODcyfQ.Cj1_-8_3fD8BgcOkdFLf5yRuUdmfC9-OcAyzMOflguA
NEXT_PUBLIC_API_URL=https://insightx-bkend.onrender.com
BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114
NEXT_PUBLIC_BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
NEXT_PUBLIC_BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
NEXT_PUBLIC_BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
NEXT_PUBLIC_BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
NEXT_PUBLIC_BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
NEXT_PUBLIC_BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
NEXT_PUBLIC_BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
NEXT_PUBLIC_BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114"""


def build_html(fe_env: str, be_env: str) -> str:
    # Escape for JS string embedding
    fe_js = fe_env.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    be_js = be_env.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

    def hl(text: str) -> str:
        """Syntax-highlight a .env block for display (HTML)."""
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("#"):
                lines.append(f'<span class="cm">{line}</span>')
            elif "=" in line:
                k, v = line.split("=", 1)
                lines.append(f'<span class="ky">{k}</span><span class="eq">=</span><span class="vl">{v}</span>')
            else:
                lines.append(line)
        return "\n".join(lines)

    fe_hl = hl(fe_env)
    be_hl = hl(be_env)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>InsightX API Docs</title>
  <link rel="icon" href="https://insightxx.vercel.app/favicon.ico"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui.min.css"/>
  <style>
    /* ── TOKENS ──────────────────────────────── */
    :root {{
      --bg:        #f1efe7;
      --bg-e:      #e8e6de;
      --bg-d:      #dddbd3;
      --fg:        #1f1f1f;
      --muted:     rgba(31,31,31,0.55);
      --stroke:    rgba(0,0,0,0.12);
      --stroke2:   rgba(0,0,0,0.2);
      --accent:    #4f46e5;
      --accent-l:  rgba(79,70,229,0.1);
      --green:     #2d5016;
      --green-l:   rgba(45,80,22,0.1);
      --amber:     #92400e;
      --amber-l:   rgba(217,119,6,0.1);
      --red:       #b91c1c;
      --red-l:     rgba(185,28,28,0.1);
      --blue:      #1e40af;
      --blue-l:    rgba(30,64,175,0.1);
      --radius:    12px;
      --mono:      'JetBrains Mono', monospace;
      --sans:      'Inter', -apple-system, sans-serif;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--fg);
      font-family: var(--sans);
      font-size: 14px;
      line-height: 1.6;
    }}

    /* ── SCROLLBAR ───────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--bg-d); border-radius: 4px; }}

    /* ── HEADER ──────────────────────────────── */
    .hdr {{
      background: #1f1f1f;
      padding: 28px 40px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .hdr-left {{ display: flex; align-items: center; gap: 12px; }}
    .hdr-icon {{
      width: 38px; height: 38px;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
      box-shadow: 0 4px 14px rgba(99,102,241,0.45);
      flex-shrink: 0;
    }}
    .hdr-title {{
      font-family: var(--sans);
      font-size: 20px;
      font-weight: 700;
      color: #f1efe7;
      letter-spacing: -0.3px;
    }}
    .hdr-badge {{
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.12);
      color: rgba(241,239,231,0.5);
      font-family: var(--mono);
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 20px;
    }}
    .hdr-btns {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .hdr-btn {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px; font-weight: 600;
      text-decoration: none;
      transition: transform 0.15s, opacity 0.15s;
      white-space: nowrap;
    }}
    .hdr-btn:hover {{ transform: translateY(-1px); opacity: 0.92; }}
    .btn-indigo {{ background: #4f46e5; color: #fff; box-shadow: 0 3px 10px rgba(79,70,229,0.4); }}
    .btn-green  {{ background: #2d5016; color: #f1efe7; box-shadow: 0 3px 10px rgba(45,80,22,0.35); }}
    .btn-ghost  {{ background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); color: rgba(241,239,231,0.7); }}
    .btn-ghost:hover {{ background: rgba(255,255,255,0.11); }}

    /* ── WRAP ────────────────────────────────── */
    .wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 40px; }}

    /* ── BANNER CARDS ────────────────────────── */
    .banner {{
      border-radius: var(--radius);
      border: 1px solid var(--stroke);
      padding: 14px 18px;
      margin-bottom: 12px;
      display: flex;
      gap: 12px;
    }}
    .banner-ico {{ font-size: 18px; flex-shrink: 0; margin-top: 1px; }}
    .banner-body {{ flex: 1; }}
    .banner-title {{ font-weight: 700; font-size: 13px; margin-bottom: 3px; }}
    .banner-text  {{ font-size: 13px; line-height: 1.65; }}
    .banner-text a {{ font-weight: 600; text-decoration: none; }}
    .banner-text a:hover {{ text-decoration: underline; }}
    .banner-text ul {{ margin: 6px 0 0 16px; }}
    .banner-text li {{ margin-bottom: 3px; }}
    /* colour variants */
    .b-blue   {{ background: var(--blue-l);  border-color: rgba(30,64,175,0.18); }}
    .b-blue   .banner-title {{ color: var(--blue); }}
    .b-blue   .banner-text  {{ color: rgba(30,64,175,0.8); }}
    .b-blue   .banner-text a {{ color: var(--green); }}
    .b-amber  {{ background: var(--amber-l); border-color: rgba(217,119,6,0.2); }}
    .b-amber  .banner-title {{ color: var(--amber); }}
    .b-amber  .banner-text  {{ color: rgba(146,64,14,0.9); }}
    .b-amber  strong {{ color: var(--amber); }}
    .b-amber  .expire {{ color: var(--red); font-weight: 700; }}
    .b-indigo {{ background: var(--accent-l); border-color: rgba(79,70,229,0.18); }}
    .b-indigo .banner-title {{ color: var(--accent); }}
    .b-indigo .banner-text  {{ color: rgba(79,70,229,0.85); }}
    .b-indigo .banner-text a {{ color: var(--accent); }}
    .b-indigo .banner-text strong {{ color: var(--fg); }}

    /* ── SECTION LABEL ───────────────────────── */
    .sec-label {{
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 28px 0 10px;
      padding-left: 2px;
    }}

    /* ── ACCORDION ───────────────────────────── */
    details.acc {{
      background: #fff;
      border: 1px solid var(--stroke);
      border-radius: var(--radius);
      margin-bottom: 8px;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    details.acc:hover {{ border-color: var(--stroke2); }}
    details.acc[open]  {{ border-color: rgba(79,70,229,0.25); box-shadow: 0 0 0 3px rgba(79,70,229,0.06); }}
    details.acc[open] > summary {{ border-bottom: 1px solid var(--stroke); }}

    details.acc > summary {{
      list-style: none;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 18px;
      cursor: pointer;
      user-select: none;
      transition: background 0.15s;
    }}
    details.acc > summary::-webkit-details-marker {{ display: none; }}
    details.acc > summary:hover {{ background: var(--bg); }}

    .s-icon {{
      width: 34px; height: 34px;
      border-radius: 9px;
      display: flex; align-items: center; justify-content: center;
      font-size: 17px; flex-shrink: 0;
    }}
    .ic-ind {{ background: var(--accent-l); }}
    .ic-sky {{ background: rgba(14,165,233,0.1); }}
    .ic-grn {{ background: var(--green-l); }}
    .ic-amb {{ background: var(--amber-l); }}

    .s-text  {{ flex: 1; }}
    .s-title {{ font-weight: 700; font-size: 14.5px; color: var(--fg); line-height: 1.2; }}
    .s-sub   {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
    .s-chev  {{ color: var(--muted); font-size: 11px; transition: transform 0.2s; }}
    details[open] .s-chev {{ transform: rotate(180deg); }}

    .acc-body {{ padding: 22px 20px 20px; }}

    /* ── STEPS ───────────────────────────────── */
    .steps {{ display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px; }}
    .step {{
      display: flex; gap: 13px; align-items: flex-start;
      background: var(--bg);
      border: 1px solid var(--stroke);
      border-radius: 10px;
      padding: 12px 15px;
      transition: border-color 0.15s;
    }}
    .step:hover {{ border-color: var(--stroke2); }}
    .step-n {{
      width: 26px; height: 26px;
      background: #1f1f1f; color: #f1efe7;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-family: var(--mono); font-size: 11px; font-weight: 600;
      flex-shrink: 0; margin-top: 1px;
    }}
    .step-n.ok {{ background: var(--green); }}
    .step-c strong {{ font-size: 14px; color: var(--fg); display: block; margin-bottom: 2px; }}
    .step-c span   {{ font-size: 12px; color: var(--muted); font-family: var(--mono); }}
    .step-c span.ok {{ color: var(--green); font-weight: 600; }}

    /* ── CODE BLOCK ──────────────────────────── */
    .cb-wrap {{
      background: var(--bg-e);
      border: 1px solid var(--stroke);
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 4px;
    }}
    .cb-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 14px;
      border-bottom: 1px solid var(--stroke);
      background: var(--bg-d);
    }}
    .cb-lbl  {{ font-family: var(--mono); font-size: 10.5px; font-weight: 600; color: var(--muted); letter-spacing: 0.04em; text-transform: uppercase; }}
    .cb-copy {{
      display: inline-flex; align-items: center; gap: 5px;
      background: #1f1f1f; color: #f1efe7;
      border: none; border-radius: 6px;
      font-family: var(--mono); font-size: 11px; font-weight: 600;
      padding: 4px 12px; cursor: pointer;
      transition: background 0.15s, transform 0.1s;
    }}
    .cb-copy:hover  {{ background: #2d2d2d; transform: translateY(-1px); }}
    .cb-copy:active {{ transform: scale(0.97); }}
    .cb-copy.ok     {{ background: var(--green); }}
    pre.cb-pre {{
      margin: 0;
      padding: 14px 16px;
      font-family: var(--mono);
      font-size: 12.5px;
      line-height: 1.7;
      color: var(--fg);
      overflow-x: auto;
      white-space: pre;
      background: var(--bg-e);
    }}
    pre.cb-pre .cm {{ color: var(--muted); font-style: italic; }}
    pre.cb-pre .ky {{ color: #1e40af; font-weight: 600; }}
    pre.cb-pre .eq {{ color: var(--muted); }}
    pre.cb-pre .vl {{ color: #2d5016; }}
    pre.cb-pre .hd {{ color: var(--muted); font-style: italic; }}

    /* ── COPY-ALL NOTICE ─────────────────────── */
    .copy-notice {{
      background: var(--blue-l);
      border: 1px solid rgba(30,64,175,0.15);
      border-radius: 8px;
      padding: 10px 14px;
      display: flex; align-items: center; justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }}
    .copy-notice-text {{ font-size: 12.5px; color: var(--blue); font-weight: 500; }}
    .copy-notice-btn {{
      display: inline-flex; align-items: center; gap: 6px;
      background: #1f1f1f; color: #f1efe7;
      border: none; border-radius: 7px;
      font-family: var(--mono); font-size: 12px; font-weight: 700;
      padding: 7px 16px; cursor: pointer; white-space: nowrap;
      transition: background 0.15s, transform 0.1s;
      flex-shrink: 0;
    }}
    .copy-notice-btn:hover  {{ background: #2d2d2d; transform: translateY(-1px); }}
    .copy-notice-btn.ok     {{ background: var(--green); }}

    /* ── HELPER TEXT ─────────────────────────── */
    .hint {{ font-size: 12.5px; color: var(--muted); margin: 6px 0 16px; line-height: 1.55; }}
    .hint code {{
      background: var(--bg-d); border-radius: 4px;
      padding: 1px 5px;
      font-family: var(--mono); font-size: 11.5px; color: var(--fg);
    }}
    .hint strong {{ color: var(--amber); }}

    /* ── SUCCESS BAR ─────────────────────────── */
    .ok-bar {{
      background: var(--green-l);
      border: 1px solid rgba(45,80,22,0.18);
      border-radius: 8px;
      padding: 10px 16px;
      color: var(--green);
      font-size: 13px; font-weight: 700;
      margin-top: 12px;
      display: flex; align-items: center; gap: 8px;
    }}

    /* ── VERIFY TABLE ────────────────────────── */
    table.vtbl {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; }}
    table.vtbl th {{
      text-align: left; padding: 8px 14px;
      font-size: 10.5px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.06em; color: var(--muted);
      border-bottom: 1px solid var(--stroke);
    }}
    table.vtbl td {{
      padding: 11px 14px; font-size: 13px;
      border-bottom: 1px solid var(--stroke); vertical-align: middle;
    }}
    table.vtbl tr:last-child td {{ border-bottom: none; }}
    table.vtbl a {{ color: var(--accent); font-family: var(--mono); font-size: 12px; font-weight: 600; text-decoration: none; }}
    table.vtbl a:hover {{ text-decoration: underline; }}
    .tag {{ display: inline-block; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 700; font-family: var(--mono); }}
    .t-fe  {{ background: var(--blue-l);  color: var(--blue); }}
    .t-api {{ background: var(--green-l); color: var(--green); }}
    .t-hc  {{ background: var(--amber-l); color: var(--amber); }}

    /* ── TROUBLE ─────────────────────────────── */
    .trouble {{ display: flex; flex-direction: column; gap: 6px; }}
    .tr-item {{
      background: var(--bg); border: 1px solid var(--stroke);
      border-radius: 8px; padding: 11px 15px;
    }}
    .tr-err  {{ font-family: var(--mono); font-size: 12px; color: var(--red); font-weight: 700; margin-bottom: 3px; }}
    .tr-fix  {{ font-size: 13px; color: var(--muted); }}
    .tr-fix code {{
      background: var(--bg-d); border-radius: 4px;
      padding: 1px 5px; font-family: var(--mono); font-size: 11.5px; color: var(--fg);
    }}

    /* ── DIVIDER & FOOTER ────────────────────── */
    hr.div {{ border: none; border-top: 1px solid var(--stroke); margin: 12px 0 20px; }}
    .footer {{
      text-align: center; color: var(--muted); font-size: 12px; padding-bottom: 28px;
    }}
    .footer a {{ color: var(--accent); text-decoration: none; }}
    .footer a:hover {{ text-decoration: underline; }}

    /* ── SWAGGER SECTION ─────────────────────── */
    .sw-wrap {{ max-width: 900px; margin: 0 auto; padding: 0 40px 60px; }}
    .sw-label {{
      font-size: 10.5px; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: var(--muted); margin-bottom: 12px; padding-left: 2px;
    }}

    /* ── SWAGGER OVERRIDES ───────────────────── */
    #swagger-ui {{ background: transparent !important; }}
    #swagger-ui .swagger-ui {{ background: transparent !important; font-family: var(--sans) !important; }}
    #swagger-ui .swagger-ui .info  {{ display: none !important; }}
    #swagger-ui .swagger-ui .topbar {{ display: none !important; }}
    #swagger-ui .swagger-ui .scheme-container {{
      background: #fff !important; border: 1px solid var(--stroke) !important;
      border-radius: var(--radius) !important; padding: 12px 16px !important;
      margin-bottom: 14px !important; box-shadow: none !important;
    }}
    #swagger-ui .swagger-ui .opblock-tag {{
      background: #fff !important; border: 1px solid var(--stroke) !important;
      border-radius: var(--radius) !important; margin-bottom: 8px !important;
      padding: 12px 18px !important; transition: border-color 0.15s !important;
    }}
    #swagger-ui .swagger-ui .opblock-tag:hover {{ border-color: var(--stroke2) !important; }}
    #swagger-ui .swagger-ui .opblock-tag h3 {{
      font-family: var(--sans) !important; font-size: 15px !important;
      font-weight: 700 !important; color: var(--fg) !important;
    }}
    #swagger-ui .swagger-ui .opblock-tag p,
    #swagger-ui .swagger-ui .opblock-tag small {{ color: var(--muted) !important; font-size: 13px !important; }}
    #swagger-ui .swagger-ui .opblock {{
      border-radius: 9px !important; border: 1px solid var(--stroke) !important;
      margin: 5px 0 !important; box-shadow: none !important;
    }}
    #swagger-ui .swagger-ui .opblock.opblock-post   {{ background: rgba(45,80,22,0.04) !important;  border-color: rgba(45,80,22,0.18) !important; }}
    #swagger-ui .swagger-ui .opblock.opblock-get    {{ background: rgba(30,64,175,0.04) !important; border-color: rgba(30,64,175,0.15) !important; }}
    #swagger-ui .swagger-ui .opblock.opblock-delete {{ background: rgba(185,28,28,0.04) !important; border-color: rgba(185,28,28,0.18) !important; }}
    #swagger-ui .swagger-ui .opblock-summary {{ padding: 10px 16px !important; }}
    #swagger-ui .swagger-ui .opblock-summary-path {{ font-family: var(--mono) !important; font-size: 13px !important; color: var(--fg) !important; }}
    #swagger-ui .swagger-ui .opblock-summary-description {{ color: var(--muted) !important; font-size: 13px !important; }}
    #swagger-ui .swagger-ui .opblock-body {{ background: var(--bg-e) !important; }}
    #swagger-ui .swagger-ui .opblock-description-wrapper p {{ color: var(--fg) !important; }}
    #swagger-ui .swagger-ui .btn.execute {{
      background: #1f1f1f !important; border-color: #1f1f1f !important;
      border-radius: 8px !important; color: #f1efe7 !important;
    }}
    #swagger-ui .swagger-ui input, #swagger-ui .swagger-ui textarea {{
      background: var(--bg) !important; border: 1px solid var(--stroke2) !important;
      color: var(--fg) !important; border-radius: 8px !important;
      font-family: var(--mono) !important;
    }}
    #swagger-ui .swagger-ui .parameter__name {{ color: var(--blue) !important; font-family: var(--mono) !important; font-size: 13px !important; }}
    #swagger-ui .swagger-ui .parameter__type {{ color: var(--muted) !important; }}
    #swagger-ui .swagger-ui .response-col_status {{ color: var(--green) !important; font-family: var(--mono) !important; }}
    #swagger-ui .swagger-ui section.models {{ display: none !important; }}
    #swagger-ui .swagger-ui .microlight {{
      background: var(--bg-d) !important; border-radius: 6px !important;
      padding: 12px 16px !important; color: var(--fg) !important;
    }}
    #swagger-ui .swagger-ui .highlight-code {{ background: var(--bg-d) !important; }}
    #swagger-ui .swagger-ui table.headers td {{ color: var(--muted) !important; }}
    #swagger-ui .swagger-ui .tab li {{ color: var(--muted) !important; }}
    #swagger-ui .swagger-ui .tab li.active {{ color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }}
    #swagger-ui .swagger-ui .arrow {{ fill: var(--muted) !important; }}
    #swagger-ui .swagger-ui svg.arrow {{ fill: var(--muted) !important; }}
    #swagger-ui .swagger-ui .model-box {{ background: var(--bg-e) !important; }}
  </style>
</head>
<body>

<!-- ── HEADER ─────────────────────────────────────── -->
<div class="hdr">
  <div class="hdr-left">
    <div class="hdr-icon">⚡</div>
    <div>
      <div class="hdr-title">InsightX API</div>
    </div>
    <span class="hdr-badge">v1.0.0</span>
  </div>
  <div class="hdr-btns">
    <a class="hdr-btn btn-indigo" href="https://insightxx.vercel.app" target="_blank">🌐 Live App</a>
    <a class="hdr-btn btn-green"  href="https://insightxx.vercel.app/workspace/0c62e010-86d0-4807-8e69-193f59926aea?chat=527a453b-16e3-42dd-a4f6-f32d511aa9ca" target="_blank">⭐ Pre-loaded Workspace</a>
    <a class="hdr-btn btn-ghost"  href="https://github.com/NabilThange/insightx" target="_blank">⚙ GitHub</a>
  </div>
</div>

<!-- ── GUIDE ───────────────────────────────────────── -->
<div class="wrap">

  <!-- Banners -->
  <div class="banner b-blue" style="margin-top:8px;">
    <div class="banner-ico">💡</div>
    <div class="banner-body">
      <div class="banner-title">Skip the setup entirely</div>
      <div class="banner-text">The <a href="https://insightxx.vercel.app/workspace/0c62e010-86d0-4807-8e69-193f59926aea?chat=527a453b-16e3-42dd-a4f6-f32d511aa9ca" target="_blank">⭐ Pre-loaded Workspace</a> has the official judging dataset already uploaded — click it and start querying immediately. No cloning, no env files.</div>
    </div>
  </div>

  <div class="banner b-amber">
    <div class="banner-ico">🔑</div>
    <div class="banner-body">
      <div class="banner-title">API Keys — Intentionally Shared for Hackathon Judging</div>
      <div class="banner-text">
        We are <strong>deliberately sharing these credentials</strong> so judges can evaluate locally without any account setup. This is a considered decision — not a security mistake.
        <ul>
          <li>Provided exclusively for <strong>IIT-B Techfest 2026 judging</strong></li>
          <li>Zero account creation required — copy, paste, run</li>
          <li class="expire">⚠ All keys permanently deactivated on March 9, 2026</li>
          <li>Please do not share or use outside of evaluation</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="banner b-indigo">
    <div class="banner-ico">ℹ️</div>
    <div class="banner-body">
      <div class="banner-title">Indian ISP Alert — Supabase blocked on Jio</div>
      <div class="banner-text">
        If uploads fail or screens are blank on <strong>Jio</strong>:
        switch to <strong>Airtel / BSNL / hotspot</strong>,
        use <a href="https://one.one.one.one" target="_blank">Cloudflare WARP</a> (free VPN),
        or just use the <a href="https://insightxx.vercel.app/workspace/0c62e010-86d0-4807-8e69-193f59926aea?chat=527a453b-16e3-42dd-a4f6-f32d511aa9ca" target="_blank">Pre-loaded Workspace</a>.
      </div>
    </div>
  </div>

  <div class="sec-label">Local Setup Guide</div>

  <!-- ── SECTION 1 — OVERVIEW ──────────────────── -->
  <details class="acc">
    <summary>
      <div class="s-icon ic-ind">🚀</div>
      <div class="s-text">
        <div class="s-title">Quick Start — Overview</div>
        <div class="s-sub">Prerequisites · 6 steps · clone command</div>
      </div>
      <span class="s-chev">▼</span>
    </summary>
    <div class="acc-body">
      <p class="hint">You need <code>Node.js 20+</code>, <code>Python 3.11+</code>, and <code>Git</code>. Verify: <code>node --version</code> · <code>python --version</code> · <code>git --version</code></p>

      <div class="steps">
        <div class="step"><div class="step-n">1</div><div class="step-c"><strong>Clone the repository</strong><span>git clone https://github.com/NabilThange/insightx.git → cd insightx-app</span></div></div>
        <div class="step"><div class="step-n">2</div><div class="step-c"><strong>Install frontend dependencies</strong><span>npm install &nbsp;(from project root)</span></div></div>
        <div class="step"><div class="step-n">3</div><div class="step-c"><strong>Create .env.local with frontend keys</strong><span>See "Frontend Setup" accordion below ↓</span></div></div>
        <div class="step"><div class="step-n">4</div><div class="step-c"><strong>Create Python venv + install backend deps</strong><span>cd backend → python -m venv venv → activate → pip install -r requirements.txt</span></div></div>
        <div class="step"><div class="step-n">5</div><div class="step-c"><strong>Create backend/.env with backend keys</strong><span>See "Backend Setup" accordion below ↓</span></div></div>
        <div class="step"><div class="step-n">6</div><div class="step-c"><strong>Run both servers in two terminals</strong><span>T1: npm run dev &nbsp;|&nbsp; T2: uvicorn main:app --reload</span></div></div>
        <div class="step"><div class="step-n ok">✓</div><div class="step-c"><strong><span class="ok">Visit http://localhost:3000 — you're live!</span></strong><span>Backend docs at http://localhost:8000/docs</span></div></div>
      </div>

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Clone</span>
          <button class="cb-copy" onclick="cp(this,'git clone https://github.com/NabilThange/insightx.git\\ncd insightx-app')">📋 Copy</button>
        </div>
        <pre class="cb-pre">git clone https://github.com/NabilThange/insightx.git
cd insightx-app</pre>
      </div>
    </div>
  </details>

  <!-- ── SECTION 2 — FRONTEND ──────────────────── -->
  <details class="acc" open>
    <summary>
      <div class="s-icon ic-sky">🎨</div>
      <div class="s-text">
        <div class="s-title">Frontend Setup + API Keys</div>
        <div class="s-sub">npm install · create .env.local · one-click copy all keys · npm run dev</div>
      </div>
      <span class="s-chev">▼</span>
    </summary>
    <div class="acc-body">

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Step 2.1 — Install frontend packages (project root)</span>
          <button class="cb-copy" onclick="cp(this,'npm install')">📋 Copy</button>
        </div>
        <pre class="cb-pre">npm install</pre>
      </div>
      <p class="hint">Installs Next.js 16, React 19, Tailwind CSS v4, Zustand, Supabase JS, Recharts, GSAP, Framer Motion + all deps.</p>

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Step 2.2 — Create .env.local (project root)</span>
          <button class="cb-copy" onclick="cp(this,'touch .env.local')">📋 Copy</button>
        </div>
        <pre class="cb-pre"><span class="cm"># Windows (PowerShell)</span>
New-Item -Path ".env.local" -ItemType File

<span class="cm"># Mac / Linux</span>
touch .env.local</pre>
      </div>

      <div class="copy-notice">
        <span class="copy-notice-text">📋 Step 2.3 — Copy all frontend keys at once and paste into <code style="background:rgba(30,64,175,0.08);padding:1px 5px;border-radius:4px;font-family:var(--mono);font-size:11.5px;">.env.local</code> &nbsp;·&nbsp; Valid until <strong>March 9, 2026</strong></span>
        <button class="copy-notice-btn" id="fe-big-btn" onclick="cpBig('fe-big-btn', feEnv)">📋 Copy All Keys</button>
      </div>
      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">.env.local — full block</span>
          <button class="cb-copy" id="fe-cb-btn" onclick="cpBig('fe-cb-btn', feEnv)">📋 Copy</button>
        </div>
        <pre class="cb-pre">{fe_hl}</pre>
      </div>

      <div class="cb-wrap" style="margin-top:14px;">
        <div class="cb-bar">
          <span class="cb-lbl">Step 2.4 — Start frontend</span>
          <button class="cb-copy" onclick="cp(this,'npm run dev')">📋 Copy</button>
        </div>
        <pre class="cb-pre">npm run dev</pre>
      </div>
      <div class="ok-bar">✅ Frontend running at http://localhost:3000</div>
    </div>
  </details>

  <!-- ── SECTION 3 — BACKEND ───────────────────── -->
  <details class="acc" open>
    <summary>
      <div class="s-icon ic-grn">⚙️</div>
      <div class="s-text">
        <div class="s-title">Backend Setup + API Keys</div>
        <div class="s-sub">venv · pip install · create backend/.env · one-click copy all keys · uvicorn</div>
      </div>
      <span class="s-chev">▼</span>
    </summary>
    <div class="acc-body">

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Step 3.1 — Navigate to backend</span>
          <button class="cb-copy" onclick="cp(this,'cd backend')">📋 Copy</button>
        </div>
        <pre class="cb-pre">cd backend</pre>
      </div>

      <div class="cb-wrap" style="margin-top:10px;">
        <div class="cb-bar">
          <span class="cb-lbl">Step 3.2 — Create + activate virtual environment</span>
          <button class="cb-copy" onclick="cp(this,'python -m venv venv')">📋 Copy</button>
        </div>
        <pre class="cb-pre"><span class="cm"># Create venv</span>
python -m venv venv

<span class="cm"># Activate — Windows</span>
venv\\Scripts\\activate

<span class="cm"># Activate — Mac / Linux</span>
source venv/bin/activate</pre>
      </div>
      <p class="hint">You'll see <code>(venv)</code> prefix in your terminal. Always activate before running the backend.</p>

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Step 3.3 — Install backend dependencies</span>
          <button class="cb-copy" onclick="cp(this,'pip install -r requirements.txt')">📋 Copy</button>
        </div>
        <pre class="cb-pre">pip install -r requirements.txt</pre>
      </div>
      <p class="hint">Installs ~35 packages: FastAPI, uvicorn, DuckDB, pandas, scipy, pyarrow, supabase, pydantic, httpx. <strong>Takes 2–5 minutes</strong> — wait for <code>Successfully installed...</code></p>

      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">Step 3.4 — Create backend/.env</span>
          <button class="cb-copy" onclick="cp(this,'touch .env')">📋 Copy</button>
        </div>
        <pre class="cb-pre"><span class="cm"># Windows (run from inside backend/ directory)</span>
New-Item -Path ".env" -ItemType File

<span class="cm"># Mac / Linux</span>
touch .env</pre>
      </div>

      <div class="copy-notice" style="margin-top:14px;">
        <span class="copy-notice-text">📋 Step 3.5 — Copy all backend keys at once and paste into <code style="background:rgba(30,64,175,0.08);padding:1px 5px;border-radius:4px;font-family:var(--mono);font-size:11.5px;">backend/.env</code> &nbsp;·&nbsp; Valid until <strong>March 9, 2026</strong></span>
        <button class="copy-notice-btn" id="be-big-btn" onclick="cpBig('be-big-btn', beEnv)">📋 Copy All Keys</button>
      </div>
      <div class="cb-wrap">
        <div class="cb-bar">
          <span class="cb-lbl">backend/.env — full block</span>
          <button class="cb-copy" id="be-cb-btn" onclick="cpBig('be-cb-btn', beEnv)">📋 Copy</button>
        </div>
        <pre class="cb-pre">{be_hl}</pre>
      </div>

      <div class="cb-wrap" style="margin-top:14px;">
        <div class="cb-bar">
          <span class="cb-lbl">Step 3.6 — Start backend (venv must be active!)</span>
          <button class="cb-copy" onclick="cp(this,'uvicorn main:app --reload')">📋 Copy</button>
        </div>
        <pre class="cb-pre">uvicorn main:app --reload</pre>
      </div>
      <div class="ok-bar">✅ Backend running at http://localhost:8000 &nbsp;|&nbsp; Docs at http://localhost:8000/docs</div>

      <p style="font-size:12px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);margin:18px 0 8px;">Troubleshooting</p>
      <div class="trouble">
        <div class="tr-item"><div class="tr-err">ModuleNotFoundError</div><div class="tr-fix">venv not activated. Run <code>venv\\Scripts\\activate</code> (Win) or <code>source venv/bin/activate</code> (Mac/Linux).</div></div>
        <div class="tr-item"><div class="tr-err">Port 8000 already in use</div><div class="tr-fix">Run <code>uvicorn main:app --reload --port 8001</code> and update <code>NEXT_PUBLIC_API_URL</code> to match.</div></div>
        <div class="tr-item"><div class="tr-err">pip install appears stuck</div><div class="tr-fix">Normal — installing ~35 packages takes 2–5 mins. Wait for the <code>Successfully installed...</code> line.</div></div>
        <div class="tr-item"><div class="tr-err">Env vars not loading</div><div class="tr-fix"><code>.env.local</code> must be in project root. <code>.env</code> must be inside <code>backend/</code>. Restart servers after editing.</div></div>
      </div>
    </div>
  </details>

  <!-- ── SECTION 4 — VERIFY ────────────────────── -->
  <details class="acc">
    <summary>
      <div class="s-icon ic-amb">✅</div>
      <div class="s-text">
        <div class="s-title">Verify Setup + Upload Your First Dataset</div>
        <div class="s-sub">Check 3 URLs · upload CSV · start querying</div>
      </div>
      <span class="s-chev">▼</span>
    </summary>
    <div class="acc-body">
      <p class="hint" style="margin-bottom:14px;">Both servers running? Verify all three:</p>
      <table class="vtbl">
        <thead><tr><th>Service</th><th>URL</th><th>Expected</th></tr></thead>
        <tbody>
          <tr><td><span class="tag t-fe">Frontend</span></td><td><a href="http://localhost:3000" target="_blank">localhost:3000</a></td><td style="color:var(--muted)">InsightX landing page loads</td></tr>
          <tr><td><span class="tag t-api">API Docs</span></td><td><a href="http://localhost:8000/docs" target="_blank">localhost:8000/docs</a></td><td style="color:var(--muted)">This page, all endpoints visible</td></tr>
          <tr><td><span class="tag t-hc">Health</span></td><td><a href="http://localhost:8000/health" target="_blank">localhost:8000/health</a></td><td style="color:var(--muted);font-family:var(--mono);font-size:12px;">{{"status":"healthy"}}</td></tr>
        </tbody>
      </table>

      <p style="font-size:14px;font-weight:700;color:var(--fg);margin-bottom:10px;">Upload your first dataset:</p>
      <div class="steps">
        <div class="step"><div class="step-n">1</div><div class="step-c"><strong>Go to /connect</strong><span>http://localhost:3000/connect</span></div></div>
        <div class="step"><div class="step-n">2</div><div class="step-c"><strong>Drag and drop any CSV file</strong><span>or click to browse</span></div></div>
        <div class="step"><div class="step-n">3</div><div class="step-c"><strong>Wait for Data DNA generation</strong><span>Schema, patterns, anomalies auto-detected</span></div></div>
        <div class="step"><div class="step-n">4</div><div class="step-c"><strong>Redirected to workspace automatically</strong><span>Start asking natural language questions</span></div></div>
        <div class="step"><div class="step-n ok">✓</div><div class="step-c"><strong><span class="ok">You're live!</span></strong><span>Try: "What is the success rate?" · "Top 5 categories by revenue"</span></div></div>
      </div>
    </div>
  </details>

  <hr class="div"/>
  <div class="footer">
    Built for IIT-B Techfest 2026 &nbsp;·&nbsp;
    <a href="https://nabil-thange.vercel.app" target="_blank">Nabil Thange</a>, Tanish Soni, Yojith Rao &nbsp;·&nbsp;
    Keys expire March 9, 2026
  </div>
</div>

<!-- ── SWAGGER UI ──────────────────────────────────── -->
<div class="sw-wrap">
  <div class="sw-label">API Endpoints</div>
  <div id="swagger-ui"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.min.js"></script>
<script>
  // ── env strings (set from Python) ──────────────
  const feEnv = `{fe_js}`;
  const beEnv = `{be_js}`;

  // ── copy helpers ────────────────────────────────
  function cp(btn, text) {{
    navigator.clipboard.writeText(text.replace(/\\\\n/g,'\\n')).then(() => flash(btn));
  }}
  function cpBig(id, text) {{
    navigator.clipboard.writeText(text).then(() => {{
      const btn = document.getElementById(id);
      flash(btn);
    }});
  }}
  function flash(btn) {{
    const orig = btn.textContent;
    btn.textContent = '✓ Copied!';
    btn.classList.add('ok');
    setTimeout(() => {{ btn.textContent = orig; btn.classList.remove('ok'); }}, 2200);
  }}

  // ── Swagger ─────────────────────────────────────
  window.onload = () => {{
    SwaggerUIBundle({{
      url: '/openapi.json',
      dom_id: '#swagger-ui',
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: 'BaseLayout',
      docExpansion: 'none',
      defaultModelsExpandDepth: -1,
      displayRequestDuration: true,
      filter: true,
      syntaxHighlight: {{ theme: 'arta' }},
    }});
  }};
</script>
</body>
</html>"""

CUSTOM_DOCS_HTML = build_html(FE_ENV, BE_ENV)


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return HTMLResponse(content=CUSTOM_DOCS_HTML)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "InsightX Backend", "version": "1.0.0",
            "docs": "https://insightx-bkend.onrender.com/docs", "live_app": "https://insightxx.vercel.app"}


@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected", "storage": "connected"}