import streamlit as st
import anthropic
import json

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Roleplay Scenario Generator",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 800px; }
    h1 { font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }
    .subhead { font-size: 15px; color: #6b7280; margin-top: -0.5rem; margin-bottom: 1.5rem; }
    .scenario-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .scenario-title {
        font-size: 16px;
        font-weight: 700;
        color: #111;
        margin-bottom: 5px;
    }
    .scenario-setting {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 12px;
        font-style: italic;
    }
    .tag-pill {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 10px;
        margin-right: 4px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .opening-label {
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 12px;
        margin-bottom: 5px;
    }
    .opening-msg {
        background: #f9fafb;
        border-left: 3px solid #6366f1;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 14px;
        color: #1f2937;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .response-label {
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .response-option {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #1e40af;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    .platform-note {
        border-radius: 8px;
        padding: 9px 13px;
        font-size: 12px;
        margin-bottom: 14px;
    }
    .note-filtered  { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .note-semi      { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
    .note-unfiltered{ background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    .stButton > button {
        background: #111 !important;
        color: white !important;
        border: none !important;
        padding: 0.65rem 2rem !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100%;
    }
    .stButton > button:hover { background: #374151 !important; }
    .affiliate-strip {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 0.5rem;
        font-size: 13px;
        color: #4b5563;
    }
    .group-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 2px 8px;
        border-radius: 4px;
        margin-left: 8px;
    }
    .gl-filtered   { background: #dcfce7; color: #166534; }
    .gl-semi       { background: #fef9c3; color: #854d0e; }
    .gl-unfiltered { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Platform data
# ---------------------------------------------------------------------------

# Groups: filtered | semi-open | unfiltered
# Determines how Claude writes the opening message

PLATFORMS = {
    # --- Filtered ---
    "Character.AI": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Strong content moderation. Openings must stay within PG-13. Emotional depth, tension, and romantic suggestion work well — avoid anything explicit.",
        "aff_label": None, "aff_url": None,
    },
    "Replika": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Emotional companion focused on warmth and connection. Slow-burn, vulnerable openings outperform dramatic ones. Explicit content is blocked.",
        "aff_label": None, "aff_url": None,
    },
    "Chai AI": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Moderate filters. Short, punchy character voices perform best. Strong personality establishment in the opening lands well here.",
        "aff_label": None, "aff_url": None,
    },
    "Talkie AI": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Leans family-friendly. Story-driven openings that emphasize mystery and connection work best. Keep content clean.",
        "aff_label": None, "aff_url": None,
    },
    "Anima AI": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Friendship and romance focus. Warm, sincere openings beat dramatic ones. Build emotional connection from the first message.",
        "aff_label": None, "aff_url": None,
    },
    "Poe": {
        "group": "filtered",
        "label": "Filtered",
        "note": "Uses underlying models (Claude, GPT-4). Quality of system prompt matters most. Scenario-focused openings with clear character voice work well.",
        "aff_label": None, "aff_url": None,
    },
    # --- Semi-open ---
    "Candy AI": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Supports mature and romantic themes. Opening messages can be suggestive and forward. Avoid graphic content but full relationship dynamic is fair game.",
        "aff_label": "Try Candy AI", "aff_url": "https://crownmediacreative.com/CandyAI-Chatbot",
    },
    "Kindroid": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Deep backstory customization. Openings that reference the character's established history feel native to this platform.",
        "aff_label": None, "aff_url": None,
    },
    "Nomi AI": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Long-term memory companion. Openings that build emotional context and reference shared history land especially well.",
        "aff_label": "Try Nomi AI", "aff_url": "https://crownmediacreative.com/NomiAI",
    },
    "EVA AI": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Relationship simulator. Direct emotional openings with clear character intent and romantic tension perform well.",
        "aff_label": None, "aff_url": None,
    },
    "DreamGF": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Intimacy-focused platform. Openings that establish closeness and personality from the start fit the platform's design.",
        "aff_label": "Try DreamGF", "aff_url": "https://www.roborhythms.com/DreamGf",
    },
    "Botify AI": {
        "group": "semi-open",
        "label": "Semi-open",
        "note": "Celebrity and character bots. Match the established character voice in the opening — consistency with the persona is key.",
        "aff_label": None, "aff_url": None,
    },
    # --- Unfiltered ---
    "Crushon.AI": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "No content restrictions. Full creative freedom — write as bold, vivid, or intense as the scenario demands.",
        "aff_label": "Try Crushon.AI", "aff_url": "https://crownmediacreative.com/NewCrushOnAI",
    },
    "SpicyChat": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "Adult-oriented platform. Full content freedom. Vivid, immersive openings that establish the scenario immediately work best.",
        "aff_label": "Try SpicyChat", "aff_url": "https://www.roborhythms.com/SpicyChatAI",
    },
    "Janitor AI": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "User-provided API keys mean no platform filtering. Direct, detailed openings that clearly establish the scenario context perform well.",
        "aff_label": None, "aff_url": None,
    },
    "Muah AI": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "Multimodal companion (voice + chat). Openings that feel natural spoken aloud work best — avoid overly complex sentence structures.",
        "aff_label": None, "aff_url": None,
    },
    "AI Dungeon": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "Story-driven adventure platform. Longer, descriptive openings with rich world-building work well — this platform rewards narrative depth.",
        "aff_label": None, "aff_url": None,
    },
    "Novel AI": {
        "group": "unfiltered",
        "label": "Unfiltered",
        "note": "Literary AI writing tool. Prose-forward openings with strong atmosphere and voice shine here more than in any other platform.",
        "aff_label": None, "aff_url": None,
    },
}

