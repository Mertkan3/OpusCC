import streamlit as st
import anthropic
import json
import csv
import io
import re
from datetime import datetime

st.set_page_config(
    page_title="ClipMaster AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0a0f; }
[data-testid="stSidebar"] { background: #111118; border-right: 1px solid #222; }
.main .block-container { padding-top: 1.5rem; }
h1, h2, h3 { color: #fff !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #1a1a24 !important;
    border: 1px solid #333 !important;
    color: #fff !important;
    border-radius: 8px !important;
}
.stSlider [data-baseweb="slider"] { color: #a78bfa !important; }

.clip-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    position: relative;
}
.clip-card:hover { border-color: #7c3aed; transition: border-color 0.2s; }

.score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    margin-right: 6px;
}
.score-fire { background: #7c3aed22; color: #a78bfa; border: 1px solid #7c3aed; }
.score-tiktok { background: #ff004422; color: #ff6688; border: 1px solid #ff0044; }
.score-ig { background: #e1306c22; color: #ff6b9d; border: 1px solid #e1306c; }
.score-yt { background: #ff000022; color: #ff6666; border: 1px solid #ff0000; }

.platform-row {
    display: flex;
    gap: 8px;
    margin: 10px 0;
    flex-wrap: wrap;
}
.hashtag {
    background: #1e1b4b;
    color: #818cf8;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    border: 1px solid #3730a3;
}
.hook-box {
    background: #0f172a;
    border-left: 3px solid #7c3aed;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
    font-style: italic;
    color: #c4b5fd;
    font-size: 14px;
}
.ffmpeg-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: monospace;
    font-size: 12px;
    color: #79c0ff;
    word-break: break-all;
}
.timestamp-badge {
    background: #134e4a;
    color: #5eead4;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #0d9488;
}
.style-badge {
    background: #1e1b4b;
    color: #818cf8;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 12px;
}
.clip-title {
    font-size: 17px;
    font-weight: 700;
    color: #f1f5f9;
    margin: 8px 0 4px 0;
}
.clip-why {
    color: #94a3b8;
    font-size: 13px;
    margin: 6px 0;
    line-height: 1.5;
}
.broll-item {
    background: #1e293b;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    color: #7dd3fc;
    margin: 3px 2px;
    display: inline-block;
}
.header-hero {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.header-hero h1 {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #a78bfa, #ec4899, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.header-hero p {
    color: #64748b;
    font-size: 1rem;
    margin-top: 6px;
}
.stat-box {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 800; color: #a78bfa; }
.stat-label { color: #64748b; font-size: 12px; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ ClipMaster AI")
    st.markdown("<p style='color:#64748b;font-size:13px;'>Better than Opus Clips</p>", unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("🔑 Anthropic API Key", type="password", placeholder="sk-ant-...")
    if api_key:
        st.success("API Key gesetzt ✓")

    st.divider()
    st.markdown("**🎨 Creator Style**")
    creator_style = st.selectbox(
        "Style wählen",
        ["Kai Cenat (Hype + Funny)", "Adin Ross (Reactions + Drama)", "iShowSpeed (Rage + Energy)", "xQc (Fast + Commentary)", "Pokimane (Chill + Relatable)", "Custom / Eigener Style"],
        label_visibility="collapsed"
    )

    st.markdown("**📱 Ziel-Plattform**")
    platforms = st.multiselect(
        "Plattformen",
        ["TikTok", "Instagram Reels", "YouTube Shorts", "Twitter/X"],
        default=["TikTok", "Instagram Reels"],
        label_visibility="collapsed"
    )

    st.markdown("**🔥 Min. Virality Score**")
    min_virality = st.slider("", 0, 100, 65, label_visibility="collapsed")

    st.markdown("**✂️ Clip-Länge**")
    clip_length = st.select_slider(
        "",
        options=["15s", "30s", "45s", "60s", "90s", "Gemischt"],
        value="Gemischt",
        label_visibility="collapsed"
    )

    st.markdown("**📊 Anzahl Clips**")
    num_clips = st.slider("", 3, 15, 8, label_visibility="collapsed")

    st.divider()
    st.markdown("**⚙️ Erweitert**")
    include_broll = st.toggle("B-Roll Vorschläge", value=True)
    include_ffmpeg = st.toggle("FFmpeg Commands", value=True)
    include_captions = st.toggle("Caption-Vorschläge", value=True)
    auto_hashtags = st.toggle("Auto-Hashtags", value=True)

# ── MAIN HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-hero">
  <h1>⚡ ClipMaster AI</h1>
  <p>KI-gestütztes Clip-Curation · Besser als Opus Clips · Powered by Claude</p>
</div>
""", unsafe_allow_html=True)

# ── INPUT FORM ─────────────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📺 Stream-Info")
        stream_title = st.text_input("Stream-Titel", placeholder="z.B. 10-STUNDEN RANKED GRIND - RANKED TO DIAMOND")
        game_category = st.text_input("Spiel / Kategorie", placeholder="z.B. League of Legends, Just Chatting, Fortnite")
        stream_duration = st.text_input("Stream-Dauer", placeholder="z.B. 4:32:15")
        vod_url = st.text_input("VOD URL (optional)", placeholder="https://www.twitch.tv/videos/...")

    with col2:
        st.markdown("### ⭐ Besondere Momente")
        special_moments = st.text_area(
            "Timestamps & Momente",
            placeholder="00:12:34 - Epischer 1v5 Clutch\n00:45:00 - Stream sniped\n01:23:10 - Rage quit Moment\n02:15:00 - Subscriber Milestone\n...",
            height=140
        )
        chat_highlights = st.text_area(
            "Chat-Reaktionen / Highlights",
            placeholder="Was hat der Chat besonders gefeiert?\nWelche Clips waren im Chat viral?\nBesondere Subs/Giftsubs/Raids?",
            height=80
        )

    custom_instructions = st.text_area(
        "🎯 Zusätzliche Anweisungen (optional)",
        placeholder="z.B. Fokus auf Rage-Momente / Keine Spoiler / Nur Momente mit Facecam-Reaction...",
        height=60
    )

# ── ANALYZE BUTTON ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
with col_btn2:
    analyze_btn = st.button("⚡ CLIPS ANALYSIEREN", type="primary", use_container_width=True)

# ── ANALYSIS LOGIC ──────────────────────────────────────────────────────────────
def build_prompt(stream_title, game_category, stream_duration, special_moments,
                 chat_highlights, creator_style, platforms, clip_length, num_clips,
                 min_virality, include_broll, include_ffmpeg, include_captions,
                 auto_hashtags, custom_instructions):

    platform_str = ", ".join(platforms) if platforms else "TikTok, Instagram Reels"

    prompt = f"""Du bist ein Elite-Clip-Curator für Twitch-Streamer. Deine Aufgabe: Analysiere diesen Stream und finde die {num_clips} viralsten Clips, die besser performen als typische Opus-Clips-Auswahlen.

## STREAM-DATEN:
- **Titel:** {stream_title}
- **Spiel/Kategorie:** {game_category}
- **Dauer:** {stream_duration}
- **Creator Style:** {creator_style}
- **Zielplattformen:** {platform_str}
- **Clip-Länge:** {clip_length}

## BESONDERE MOMENTE:
{special_moments if special_moments else "Keine spezifischen Timestamps angegeben - analysiere den gesamten Stream"}

## CHAT-HIGHLIGHTS:
{chat_highlights if chat_highlights else "Keine Chat-Highlights angegeben"}

## ZUSÄTZLICHE ANWEISUNGEN:
{custom_instructions if custom_instructions else "Keine"}

## DEINE AUFGABE:
Erstelle eine detaillierte Clip-Liste im folgenden JSON-Format. Nur Clips mit Virality-Score >= {min_virality}.

Antworte NUR mit validem JSON, ohne Markdown-Backticks, ohne Erklärungen:

{{
  "clips": [
    {{
      "rank": 1,
      "title": "Kurzer, knalliger Clip-Titel (max 8 Wörter)",
      "timestamp_start": "HH:MM:SS",
      "timestamp_end": "HH:MM:SS",
      "duration_seconds": 45,
      "virality_score": 92,
      "tiktok_score": 95,
      "instagram_score": 88,
      "youtube_shorts_score": 85,
      "clip_type": "Rage Moment|Funny Reaction|Epic Play|Viewer Interaction|Emotional|Plot Twist|Skill Showcase",
      "hook": "Der erste Satz/Moment der den Viewer sofort fesselt",
      "why_viral": "Konkrete Begründung warum dieser Clip viral geht (2-3 Sätze)",
      "emotional_trigger": "Lachen|Schock|Spannung|Fremdscham|Hype|Mitgefühl|Rage|Cringe",
      "best_platform": "TikTok|Instagram|YouTube Shorts",
      "caption_suggestion": "Fertige Caption für Social Media inkl. Call-to-Action",
      "hashtags": ["#gaming", "#twitch", "#viral", "#fyp", "#streamer"],
      "broll_suggestions": ["Zoom auf Gesicht bei Reaction", "Chat-Overlay einblenden", "Slow-Motion bei Epic Moment"],
      "ffmpeg_command": "ffmpeg -i input.mp4 -ss HH:MM:SS -to HH:MM:SS -c copy output_clip1.mp4",
      "thumbnail_idea": "Beschreibung des perfekten Thumbnails",
      "edit_tips": "Konkrete Schnitt-Tipps für diesen Clip",
      "trending_sounds": "Welcher Trend-Sound würde passen",
      "predicted_views": "10k-50k"
    }}
  ],
  "session_summary": {{
    "best_overall_clip": 1,
    "total_viral_moments": {num_clips},
    "recommended_posting_order": [1, 3, 2],
    "content_strategy": "Kurze Empfehlung zur Posting-Strategie",
    "stream_highlights": "Was war das absolute Highlight dieses Streams?"
  }}
}}

WICHTIG:
- Sei spezifisch und kreativ mit Titeln und Hooks
- Berücksichtige den {creator_style} Style
- Priorisiere emotionale Momente über technische Gameplay-Clips
- TikTok-Hooks müssen in den ersten 2 Sekunden greifen
- Timestamps müssen realistisch zur Stream-Dauer {stream_duration} passen
{"- Füge kreative B-Roll Vorschläge hinzu" if include_broll else ""}
{"- Füge präzise FFmpeg-Befehle hinzu" if include_ffmpeg else ""}
{"- Erstelle catchy Captions" if include_captions else ""}
{"- 5 relevante Hashtags pro Clip" if auto_hashtags else ""}
"""
    return prompt


def parse_clips(raw_text):
    clean = raw_text.strip()
    clean = re.sub(r'^```json\s*', '', clean)
    clean = re.sub(r'^```\s*', '', clean)
    clean = re.sub(r'\s*```$', '', clean)
    return json.loads(clean)


def render_clip_card(clip, idx, include_broll, include_ffmpeg, include_captions, auto_hashtags):
    score = clip.get("virality_score", 0)
    score_color = "#22c55e" if score >= 85 else "#f59e0b" if score >= 70 else "#ef4444"

    tiktok_s = clip.get("tiktok_score", "—")
    ig_s = clip.get("instagram_score", "—")
    yt_s = clip.get("youtube_shorts_score", "—")

    hashtags_html = ""
    if auto_hashtags:
        tags = clip.get("hashtags", [])
        hashtags_html = "".join(f'<span class="hashtag">{t}</span>' for t in tags[:6])

    broll_html = ""
    if include_broll:
        brolls = clip.get("broll_suggestions", [])
        broll_html = "".join(f'<span class="broll-item">🎬 {b}</span>' for b in brolls)

    ffmpeg_html = ""
    if include_ffmpeg and clip.get("ffmpeg_command"):
        ffmpeg_html = f'<div class="ffmpeg-box">💻 {clip["ffmpeg_command"]}</div>'

    caption_html = ""
    if include_captions and clip.get("caption_suggestion"):
        caption_html = f"""
        <div style="background:#0f1729;border:1px solid #1e3a5f;border-radius:8px;padding:10px 14px;margin:8px 0;font-size:13px;color:#93c5fd;">
            📝 <strong style="color:#60a5fa;">Caption:</strong> {clip["caption_suggestion"]}
        </div>"""

    st.markdown(f"""
    <div class="clip-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
            <div>
                <span class="timestamp-badge">#{clip.get('rank','?')} · {clip.get('timestamp_start','?')} → {clip.get('timestamp_end','?')}</span>
                <span class="style-badge" style="margin-left:6px;">{clip.get('clip_type','?')}</span>
                <p class="clip-title">{clip.get('title','Untitled')}</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2rem;font-weight:900;color:{score_color};line-height:1;">{score}</div>
                <div style="font-size:10px;color:#64748b;">VIRALITY</div>
            </div>
        </div>

        <div class="platform-row">
            <span class="score-badge score-tiktok">TikTok {tiktok_s}</span>
            <span class="score-badge score-ig">Instagram {ig_s}</span>
            <span class="score-badge score-yt">YT Shorts {yt_s}</span>
            <span class="score-badge score-fire">⚡ {clip.get('emotional_trigger','?')}</span>
            <span class="score-badge" style="background:#14532d22;color:#86efac;border:1px solid #14532d;">📈 {clip.get('predicted_views','?')}</span>
        </div>

        <div class="hook-box">🪝 Hook: "{clip.get('hook','')}"</div>

        <p class="clip-why">🎯 {clip.get('why_viral','')}</p>

        <div style="background:#0f172a;border-radius:8px;padding:10px 14px;margin:8px 0;font-size:13px;color:#fbbf24;">
            🖼️ <strong>Thumbnail:</strong> {clip.get('thumbnail_idea','')}
        </div>

        {caption_html}

        <div style="margin:6px 0;">{hashtags_html}</div>

        {broll_html and f'<div style="margin:8px 0;">{broll_html}</div>' or ""}

        {ffmpeg_html}

        <div style="display:flex;gap:16px;margin-top:10px;font-size:12px;color:#475569;">
            <span>✂️ {clip.get('edit_tips','')}</span>
        </div>
        <div style="font-size:12px;color:#475569;margin-top:4px;">
            🎵 Trend-Sound: {clip.get('trending_sounds','')}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── RUN ANALYSIS ────────────────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("❌ Bitte gib deinen Anthropic API Key in der Sidebar ein!")
        st.stop()
    if not stream_title:
        st.error("❌ Bitte gib mindestens den Stream-Titel ein!")
        st.stop()

    prompt = build_prompt(
        stream_title, game_category, stream_duration, special_moments,
        chat_highlights, creator_style, platforms, clip_length, num_clips,
        min_virality, include_broll, include_ffmpeg, include_captions,
        auto_hashtags, custom_instructions
    )

    with st.spinner("⚡ Claude analysiert deinen Stream..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text
            data = parse_clips(raw)
            clips = data.get("clips", [])
            summary = data.get("session_summary", {})

            st.session_state["clips"] = clips
            st.session_state["summary"] = summary
            st.session_state["stream_title"] = stream_title
            st.session_state["raw_json"] = raw

        except json.JSONDecodeError:
            st.error("Fehler beim Parsen der KI-Antwort. Versuche es erneut.")
            with st.expander("Raw Response"):
                st.code(raw)
            st.stop()
        except Exception as e:
            st.error(f"API Fehler: {e}")
            st.stop()

# ── DISPLAY RESULTS ─────────────────────────────────────────────────────────────
if "clips" in st.session_state:
    clips = st.session_state["clips"]
    summary = st.session_state["summary"]

    st.markdown("---")
    st.markdown(f"## ✅ {len(clips)} Clips gefunden für: *{st.session_state['stream_title']}*")

    # Stats row
    if clips:
        avg_virality = sum(c.get("virality_score", 0) for c in clips) / len(clips)
        top_score = max(c.get("virality_score", 0) for c in clips)
        total_dur = sum(c.get("duration_seconds", 0) for c in clips)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(clips)}</div><div class="stat-label">Clips total</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{avg_virality:.0f}</div><div class="stat-label">Ø Virality Score</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{top_score}</div><div class="stat-label">Top Score</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{total_dur//60}m</div><div class="stat-label">Content gesamt</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strategy box
    if summary.get("content_strategy"):
        st.markdown(f"""
        <div style="background:#1e1b4b;border:1px solid #3730a3;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
            <strong style="color:#a78bfa;">📋 Strategie-Empfehlung:</strong>
            <p style="color:#c4b5fd;margin:6px 0 0 0;font-size:14px;">{summary['content_strategy']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Filter & Sort
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sort_by = st.selectbox("Sortieren nach", ["Virality Score", "TikTok Score", "Instagram Score", "YouTube Score", "Reihenfolge"])
    with col_f2:
        filter_type = st.selectbox("Clip-Typ Filter", ["Alle"] + list(set(c.get("clip_type", "") for c in clips)))
    with col_f3:
        filter_platform = st.selectbox("Beste Plattform", ["Alle"] + list(set(c.get("best_platform", "") for c in clips if c.get("best_platform"))))

    # Apply filters
    filtered = clips[:]
    if filter_type != "Alle":
        filtered = [c for c in filtered if c.get("clip_type") == filter_type]
    if filter_platform != "Alle":
        filtered = [c for c in filtered if c.get("best_platform") == filter_platform]

    if sort_by == "Virality Score":
        filtered.sort(key=lambda x: x.get("virality_score", 0), reverse=True)
    elif sort_by == "TikTok Score":
        filtered.sort(key=lambda x: x.get("tiktok_score", 0), reverse=True)
    elif sort_by == "Instagram Score":
        filtered.sort(key=lambda x: x.get("instagram_score", 0), reverse=True)
    elif sort_by == "YouTube Score":
        filtered.sort(key=lambda x: x.get("youtube_shorts_score", 0), reverse=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for i, clip in enumerate(filtered):
        render_clip_card(clip, i, include_broll, include_ffmpeg, include_captions, auto_hashtags)

    # ── EXPORT ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📦 Export")

    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        json_str = json.dumps({"clips": clips, "summary": summary}, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ JSON exportieren",
            data=json_str,
            file_name=f"clipmaster_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

    with ec2:
        csv_buffer = io.StringIO()
        if clips:
            fieldnames = ["rank", "title", "timestamp_start", "timestamp_end", "duration_seconds",
                          "virality_score", "tiktok_score", "instagram_score", "youtube_shorts_score",
                          "clip_type", "hook", "why_viral", "best_platform", "predicted_views"]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(clips)
        st.download_button(
            "⬇️ CSV exportieren",
            data=csv_buffer.getvalue(),
            file_name=f"clipmaster_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ec3:
        social_lines = []
        for clip in clips:
            social_lines.append(f"{'='*50}")
            social_lines.append(f"#{clip.get('rank')} | {clip.get('title')}")
            social_lines.append(f"⏱️ {clip.get('timestamp_start')} → {clip.get('timestamp_end')}")
            social_lines.append(f"🔥 Virality: {clip.get('virality_score')}/100")
            social_lines.append(f"📝 Caption: {clip.get('caption_suggestion','')}")
            tags = " ".join(clip.get("hashtags", []))
            social_lines.append(f"🏷️ {tags}")
            if include_ffmpeg:
                social_lines.append(f"💻 {clip.get('ffmpeg_command','')}")
            social_lines.append("")
        social_text = "\n".join(social_lines)
        st.download_button(
            "⬇️ Social Posts exportieren",
            data=social_text,
            file_name=f"social_posts_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Raw JSON
    with st.expander("🔍 Raw JSON anzeigen"):
        st.code(st.session_state.get("raw_json", ""), language="json")

# ── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#334155;font-size:12px;">
    ⚡ ClipMaster AI · Powered by Claude · Made for Twitch Streamers
</div>
""", unsafe_allow_html=True)
