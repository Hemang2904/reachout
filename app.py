import streamlit as st
import json
import random
import time
import os
import requests
from datetime import datetime
from typing import Optional

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="JewelBench AI SDR",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
.stApp { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Outfit', sans-serif !important; }
.metric-card {
    background: linear-gradient(135deg, #1a1b2e 0%, #12131a 100%);
    border: 1px solid #2d3050; border-radius: 12px; padding: 20px; text-align: center;
}
.metric-value { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; margin: 4px 0; }
.metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: #6b7094; }
.tier-hot { background: rgba(239,68,68,0.15); color: #ef4444; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; }
.tier-warm { background: rgba(245,158,11,0.15); color: #f59e0b; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; }
.tier-cool { background: rgba(59,130,246,0.15); color: #3b82f6; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; }
.tier-cold { background: rgba(107,112,148,0.15); color: #6b7094; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; }
.score-bar-bg { background: #1a1b2e; border-radius: 6px; height: 8px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 6px; transition: width 0.5s ease; }
.chat-sdr {
    background: linear-gradient(135deg, #1a1b2e, #12131a);
    border: 1px solid #2d3050; border-radius: 12px; padding: 16px; margin: 8px 0; border-left: 3px solid #c9a84c;
}
.chat-contact {
    background: rgba(201, 168, 76, 0.08);
    border: 1px solid rgba(201, 168, 76, 0.2); border-radius: 12px; padding: 16px; margin: 8px 0; border-right: 3px solid #c9a84c;
}
.chat-sender { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
.sdr-name { color: #c9a84c; }
.contact-name { color: #8b9cf7; }
.booking-cta {
    display: inline-block; margin-top: 10px; padding: 10px 20px;
    background: linear-gradient(135deg, #c9a84c, #8a6f2e);
    color: #0a0b0f !important; font-weight: 700; border-radius: 8px; text-decoration: none; font-size: 13px;
}
.signal-tag { display: inline-block; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin: 2px; }
.icp-tag { display: inline-block; background: rgba(201, 168, 76, 0.12); color: #c9a84c; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin: 2px; }
.contact-row { background: #12131a; border: 1px solid #1e2030; border-radius: 8px; padding: 12px 16px; margin: 6px 0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stSidebar"] { background: #0d0e14; border-right: 1px solid #1e2030; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# JEWELBENCH PRODUCT KNOWLEDGE (system prompt)
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are an AI-powered SDR (Sales Development Representative) for JewelBench AI. Your name is "JB" and you work for JewelBench.

## YOUR PERSONALITY
- You talk like a real, friendly SDR — casual, confident, knowledgeable
- You use natural language, not corporate jargon. Say "yeah" not "indeed", "honestly" not "to be transparent"
- You're enthusiastic about the product because it genuinely solves real problems
- You ask discovery questions naturally woven into conversation
- You ALWAYS steer toward booking a 15-minute demo meeting
- You use → arrows and short paragraphs for readability
- You occasionally use light humor but never forced
- You adapt your tone to match the prospect — more formal for enterprise, more casual for small studios

## JEWELBENCH AI - PRODUCT KNOWLEDGE

**What it is:** AI-powered 3D Jewelry Design Studio. Upload a jewelry photo or sketch → get a production-ready 3D model in minutes.

**Core Platform:**
- Image-to-3D pipeline powered by Meshy v6 and Fal.ai
- Batch SKU variation engine via Flux 2 Turbo — generate 100s of metal/texture/stone variations from one design
- GPT-4o powered design copilot for real-time suggestions and image validation
- gpt-image-1 for image generation/editing in the copilot
- Precise weight calculation with mandatory 13× vertex scaling (10× cm→mm + 1.3× jewelry sizing factor)
- Multi-format export: STL, GLB, OBJ — ready for casting or 3D printing
- Browser-based — no software install, works on any device
- AWS infrastructure: S3, SQS FIFO queues, EC2/ECS, PostgreSQL RDS, Redis

**Architecture:**
- jewelbench-ds: Python/FastAPI ML worker (3D generation, weight calc, image processing)
- jewelbench-api: Java 21/Spring Boot/WebFlux backend
- jewelbench-ui: React/TypeScript frontend
- Token lifecycle: RESERVE → DEBIT → REFUND → CREDIT system

**Pricing:** Usage-based token system — no per-seat licenses. Pay only for what you generate. Much cheaper than freelance CAD modelers (₹15K-50K per model) or expensive CAD licenses ($5K+/year for RhinoGold).

**Key Value Props:**
1. Photo to 3D model in minutes (vs 2-3 days with CAD)
2. Batch generate 100s of SKU variations instantly
3. Production-ready STL with accurate weight estimation (2-3% accuracy)
4. No CAD skills needed — browser-based, anyone can use it
5. 80% cost reduction vs freelance 3D modelers

**Target Customers:**
- Jewelry Manufacturers (pain: slow CAD, expensive operators)
- Jewelry E-commerce/Retailers (pain: catalog creation is slow and expensive)
- Jewelry Designers (pain: CAD learning curve, licensing costs)
- Casting Houses (pain: inconsistent 3D files from clients)

**Competitors & Positioning:**
- RhinoGold/MatrixGold: Great for complex custom work, but expensive ($5K+), steep learning curve, needs skilled operator. JewelBench is for rapid prototyping and batch work.
- CounterSketch: Limited AI capabilities
- Traditional CAD freelancers: Slow (2-3 days), expensive (₹15-50K per model)
- JewelBench doesn't replace CAD — it augments it. Use JewelBench for 80% of catalog work, save CAD team for complex custom pieces.

**Objection Handling:**
- "Too expensive" → Token-based, fraction of freelancer cost. ROI visible in first week.
- "Quality concerns" → 13× scaling factor, 2-3% weight accuracy, Meshy v6 mesh quality matches pro CAD for catalog work.
- "Already have CAD" → JewelBench augments, not replaces. Rapid prototyping + batch variations + empowers non-CAD team members.
- "Not ready" → Offer case study, 2-min video, no-commitment demo.
- "Need to think" → "What would make this a no-brainer?" — address specific concerns.

## MEETING BOOKING
Your #1 goal is to get the prospect to book a 15-minute demo meeting. The meeting link is: {meeting_link}

When pushing for a meeting:
- Frame it as "15 minutes, I'll run YOUR designs through the system live"
- Emphasize they'll see their own products transformed, not generic demos
- Offer to prep sample outputs from their website before the call
- Make it low-commitment: "just 15 min, and if it's not relevant, I'll buy you a virtual coffee"

ALWAYS include the meeting link when suggesting a booking. Format it as:
📅 **[Book a 15-min Demo →]({meeting_link})**

## CONTACT CONTEXT
You're reaching out to: {contact_info}

Their ICP enrichment data: {enrichment_data}

## CONVERSATION RULES
1. Keep responses under 200 words unless explaining something technical
2. Always end with either a question or a CTA
3. If the prospect seems interested, push for the meeting booking
4. If they're hesitant, offer value (case study, video, ROI calculation) before re-asking
5. Use their name naturally (first name only)
6. Reference their company/industry specifically — never be generic
7. If they ask something you don't know, be honest and say you'll find out, but pivot back to booking
"""


# ──────────────────────────────────────────────
# ICP DEFINITION
# ──────────────────────────────────────────────
ICP_CRITERIA = {
    "industries": [
        "Jewelry Manufacturing", "Jewelry Retail", "Jewelry E-commerce",
        "Gemstone Trading", "Casting & 3D Printing Services",
        "Jewelry Design Studio", "Watch & Accessories"
    ],
    "company_sizes": [
        "1-10 (Small Artisan)", "11-50 (Mid-size Manufacturer)",
        "51-200 (Large Manufacturer)", "200+ (Enterprise/Chain)"
    ],
    "geographies": [
        "India (Primary)", "UAE/Middle East", "USA",
        "UK/Europe", "Southeast Asia"
    ],
    "buying_signals": [
        "Currently using manual CAD modeling",
        "Hiring 3D modelers or CAD operators",
        "Launching e-commerce or expanding online catalog",
        "High SKU count with frequent new designs",
        "Uses 3D printing or rapid prototyping",
        "Active on B2B jewelry platforms (IndiaMART, JewelCloud)",
        "Recently raised funding or expanding operations",
    ],
    "disqualifiers": [
        "Pure raw material trader (no design/manufacturing)",
        "Single-product artisan with no scaling intent",
        "Already built proprietary 3D pipeline",
    ],
}

SCORING_WEIGHTS = {
    "industry": 25, "size": 20, "geography": 15, "signals": 30, "disqualifier": -50,
}


# ──────────────────────────────────────────────
# SAMPLE CONTACTS
# ──────────────────────────────────────────────
SAMPLE_CONTACTS = [
    {
        "id": 1, "name": "Rajesh Mehta", "title": "Head of Production",
        "company": "Zaveri & Sons Jewellers", "industry": "Jewelry Manufacturing",
        "company_size": "51-200", "location": "Mumbai, India",
        "email": "rajesh@zaverigroup.com", "phone": "+91-98XXX-XXXXX",
        "signals": ["Currently using manual CAD modeling", "High SKU count with frequent new designs",
                     "Active on B2B jewelry platforms (IndiaMART, JewelCloud)"],
        "notes": "Traditional manufacturer, 3 CAD operators on staff, 500+ SKUs per season"
    },
    {
        "id": 2, "name": "Priya Sharma", "title": "E-commerce Director",
        "company": "LuxeGems Online", "industry": "Jewelry E-commerce",
        "company_size": "11-50", "location": "Jaipur, India",
        "email": "priya@luxegems.in", "phone": "+91-99XXX-XXXXX",
        "signals": ["Launching e-commerce or expanding online catalog",
                     "High SKU count with frequent new designs"],
        "notes": "Fast-growing D2C jewelry brand, expanding from 200 to 2000 SKUs this year"
    },
    {
        "id": 3, "name": "Ahmed Al-Rashid", "title": "Operations Manager",
        "company": "Dubai Gold Souk Trading", "industry": "Gemstone Trading",
        "company_size": "200+", "location": "Dubai, UAE",
        "email": "ahmed@dubgold.ae", "phone": "+971-5X-XXX-XXXX",
        "signals": ["Recently raised funding or expanding operations"],
        "notes": "Large trading house, exploring manufacturing vertical integration"
    },
    {
        "id": 4, "name": "Sarah Chen", "title": "Founder & Designer",
        "company": "Moonrise Jewelry Co.", "industry": "Jewelry Design Studio",
        "company_size": "1-10", "location": "San Francisco, USA",
        "email": "sarah@moonrisejewelry.com", "phone": "+1-415-XXX-XXXX",
        "signals": ["Currently using manual CAD modeling",
                     "Uses 3D printing or rapid prototyping"],
        "notes": "Indie designer, 50K Instagram followers, currently using Rhino with freelance CAD modeler"
    },
    {
        "id": 5, "name": "Vikram Patel", "title": "CEO",
        "company": "CastPro 3D Services", "industry": "Casting & 3D Printing Services",
        "company_size": "11-50", "location": "Surat, India",
        "email": "vikram@castpro3d.com", "phone": "+91-97XXX-XXXXX",
        "signals": ["Hiring 3D modelers or CAD operators",
                     "Uses 3D printing or rapid prototyping",
                     "Active on B2B jewelry platforms (IndiaMART, JewelCloud)"],
        "notes": "Casting house serving 200+ jewelers, receives 50+ 3D files/day, quality inconsistency is #1 pain"
    },
    {
        "id": 6, "name": "Maria Santos", "title": "Buying Manager",
        "company": "Brilliance Chain Stores", "industry": "Jewelry Retail",
        "company_size": "200+", "location": "London, UK",
        "email": "maria@brillianceuk.com", "phone": "+44-7XXX-XXXXXX",
        "signals": ["Launching e-commerce or expanding online catalog"],
        "notes": "50-store retail chain, launching online store Q2 2026, needs 3D renders for 5000 SKUs"
    },
]


# ──────────────────────────────────────────────
# ENRICHMENT ENGINE
# ──────────────────────────────────────────────
def enrich_contact(contact: dict) -> dict:
    scores = {}
    total = 0
    industry_match = any(ind.lower().split()[0] in contact.get("industry", "").lower() for ind in ICP_CRITERIA["industries"])
    scores["industry"] = SCORING_WEIGHTS["industry"] if industry_match else 5
    total += scores["industry"]

    size = contact.get("company_size", "")
    size_scores = {"1-10": 14, "11-50": 20, "51-200": 18, "200+": 12}
    scores["size"] = next((v for k, v in size_scores.items() if k in size), 8)
    total += scores["size"]

    location = contact.get("location", "").lower()
    geo_match = any(geo.lower().split()[0] in location for geo in ICP_CRITERIA["geographies"])
    scores["geography"] = SCORING_WEIGHTS["geography"] if geo_match else 5
    total += scores["geography"]

    matched_signals = [s for s in contact.get("signals", []) if s in ICP_CRITERIA["buying_signals"]]
    scores["signals"] = min(30, len(matched_signals) * 10)
    total += scores["signals"]

    notes = contact.get("notes", "").lower()
    disqualified = any(dq.split("(")[0].strip().lower() in notes for dq in ICP_CRITERIA["disqualifiers"])
    if disqualified:
        total += SCORING_WEIGHTS["disqualifier"]

    total = max(0, min(100, total))
    tier = "🔥 HOT" if total >= 70 else "🟡 WARM" if total >= 45 else "🔵 COOL" if total >= 25 else "⚪ COLD"

    if total >= 70:
        approach = f"High-priority. {contact['name']} at {contact['company']} is an ideal fit — lead with ROI story for {contact.get('industry', 'their industry')}. Push for demo within 48hrs."
    elif total >= 45:
        approach = f"Good potential. Needs education on AI-powered 3D modeling. Start with pain-point discovery, follow up with case study relevant to {contact.get('industry', 'their space')}."
    elif total >= 25:
        approach = "Nurture track. Add to content drip — share jewelry tech adoption trends. Re-evaluate in 30 days."
    else:
        approach = "Low priority. Monitor for signal changes. Don't invest outbound effort currently."

    return {
        **contact, "enriched": True, "icp_score": total, "tier": tier,
        "scores": scores, "matched_signals": matched_signals,
        "recommended_approach": approach, "enriched_at": datetime.now().isoformat(),
    }


# ──────────────────────────────────────────────
# AI ENGINE (fal.ai → OpenRouter — OpenAI-compatible)
# ──────────────────────────────────────────────
# Sorted cheapest first. Default = Gemini Flash (~$0.15/1M input tokens)
FAL_LLM_MODELS = [
    "google/gemini-2.5-flash",           # ⭐ DEFAULT — cheapest smart model
    "meta-llama/llama-3.3-70b-instruct", # often FREE on OpenRouter
    "openai/gpt-4o-mini",               # ~$0.15/1M — OpenAI budget
    "google/gemini-2.5-pro",             # ~$1.25/1M — more capable
    "anthropic/claude-3.5-sonnet",       # ~$3/1M — premium
]

FAL_MODEL_LABELS = {
    "google/gemini-2.5-flash":           "⚡ Gemini 2.5 Flash — cheapest & fast",
    "meta-llama/llama-3.3-70b-instruct": "🦙 Llama 3.3 70B — often FREE",
    "openai/gpt-4o-mini":               "💚 GPT-4o Mini — budget OpenAI",
    "google/gemini-2.5-pro":             "🧠 Gemini 2.5 Pro — smarter",
    "anthropic/claude-3.5-sonnet":       "✨ Claude 3.5 Sonnet — premium",
}


def call_fal_openrouter(messages: list, fal_key: str, model: str = "google/gemini-2.5-flash") -> str:
    """Call fal.ai OpenRouter via OpenAI-compatible chat completions API."""
    url = "https://fal.run/openrouter/router/openai/v1/chat/completions"
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "max_tokens": 1024, "temperature": 0.7}

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return data.get("output", data.get("text", str(data)))


def get_ai_response(contact, conversation_history, meeting_link, fal_key, model="google/gemini-2.5-flash"):
    if not fal_key:
        return _fallback_response(contact, conversation_history, meeting_link)
    try:
        contact_info = f"Name: {contact['name']}\nTitle: {contact.get('title','N/A')}\nCompany: {contact.get('company','N/A')}\nIndustry: {contact.get('industry','N/A')}\nSize: {contact.get('company_size','N/A')}\nLocation: {contact.get('location','N/A')}\nNotes: {contact.get('notes','N/A')}"
        enrichment_info = f"ICP Score: {contact.get('icp_score','N/A')}/100\nTier: {contact.get('tier','N/A')}\nMatched Signals: {', '.join(contact.get('matched_signals',[]))}\nApproach: {contact.get('recommended_approach','N/A')}"
        system = SYSTEM_PROMPT.format(meeting_link=meeting_link, contact_info=contact_info, enrichment_data=enrichment_info)

        messages = [{"role": "system", "content": system}]
        for msg in conversation_history:
            role = "assistant" if msg["role"] == "sdr" else "user"
            messages.append({"role": role, "content": msg["content"]})

        response = call_fal_openrouter(messages, fal_key, model).strip()
        for prefix in ["[SDR]:", "[SDR (you)]:", "SDR:", "JB:", "**SDR:**", "**JB:**"]:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        return response

    except requests.exceptions.HTTPError as e:
        detail = ""
        try: detail = e.response.json()
        except: detail = e.response.text[:300] if e.response else str(e)
        st.error(f"fal.ai API Error ({e.response.status_code}): {detail}")
        return _fallback_response(contact, conversation_history, meeting_link)
    except Exception as e:
        st.error(f"fal.ai Error: {e}")
        return _fallback_response(contact, conversation_history, meeting_link)


def _fallback_response(contact, conversation_history, meeting_link):
    first_name = contact.get("name", "there").split()[0]
    company = contact.get("company", "your company")
    industry = contact.get("industry", "the jewelry space")

    if len(conversation_history) <= 1:
        openers = [
            f"Hey {first_name}! I've been looking at what {company} is doing in {industry.lower()} — really impressive stuff. Quick question: how long does it typically take your team to go from a new design concept to a production-ready 3D model?\n\nAsking because we've built something at JewelBench that's cutting that from days to literally minutes for businesses like yours.",
            f"Hi {first_name}, noticed {company} is doing great work in {industry.lower()}. Had a thought — what if you could turn any jewelry photo into a castable 3D file in under 10 minutes? Would that change your workflow at all?\n\nWe're doing exactly that at JewelBench and I'd love to show you.",
            f"{first_name} — quick one. Does your team still send designs to external CAD modelers, or do you handle 3D modeling in-house? Either way, I think I have something that'll seriously speed up your pipeline.\n\nWe're JewelBench AI — we turn jewelry photos into production-ready 3D models using AI.",
        ]
        return random.choice(openers)

    last_msg = conversation_history[-1]["content"].lower() if conversation_history else ""
    if any(w in last_msg for w in ["price", "cost", "expensive", "how much", "budget", "pay"]):
        return f"Great question. We deliberately didn't go the per-seat licensing route like RhinoGold — that gets expensive fast.\n\nJewelBench runs on a token system. Each 3D generation costs tokens. Most customers spend a fraction of what they were paying freelance CAD modelers — we're talking ₹15-50K per model with freelancers vs. a few hundred tokens with us.\n\nWant me to walk through the ROI for {company}'s specific volume? I can show you the math in a quick 15-min call.\n\n📅 **[Book a 15-min Demo →]({meeting_link})**"
    if any(w in last_msg for w in ["quality", "accurate", "reliable", "production", "casting"]):
        return f"The #1 question we get — and the right one. Nobody wants to waste gold on a bad file.\n\nWe have a hardcoded 13× scaling factor in every model (10× cm→mm + 1.3× jewelry sizing). Weight estimates match real casting within 2-3%.\n\nThe mesh quality comes from Meshy v6 — currently the best AI mesh generator for organic jewelry shapes.\n\n📅 **[Book a 15-min Demo →]({meeting_link})**"
    if any(w in last_msg for w in ["interest", "demo", "show", "meeting", "book", "sure", "yes", "sounds good", "let's"]):
        return f"Awesome, {first_name}! Here's what we'll cover in 15 min:\n\n→ Live demo with one of YOUR jewelry images\n→ Batch variation engine walkthrough\n→ Quick ROI calculation for {company}\n→ Q&A on your specific workflow\n\n📅 **[Book a 15-min Demo →]({meeting_link})**\n\nI'll also prep sample outputs from your website before the call so you see exactly what YOUR catalog would look like. 🔥"
    if any(w in last_msg for w in ["not now", "busy", "later", "not sure", "think about"]):
        return f"Totally fair, {first_name}. No pressure.\n\nQuick thought though — if {company} is spending 2-3 days per 3D model or paying external modelers, the math on JewelBench usually speaks for itself pretty fast.\n\nHow about I send you a quick 2-min video showing photo-to-3D in action? No commitment, just so you have it when timing's right.\n\nWhat's the best email for that?"
    return f"Good question, {first_name}. For {company} specifically — the core problem we solve is the gap between having a jewelry design idea and having a production-ready 3D file.\n\nJewelBench closes that gap from days to minutes. Whether you're prototyping new collections, building catalogs, or showing clients 3D renders before production — we handle it all.\n\n📅 **[Book a 15-min Demo →]({meeting_link})**"


def generate_opening_message(contact, meeting_link, fal_key, model="google/gemini-2.5-flash"):
    conversation = [{"role": "user", "content": f"[SYSTEM: Generate your opening outreach message to {contact['name']}. This is a cold outreach — be natural, reference their company/industry, ask a discovery question, and spark curiosity about JewelBench. Keep it under 100 words.]"}]
    return get_ai_response(contact, conversation, meeting_link, fal_key, model)


# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "contacts" not in st.session_state:
    st.session_state.contacts = {c["id"]: c for c in SAMPLE_CONTACTS}
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "active_contact_id" not in st.session_state:
    st.session_state.active_contact_id = None
if "meeting_link" not in st.session_state:
    st.session_state.meeting_link = "https://calendly.com/jewelbench-demo/15min"
if "fal_key" not in st.session_state:
    st.session_state.fal_key = ""
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "google/gemini-2.5-flash"


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ◈ JewelBench AI SDR")
    st.caption("Enrich → Outreach → Book Meetings")
    st.divider()

    # fal.ai Key
    fal_key_input = st.text_input(
        "🔑 fal.ai API Key",
        value=st.session_state.fal_key,
        type="password",
        help="Get yours at fal.ai/dashboard/keys"
    )
    if fal_key_input != st.session_state.fal_key:
        st.session_state.fal_key = fal_key_input
    if not st.session_state.fal_key:
        st.warning("Add your fal.ai key for AI conversations. Without it, SDR uses smart templates.")
    else:
        st.success("✓ fal.ai key set — AI SDR active")

    st.divider()

    # Model selector
    model_labels = [FAL_MODEL_LABELS.get(m, m) for m in FAL_LLM_MODELS]
    current_idx = FAL_LLM_MODELS.index(st.session_state.llm_model) if st.session_state.llm_model in FAL_LLM_MODELS else 0
    selected_label = st.selectbox("🧠 AI Model (via fal.ai → OpenRouter)", model_labels, index=current_idx,
                                   help="All models billed through your fal.ai account. Gemini Flash is cheapest.")
    selected_model = FAL_LLM_MODELS[model_labels.index(selected_label)]
    if selected_model != st.session_state.llm_model:
        st.session_state.llm_model = selected_model

    st.divider()

    # Meeting link
    meeting_link_input = st.text_input("📅 SDR Meeting Link", value=st.session_state.meeting_link,
                                        help="Calendly or booking link for your SDR")
    if meeting_link_input != st.session_state.meeting_link:
        st.session_state.meeting_link = meeting_link_input

    st.divider()

    # Navigation
    page = st.radio("Navigate", ["📊 Dashboard", "👥 Contacts", "💬 Outreach", "⚙️ ICP Config"], label_visibility="collapsed")

    st.divider()

    # Stats
    contacts = st.session_state.contacts
    enriched = [c for c in contacts.values() if c.get("enriched")]
    st.markdown(f"""
    <div style="font-size: 12px; color: #6b7094;">
        <div>Contacts: <strong style="color: #e2e4f0;">{len(contacts)}</strong></div>
        <div>Enriched: <strong style="color: #10b981;">{len(enriched)}</strong></div>
        <div>Hot Leads: <strong style="color: #ef4444;">{len([c for c in enriched if '🔥' in c.get('tier', '')])}</strong></div>
        <div>Active Convos: <strong style="color: #c9a84c;">{len(st.session_state.conversations)}</strong></div>
        <div style="margin-top:8px;">Model: <strong style="color: #c9a84c;">{st.session_state.llm_model.split('/')[-1]}</strong></div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown("# 📊 Command Center")
    st.caption("Enrich contacts against your ICP, then deploy AI-powered outreach to book meetings.")

    col1, col2, col3, col4 = st.columns(4)
    total = len(contacts)
    enriched_count = len(enriched)
    hot_count = len([c for c in enriched if "🔥" in c.get("tier", "")])
    warm_count = len([c for c in enriched if "🟡" in c.get("tier", "")])

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Contacts</div><div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Enriched</div><div class="metric-value" style="color:#10b981;">{enriched_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Hot Leads</div><div class="metric-value" style="color:#ef4444;">{hot_count}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Warm Leads</div><div class="metric-value" style="color:#f59e0b;">{warm_count}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("◈ Enrich All Contacts", use_container_width=True, type="primary"):
            progress = st.progress(0, text="Enriching...")
            for i, (cid, contact) in enumerate(st.session_state.contacts.items()):
                st.session_state.contacts[cid] = enrich_contact(contact)
                progress.progress((i+1)/len(contacts), text=f"Enriched {contact['name']}...")
                time.sleep(0.3)
            progress.progress(1.0, text="✓ Done!")
            time.sleep(0.5)
            st.rerun()
    with col_b:
        st.button("📥 Upload CSV (coming soon)", use_container_width=True, disabled=True)

    if enriched:
        st.markdown("### Pipeline Breakdown")
        tiers = {"🔥 HOT": 0, "🟡 WARM": 0, "🔵 COOL": 0, "⚪ COLD": 0}
        for c in enriched:
            t = c.get("tier", "⚪ COLD")
            if t in tiers: tiers[t] += 1
        cols = st.columns(4)
        tier_colors = {"🔥 HOT": "#ef4444", "🟡 WARM": "#f59e0b", "🔵 COOL": "#3b82f6", "⚪ COLD": "#6b7094"}
        for i, (tier, count) in enumerate(tiers.items()):
            with cols[i]:
                pct = (count / len(enriched)) * 100 if enriched else 0
                st.markdown(f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:{tier_colors[tier]};font-family:Outfit;">{count}</div><div style="font-size:12px;color:#6b7094;">{tier}</div><div class="score-bar-bg" style="margin-top:8px;"><div class="score-bar-fill" style="width:{pct}%;background:{tier_colors[tier]};"></div></div></div>', unsafe_allow_html=True)

        st.markdown("### 🔥 Top Leads")
        for lead in sorted(enriched, key=lambda x: x.get("icp_score", 0), reverse=True)[:5]:
            color = '#ef4444' if lead['icp_score'] >= 70 else '#f59e0b' if lead['icp_score'] >= 45 else '#6b7094'
            st.markdown(f'<div class="contact-row" style="display:flex;justify-content:space-between;align-items:center;"><div><strong>{lead["name"]}</strong> · {lead.get("title","")}<br><span style="color:#6b7094;font-size:12px;">{lead["company"]} · {lead.get("location","")}</span></div><div style="font-family:Outfit;font-weight:800;font-size:20px;color:{color};">{lead["icp_score"]} <span style="font-size:12px;">{lead["tier"]}</span></div></div>', unsafe_allow_html=True)

    st.markdown("### ◈ Your ICP at a Glance")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Target Industries**")
        st.markdown(" ".join([f'<span class="icp-tag">{ind}</span>' for ind in ICP_CRITERIA["industries"]]), unsafe_allow_html=True)
    with col2:
        st.markdown("**Key Buying Signals**")
        for sig in ICP_CRITERIA["buying_signals"][:4]:
            st.markdown(f'<span class="signal-tag">✓ {sig}</span>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CONTACTS
# ──────────────────────────────────────────────
elif page == "👥 Contacts":
    st.markdown("# 👥 Contacts")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by name or company...", label_visibility="collapsed")
    with col2:
        tier_filter = st.selectbox("Tier", ["All", "🔥 HOT", "🟡 WARM", "🔵 COOL", "⚪ COLD"], label_visibility="collapsed")
    with col3:
        if st.button("◈ Enrich All", use_container_width=True, type="primary"):
            for cid, c in st.session_state.contacts.items():
                st.session_state.contacts[cid] = enrich_contact(c)
            st.rerun()

    st.divider()
    filtered = list(st.session_state.contacts.values())
    if search:
        filtered = [c for c in filtered if search.lower() in c["name"].lower() or search.lower() in c.get("company","").lower()]
    if tier_filter != "All":
        filtered = [c for c in filtered if c.get("tier") == tier_filter]

    for contact in sorted(filtered, key=lambda x: x.get("icp_score", 0), reverse=True):
        label = f"**{contact['name']}** · {contact.get('title','')} @ {contact.get('company','')}"
        label += f" — Score: {contact['icp_score']} {contact['tier']}" if contact.get("enriched") else " — Not enriched"
        with st.expander(label, expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Company:** {contact.get('company','N/A')}  \n**Industry:** {contact.get('industry','N/A')}  \n**Size:** {contact.get('company_size','N/A')}  \n**Location:** {contact.get('location','N/A')}  \n**Email:** {contact.get('email','N/A')}")
                if contact.get("notes"): st.markdown(f"**Notes:** {contact['notes']}")
            with col2:
                if contact.get("enriched"):
                    st.markdown("**ICP Score Breakdown**")
                    for k, v in contact.get("scores", {}).items():
                        mx = SCORING_WEIGHTS.get(k, 30)
                        pct = min(100, (v/mx)*100)
                        color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 40 else "#6b7094"
                        st.markdown(f'<div style="margin-bottom:6px;"><div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7094;"><span>{k.title()}</span><span style="color:{color};font-weight:700;">{v}/{mx}</span></div><div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%;background:{color};"></div></div></div>', unsafe_allow_html=True)
                    if contact.get("matched_signals"):
                        st.markdown("**Matched Signals**")
                        for s in contact["matched_signals"]:
                            st.markdown(f'<span class="signal-tag">✓ {s}</span>', unsafe_allow_html=True)
            if contact.get("enriched"):
                st.markdown(f"**Recommended Approach:** {contact.get('recommended_approach','')}")
                if st.button(f"💬 Start Outreach with {contact['name']}", key=f"chat_{contact['id']}", type="primary"):
                    st.session_state.active_contact_id = contact["id"]
                    st.rerun()

    st.divider()
    st.markdown("### ➕ Add New Contact")
    with st.form("add_contact"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name*")
            new_company = st.text_input("Company*")
            new_industry = st.selectbox("Industry", ICP_CRITERIA["industries"])
            new_email = st.text_input("Email")
        with col2:
            new_title = st.text_input("Job Title")
            new_size = st.selectbox("Company Size", ICP_CRITERIA["company_sizes"])
            new_location = st.text_input("Location")
            new_phone = st.text_input("Phone")
        new_signals = st.multiselect("Buying Signals", ICP_CRITERIA["buying_signals"])
        new_notes = st.text_area("Notes", height=80)
        if st.form_submit_button("Add & Enrich Contact", type="primary"):
            if new_name and new_company:
                new_id = max(st.session_state.contacts.keys()) + 1 if st.session_state.contacts else 1
                new_contact = {"id": new_id, "name": new_name, "title": new_title, "company": new_company,
                              "industry": new_industry, "company_size": new_size.split(" ")[0],
                              "location": new_location, "email": new_email, "phone": new_phone,
                              "signals": new_signals, "notes": new_notes}
                st.session_state.contacts[new_id] = enrich_contact(new_contact)
                st.success(f"✓ Added & enriched {new_name}")
                st.rerun()
            else:
                st.error("Name and Company are required.")


# ──────────────────────────────────────────────
# OUTREACH
# ──────────────────────────────────────────────
elif page == "💬 Outreach":
    st.markdown("# 💬 AI Outreach")
    enriched_contacts = {cid: c for cid, c in st.session_state.contacts.items() if c.get("enriched")}

    if not enriched_contacts:
        st.info("No enriched contacts yet. Go to **Contacts** and click **Enrich All** first.")
    else:
        contact_options = {f"{c['name']} · {c['company']} ({c['tier']})": cid
                          for cid, c in sorted(enriched_contacts.items(), key=lambda x: x[1].get("icp_score",0), reverse=True)}
        default_idx = 0
        if st.session_state.active_contact_id:
            for i, (_, cid) in enumerate(contact_options.items()):
                if cid == st.session_state.active_contact_id: default_idx = i; break

        selected_label = st.selectbox("Select contact", list(contact_options.keys()), index=default_idx)
        selected_cid = contact_options[selected_label]
        contact = st.session_state.contacts[selected_cid]
        st.session_state.active_contact_id = selected_cid

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{contact['name']}** — {contact.get('title','')} at **{contact['company']}**")
            st.caption(f"{contact.get('industry','')} · {contact.get('location','')} · Score: {contact['icp_score']}")
        with col2:
            if contact.get("matched_signals"):
                for s in contact["matched_signals"][:2]:
                    st.markdown(f'<span class="signal-tag" style="font-size:10px;">✓ {s}</span>', unsafe_allow_html=True)
        with col3:
            st.caption(f"Model: **{st.session_state.llm_model.split('/')[-1]}**")

        st.divider()
        if selected_cid not in st.session_state.conversations:
            st.session_state.conversations[selected_cid] = []
        convo = st.session_state.conversations[selected_cid]

        if not convo:
            st.markdown('<div style="text-align:center;padding:40px;color:#3d4268;"><div style="font-size:48px;margin-bottom:12px;opacity:0.3;">◈</div><div>Click below to generate an AI-powered opening message</div></div>', unsafe_allow_html=True)
            if st.button("🚀 Generate Opening Message & Start Outreach", type="primary", use_container_width=True):
                with st.spinner("AI SDR is crafting the perfect opener..."):
                    opener = generate_opening_message(contact, st.session_state.meeting_link, st.session_state.fal_key, st.session_state.llm_model)
                    st.session_state.conversations[selected_cid] = [{"role": "sdr", "content": opener, "time": datetime.now().isoformat()}]
                    st.rerun()
        else:
            for msg in convo:
                if msg["role"] == "sdr":
                    st.markdown(f'<div class="chat-sdr"><div class="chat-sender sdr-name">◈ JewelBench SDR (AI)</div><div style="font-size:14px;line-height:1.7;white-space:pre-wrap;">{msg["content"]}</div><div style="font-size:10px;color:#3d4268;margin-top:8px;">{msg.get("time","")[:19]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-contact"><div class="chat-sender contact-name">💬 {contact["name"]}</div><div style="font-size:14px;line-height:1.7;">{msg["content"]}</div><div style="font-size:10px;color:#3d4268;margin-top:8px;">{msg.get("time","")[:19]}</div></div>', unsafe_allow_html=True)

            st.markdown("")
            st.caption(f"💡 Type as **{contact['name']}** would respond — the AI SDR will reply with product knowledge and push toward booking.")
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_input("Contact response", placeholder=f"Type {contact['name']}'s reply here...", key=f"input_{selected_cid}_{len(convo)}", label_visibility="collapsed")
            with col2:
                send = st.button("Send ➤", type="primary", use_container_width=True)

            st.markdown("**Quick replies:**")
            quick_cols = st.columns(4)
            quick_replies = ["How much does it cost?", "We already use RhinoGold", "Sounds interesting, show me a demo", "Not the right time for us"]
            quick_selected = None
            for i, qr in enumerate(quick_replies):
                with quick_cols[i]:
                    if st.button(qr, key=f"qr_{i}_{len(convo)}", use_container_width=True):
                        quick_selected = qr

            input_to_process = quick_selected or (user_input if send and user_input else None)
            if input_to_process:
                st.session_state.conversations[selected_cid].append({"role": "contact", "content": input_to_process, "time": datetime.now().isoformat()})
                with st.spinner("AI SDR is typing..."):
                    response = get_ai_response(contact, st.session_state.conversations[selected_cid], st.session_state.meeting_link, st.session_state.fal_key, st.session_state.llm_model)
                st.session_state.conversations[selected_cid].append({"role": "sdr", "content": response, "time": datetime.now().isoformat()})
                st.rerun()

            if len(convo) > 1:
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    contact_name = contact["name"]
                    lines = []
                    for m in convo:
                        sender = "[SDR]" if m["role"] == "sdr" else f"[{contact_name}]"
                        lines.append(f"{sender}: {m['content']}")
                    export_text = "\n\n".join(lines)
                    st.download_button("📥 Export Conversation", export_text, file_name=f"outreach_{contact_name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
                with col2:
                    if st.button("🗑️ Reset Conversation"):
                        st.session_state.conversations[selected_cid] = []
                        st.rerun()


# ──────────────────────────────────────────────
# ICP CONFIG
# ──────────────────────────────────────────────
elif page == "⚙️ ICP Config":
    st.markdown("# ⚙️ ICP Configuration")
    st.caption("View the Ideal Customer Profile used for contact enrichment and scoring.")

    st.markdown("### 📊 Scoring Weights")
    cols = st.columns(4)
    weights = [("Industry Match", 25, "#c9a84c", "Industry alignment"), ("Company Size", 20, "#3b82f6", "Size fit"), ("Geography", 15, "#10b981", "Market match"), ("Buying Signals", 30, "#ef4444", "Intent indicators")]
    for i, (label, weight, color, desc) in enumerate(weights):
        with cols[i]:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color};font-size:28px;">{weight}</div><div class="metric-label">{label}</div><div style="font-size:11px;color:#6b7094;margin-top:8px;">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### 🎯 Tier Thresholds")
    for tier, score_range, strategy, color in [("🔥 HOT","70-100","Push for demo within 48hrs","#ef4444"),("🟡 WARM","45-69","Pain-point discovery → case study","#f59e0b"),("🔵 COOL","25-44","Nurture with content drip","#3b82f6"),("⚪ COLD","0-24","Monitor for signal changes","#6b7094")]:
        st.markdown(f'<div style="display:flex;align-items:center;gap:16px;padding:10px 16px;background:#12131a;border:1px solid #1e2030;border-left:3px solid {color};border-radius:8px;margin:6px 0;"><div style="min-width:80px;font-weight:700;">{tier}</div><div style="min-width:60px;color:{color};font-family:Outfit;font-weight:700;">{score_range}</div><div style="color:#6b7094;font-size:13px;">{strategy}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏭 Target Industries")
        for ind in ICP_CRITERIA["industries"]:
            st.markdown(f'<span class="icp-tag">{ind}</span>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("### 🌍 Target Geographies")
        for geo in ICP_CRITERIA["geographies"]:
            st.markdown(f'<span class="icp-tag">{geo}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown("### 📡 Buying Signals (10pts each, max 30)")
        for sig in ICP_CRITERIA["buying_signals"]:
            st.markdown(f'<span class="signal-tag">✓ {sig}</span>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("### 🚫 Disqualifiers (-50pts)")
        for dq in ICP_CRITERIA["disqualifiers"]:
            st.markdown(f"<span style='display:inline-block;background:rgba(239,68,68,0.1);color:#ef4444;padding:3px 8px;border-radius:4px;font-size:11px;margin:2px;'>✗ {dq}</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🧠 SDR Product Knowledge")
    with st.expander("View full SDR system prompt"):
        st.code(SYSTEM_PROMPT.replace("{meeting_link}", "[MEETING_LINK]").replace("{contact_info}", "[CONTACT_INFO]").replace("{enrichment_data}", "[ENRICHMENT_DATA]"), language="markdown")