GROUP_INSTRUCTION = {
    "filtered": "The platform has content moderation. Keep the opening message within PG-13 limits. Romantic tension, emotional depth, and suggestive subtext are fine — avoid any explicit content or graphic descriptions.",
    "semi-open": "The platform supports mature themes and romantic content. The opening can be suggestive, intimate, and forward without being graphic. Don't hold back on tension or implied desire, but stop short of explicit description.",
    "unfiltered": "The platform has no content restrictions. Write with complete creative freedom. Be as vivid, bold, and immersive as the genre and tone call for. If the tone is dark, go dark. If it's intense, go intense.",
}

NOTE_CLASS = {"filtered": "note-filtered", "semi-open": "note-semi", "unfiltered": "note-unfiltered"}
NOTE_ICON  = {"filtered": "🟢", "semi-open": "🟡", "unfiltered": "🔴"}

GENRES = [
    "Romance", "Dark Romance", "Fantasy", "Dark Fantasy", "Sci-Fi",
    "Thriller / Mystery", "Slice of Life", "Historical", "Supernatural / Horror",
    "Post-Apocalyptic", "Enemies to Lovers", "Found Family", "Psychological",
]
TONES = [
    "Sweet & cozy", "Dark & intense", "Playful & flirty", "Emotionally deep",
    "Slow burn tension", "Fast & action-packed", "Mysterious & unsettling",
]
DYNAMICS = [
    "Strangers meeting for the first time",
    "Childhood friends reunited",
    "Rivals forced to work together",
    "Forbidden attraction",
    "Protector and someone in danger",
    "Mentor and student",
    "Royalty and commoner",
    "Two survivors in a dangerous world",
    "Forced proximity / arranged situation",
    "Second chance after a painful past",
    "Captor and captive",
    "Immortal and mortal",
    "Enemies who discover a shared secret",
    "Bodyguard and the person they protect",
]

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        import os, json as _json
        try:
            creds = _json.load(open("C:/Users/NOAH/.claude/.credentials.json", encoding="utf-8"))
            api_key = creds["anthropic"]["api_key"]
        except Exception:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    return anthropic.Anthropic(api_key=api_key)


def generate_scenarios(platform, genre, tone, dynamic, character_hint):
    p = PLATFORMS[platform]
    client = get_client()

    char_context = f"\nUser's character hint: {character_hint.strip()}" if character_hint.strip() else ""
    content_rule = GROUP_INSTRUCTION[p.get("group") or "filtered"]

    prompt = f"""You are a creative writing assistant specialising in AI companion app roleplay.

Generate exactly 3 distinct roleplay scenarios for:
- Platform: {platform}
- Genre: {genre}
- Tone: {tone}
- Dynamic: {dynamic}{char_context}

Content rule for {platform}: {content_rule}

For each scenario output a JSON object with these exact keys:
- "title": short evocative title, 5-8 words
- "setting": one vivid sentence describing the world and location, max 30 words
- "opening": the AI character's first message to the user, ready to paste directly into {platform}. Write in first person as the character. 3-5 sentences. Match the tone exactly. Do NOT use asterisks for actions — write natural dialogue and inner framing only.
- "responses": array of exactly 3 short user reply options (1-2 sentences each) that naturally continue the opening. These help the user start without staring at a blank input.

Output ONLY a valid JSON array of 3 objects. No markdown, no preamble, no explanation."""

    message = get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown("# 🎭 AI Roleplay Scenario Generator")
st.markdown('<p class="subhead">Pick your platform, genre, and vibe — get 3 complete scenarios with opening messages and reply options ready to paste.</p>', unsafe_allow_html=True)

# Platform ordered display: filtered → semi-open → unfiltered
platform_order = [
    # filtered
    "Character.AI", "Replika", "Chai AI", "Talkie AI", "Anima AI", "Poe",
    # semi-open
    "Candy AI", "Kindroid", "Nomi AI", "EVA AI", "DreamGF", "Botify AI",
    # unfiltered
    "Crushon.AI", "SpicyChat", "Janitor AI", "Muah AI", "AI Dungeon", "Novel AI",
]

col1, col2 = st.columns(2)

with col1:
    platform = st.selectbox(
        "Platform",
        platform_order,
        format_func=lambda p: f"{NOTE_ICON[PLATFORMS[p].get('group') or 'filtered']}  {p}  [{PLATFORMS[p].get('label') or ''}]",
    )
    genre = st.selectbox("Genre", GENRES)
    tone  = st.selectbox("Tone",  TONES)

with col2:
    dynamic = st.selectbox("Dynamic", DYNAMICS)
    character_hint = st.text_input(
        "Character name or type (optional)",
        placeholder="e.g. brooding vampire lord, cheerful rival barista...",
    )
    st.markdown("&nbsp;", unsafe_allow_html=True)
    generate_btn = st.button("Generate Scenarios", use_container_width=True)

st.markdown("---")

if generate_btn:
    with st.spinner("Writing your scenarios..."):
        try:
            scenarios = generate_scenarios(platform, genre, tone, dynamic, character_hint)
        except json.JSONDecodeError:
            st.error("Generation returned an unexpected format. Hit Generate again.")
            st.stop()
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

    p_data = PLATFORMS[platform]
    p_group = p_data.get("group") or "filtered"
    note_class = NOTE_CLASS[p_group]

    st.markdown(f"### 3 scenarios for {platform}")
    st.caption(f"{genre} · {tone} · {dynamic}")

    # Platform tip
    st.markdown(
        f'<div class="platform-note {note_class}">'
        f'{NOTE_ICON[p_group]} <strong>{platform} ({p_data.get("label") or ""}):</strong> {p_data.get("note") or ""}'
        f'</div>',
        unsafe_allow_html=True,
    )

    for i, s in enumerate(scenarios, 1):
        responses_html = "".join(
            f'<div class="response-option">"{r}"</div>'
            for r in s.get("responses", [])
        )
        st.markdown(f"""
        <div class="scenario-card">
            <div class="scenario-title">#{i} — {s['title']}</div>
            <div class="scenario-setting">{s['setting']}</div>
            <span class="tag-pill">{genre}</span><span class="tag-pill">{tone}</span>
            <div class="opening-label">Opening message — paste into {platform}</div>
            <div class="opening-msg">{s['opening']}</div>
            <div class="response-label">Your reply options</div>
            {responses_html}
        </div>
        """, unsafe_allow_html=True)

    # Affiliate strip
    if p_data["aff_label"]:
        st.markdown(
            f'<div class="affiliate-strip">Ready to try it? '
            f'<a href="{p_data["aff_url"]}" target="_blank" style="color:#111;font-weight:700;">{p_data["aff_label"]} →</a>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # fallback: link to RR best companions article
        st.markdown(
            '<div class="affiliate-strip">Not sure which platform fits you? '
            '<a href="https://www.roborhythms.com/best-ai-companion-apps/" target="_blank" style="color:#111;font-weight:700;">'
            'Compare all AI companion apps →</a></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("Tip: same genre + different dynamic = completely different feel. Experiment with Slow burn vs Dark & intense for the same scenario setup.")

else:
    st.markdown("""
    <div style="background:#f9fafb;border-radius:12px;padding:2.5rem;text-align:center;color:#6b7280;">
        <div style="font-size:2.5rem;margin-bottom:0.5rem;">🎭</div>
        <div style="font-size:16px;font-weight:600;color:#374151;margin-bottom:0.5rem;">Ready to generate</div>
        <div style="font-size:14px;">Choose your platform, genre, tone, and dynamic above.<br>
        Each run gives 3 complete scenarios with opening messages and reply options ready to paste.</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<p style="font-size:12px;color:#d1d5db;text-align:center;">'
    'AI Roleplay Scenario Generator by <a href="https://www.roborhythms.com" style="color:#d1d5db;">RoboRhythms</a> '
    '· Scenarios generated with Claude · Not affiliated with any AI companion platform listed.</p>',
    unsafe_allow_html=True,
)
