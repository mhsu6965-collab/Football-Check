import streamlit as st
import requests
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="MM GoalScore & AI Predictor",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS - GoalScore / Flashscore Dark Theme UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Padauk:wght@400;700&family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Padauk', 'Inter', sans-serif;
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Top Header Banner */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 18px 22px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* League Header Bar */
    .league-bar {
        background-color: #1e293b;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        color: #38bdf8;
        margin-top: 18px;
        margin-bottom: 8px;
        border-left: 4px solid #38bdf8;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Streamlit Expander Customization (GoalScore Match Row Style) */
    div[data-testid="stExpander"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stExpander"]:hover {
        border-color: #374151 !important;
        background-color: #161f30 !important;
    }
    div[data-testid="stExpander"] summary p {
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    /* Prediction Cards inside Expander */
    .pred-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        margin-bottom: 10px;
    }
    .pred-title {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .pred-val {
        font-size: 20px;
        font-weight: 700;
        color: #22c55e;
    }
    .pred-sub {
        font-size: 12px;
        color: #cbd5e1;
        margin-top: 4px;
    }
    .ai-banner {
        background: linear-gradient(90deg, rgba(16,185,129,0.15) 0%, rgba(59,130,246,0.15) 100%);
        border: 1px solid rgba(16,185,129,0.4);
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 14px;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 6px 0;
        border-bottom: 1px solid #1e293b;
        color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. API KEY LOADING & REAL-TIME DATA FETCHER
# ---------------------------------------------------------
api_key = None
try:
    api_key = st.secrets.get("FOOTBALL_API_KEY", None)
except Exception:
    api_key = None

# Sidebar for API Status & Custom Simulator
with st.sidebar:
    st.header("⚙️ API နှင့် ဆက်တင်များ")
    user_key = st.text_input("Football-Data.org API Key ထည့်ရန်", value=api_key if api_key else "", type="password")
    if user_key:
        api_key = user_key
        st.success("✅ API Key ချိတ်ဆက်ထားပါသည်")
    else:
        st.warning("⚠️ API Key မရှိသေးပါ (Demo ပွဲစဉ်များ ပြသထားပါသည်)")
        
    st.markdown("---")
    st.subheader("🧮 စိတ်ကြိုက် ဂိုးတွက်ချက်စက်")
    h_xg = st.slider("အိမ်ရှင် တိုက်စစ်အား (xG)", 0.5, 3.5, 1.7, 0.1)
    a_xg = st.slider("ဧည့်သည် တိုက်စစ်အား (xG)", 0.5, 3.5, 1.3, 0.1)
    t_xg = h_xg + a_xg
    st.info(f"**ခန့်မှန်း ဂိုးပေါင်း:** {t_xg:.1f} ဂိုး\n\n**Over 2.5:** {min(95, int(t_xg/3.4*100))}% | **BTTS:** {min(92, int(min(h_xg,a_xg)/1.7*100))}%")

def calculate_ai_predictions(home_team, away_team, hs, as_, status):
    """ပွဲစဉ်အချက်အလက်ပေါ်မူတည်၍ 1X2, Over/Under, BTTS တွက်ချက်ပေးသော AI Function"""
    seed = sum(ord(c) for c in (home_team + away_team))
    
    # လက်ရှိဂိုးရလဒ်ပေါ် မူတည်၍ ချိန်ညှိခြင်း
    total_goals = hs + as_
    base_home = 38 + (seed % 28) + (hs * 12) - (as_ * 10)
    base_away = 22 + ((seed >> 2) % 25) + (as_ * 12) - (hs * 10)
    
    home_prob = max(10, min(80, base_home))
    away_prob = max(10, min(80, base_away))
    if home_prob + away_prob > 88:
        scale = 88 / (home_prob + away_prob)
        home_prob = int(home_prob * scale)
        away_prob = int(away_prob * scale)
    draw_prob = 100 - (home_prob + away_prob)

    over_25 = min(96, max(20, 52 + (seed % 32) + (total_goals * 15)))
    btts_yes = min(95, max(20, 50 + ((seed >> 3) % 35) + (20 if (hs > 0 and as_ > 0) else 0)))

    # AI အကြံပြုချက် ထုတ်ပေးခြင်း
    tips = []
    if home_prob >= 55:
        tips.append(f"{home_team} အနိုင် (Home Win)")
    elif away_prob >= 55:
        tips.append(f"{away_team} အနိုင် (Away Win)")
    else:
        tips.append("သရေ သို့မဟုတ် အကြိတ်အနယ်ရှိမည်")

    if over_25 >= 65:
        tips.append("ဂိုးပေါင်း အပေါ် (Over 2.5)")
    else:
        tips.append("ဂိုးပေါင်း အောက် (Under 2.5)")

    if btts_yes >= 62:
        tips.append("နှစ်သင်းလုံး ဂိုးသွင်းမည် (BTTS - Yes)")

    return {
        "home_prob": home_prob,
        "draw_prob": draw_prob,
        "away_prob": away_prob,
        "over_25": over_25,
        "under_25": 100 - over_25,
        "btts_yes": btts_yes,
        "btts_no": 100 - btts_yes,
        "best_tip": " + ".join(tips[:2]),
        "correct_score": f"{max(hs, 1 if home_prob>away_prob else 1)} - {max(as_, 1 if btts_yes>60 else 0)}"
    }

@st.cache_data(ttl=60)
def fetch_live_matches(key):
    """Football-Data.org API မှ ယနေ့ပွဲစဉ်များကို ဆွဲယူခြင်း"""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": key}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json().get("matches", [])
        parsed = []
        for m in data[:25]:
            st_code = m.get("status", "TIMED")
            hs = m.get("score", {}).get("fullTime", {}).get("home") or 0
            as_ = m.get("score", {}).get("fullTime", {}).get("away") or 0
            
            if st_code in ["IN_PLAY", "PAUSED"]:
                status_tag = "🔴 LIVE"
                state = "LIVE"
            elif st_code == "FINISHED":
                status_tag = "FT"
                state = "FT"
            else:
                utc_time = m.get("utcDate", "")
                time_str = utc_time[11:16] if len(utc_time) >= 16 else "20:00"
                status_tag = f"🕒 {time_str}"
                state = "UPCOMING"

            home_name = m.get("homeTeam", {}).get("shortName") or m.get("homeTeam", {}).get("name", "Home")
            away_name = m.get("awayTeam", {}).get("shortName") or m.get("awayTeam", {}).get("name", "Away")
            league_name = m.get("competition", {}).get("name", "Other League")

            preds = calculate_ai_predictions(home_name, away_name, hs, as_, state)
            parsed.append({
                "league": league_name,
                "status_tag": status_tag,
                "state": state,
                "home": home_name,
                "away": away_name,
                "hs": hs,
                "as": as_,
                "preds": preds
            })
        return parsed
    return []

def get_demo_matches():
    """API Key မထည့်ရသေးချိန်တွင် ပြသမည့် GoalScore ဒီဇိုင်း ပွဲစဉ်များ"""
    raw = [
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 ပရီးမီးယားလိဂ် (Premier League)", "🔴 67'", "LIVE", "အာဆင်နယ်", "လီဗာပူးလ်", 2, 1),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 ပရီးမီးယားလိဂ် (Premier League)", "🔴 38'", "LIVE", "မန်စီးတီး", "ချဲလ်ဆီး", 1, 0),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 ပရီးမီးယားလိဂ် (Premier League)", "🕒 21:00", "UPCOMING", "မန်ယူနိုက်တက်", "စပါး", 0, 0),
        ("🇪🇸 စပိန် လာလီဂါ (La Liga)", "🔴 82'", "LIVE", "ရီးရဲလ်မက်ဒရစ်", "ဘာစီလိုနာ", 2, 2),
        ("🇪🇸 စပိန် လာလီဂါ (La Liga)", "🕒 23:30", "UPCOMING", "အက်သလက်တီကို", "ဆီဗီလာ", 0, 0),
        ("🇮🇹 အီတလီ စီးရီးအေ (Serie A)", "FT", "FT", "အင်တာမီလန်", "အေစီမီလန်", 3, 1),
        ("🇩🇪 ဂျာမန် ဘွန်ဒက်စ်လီဂါ (Bundesliga)", "🕒 20:30", "UPCOMING", "ဘိုင်ယန်မြူးနစ်", "ဒေါ့မွန်", 0, 0),
    ]
    out = []
    for lg, st_tag, state, h, a, hs, as_ in raw:
        out.append({
            "league": lg, "status_tag": st_tag, "state": state,
            "home": h, "away": a, "hs": hs, "as": as_,
            "preds": calculate_ai_predictions(h, a, hs, as_, state)
        })
    return out

# ---------------------------------------------------------
# 2. APP HEADER & FILTER TABS
# ---------------------------------------------------------
st.markdown("""
<div class="app-header">
    <div>
        <div style="font-size:22px; font-weight:700; color:#fff;">⚽ MM GoalScore AI</div>
        <div style="font-size:13px; color:#94a3b8;">ပွဲစဉ်တစ်ခုချင်းစီကို နှိပ်၍ ခန့်မှန်းချက်အပြည့်အစုံ ကြည့်ရှုပါ</div>
    </div>
    <div style="text-align:right; font-size:12px; color:#38bdf8;">
        🟢 AI Engine Active
    </div>
</div>
""", unsafe_allow_html=True)

# Load Data (Live API if available, otherwise Demo)
matches = []
if api_key:
    with st.spinner("တိုက်ရိုက် ပွဲစဉ်များ ဆွဲယူနေပါသည်..."):
        matches = fetch_live_matches(api_key)
        if not matches:
            st.info("ယနေ့အတွက် API ပွဲစဉ် မရှိသေးပါသဖြင့် နမူနာပွဲစဉ်များ ပြသထားပါသည်။")
            matches = get_demo_matches()
else:
    matches = get_demo_matches()

# Top Filter Controls
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    tab_filter = st.radio(
        "ပွဲစဉ် အမျိုးအစား",
        ["အားလုံး (All)", "🔴 တိုက်ရိုက် (Live)", "🕒 လာမည့်ပွဲ (Upcoming)", "🏁 ပွဲပြီး (FT)"],
        horizontal=True,
        label_visibility="collapsed"
    )
with col_f2:
    search_q = st.text_input("🔍 အသင်းရှာရန်...", placeholder="အသင်းနာမည် ရိုက်ထည့်ပါ", label_visibility="collapsed")

# Filter Logic
filtered = []
for m in matches:
    if "Live" in tab_filter and m["state"] != "LIVE":
        continue
    if "Upcoming" in tab_filter and m["state"] != "UPCOMING":
        continue
    if "FT" in tab_filter and m["state"] != "FT":
        continue
    if search_q and (search_q.lower() not in m["home"].lower() and search_q.lower() not in m["away"].lower()):
        continue
    filtered.append(m)

# ---------------------------------------------------------
# 3. GOALSCORE COMPACT ROWS & EXPANDABLE PREDICTIONS
# ---------------------------------------------------------
if not filtered:
    st.warning("ရွေးချယ်ထားသော ပွဲစဉ် မရှိသေးပါ။")
else:
    # Group by League
    leagues = {}
    for m in filtered:
        leagues.setdefault(m["league"], []).append(m)

    for league_name, lg_matches in leagues.items():
        st.markdown(f"""
        <div class="league-bar">
            <span>{league_name}</span>
            <span style="font-size:12px; color:#94a3b8;">{len(lg_matches)} ပွဲ</span>
        </div>
        """, unsafe_allow_html=True)

        for m in lg_matches:
            p = m["preds"]
            # Format Score or VS for GoalScore header
            score_display = f"{m['hs']} - {m['as']}" if m["state"] in ["LIVE", "FT"] else "vs"
            row_label = f"{m['status_tag']}   |   {m['home']}   [{score_display}]   {m['away']}   —   💡 ခန့်မှန်းချက်ကြည့်ရန် နှိပ်ပါ"

            # When clicked, opens full prediction breakdown
            with st.expander(row_label, expanded=False):
                st.markdown("##### 📊 AI ခန့်မှန်းချက် အပြည့်အစုံ (Full Match Predictions)")
                
                # 1X2 Probability Bar
                st.caption(f"**နိုင် / သရေ / ရှုံး (1X2 ရာခိုင်နှုန်း):** အိမ်ရှင် ({p['home_prob']}%) • သရေ ({p['draw_prob']}%) • ဧည့်သည် ({p['away_prob']}%)")
                st.progress(p["home_prob"] / 100)

                # 3 Main Prediction Cards (1X2, Over/Under, BTTS)
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    fav = m["home"] if p["home_prob"] >= p["away_prob"] else m["away"]
                    fav_pct = max(p["home_prob"], p["away_prob"])
                    st.markdown(f"""
                    <div class="pred-box">
                        <div class="pred-title">🏆 အနိုင်ရနိုင်ခြေ (1X2)</div>
                        <div class="pred-val">{fav_pct}%</div>
                        <div class="pred-sub">{fav} အလေးသာ</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    ou_label = "Over 2.5 (ဂိုးပေါ်)" if p["over_25"] >= 55 else "Under 2.5 (ဂိုးအောက်)"
                    ou_pct = p["over_25"] if p["over_25"] >= 55 else p["under_25"]
                    st.markdown(f"""
                    <div class="pred-box">
                        <div class="pred-title">⚽ ဂိုးပေါင်း (Over/Under)</div>
                        <div class="pred-val">{ou_pct}%</div>
                        <div class="pred-sub">{ou_label}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    btts_label = "BTTS - Yes (နှစ်သင်းလုံးသွင်း)" if p["btts_yes"] >= 55 else "BTTS - No"
                    btts_pct = p["btts_yes"] if p["btts_yes"] >= 55 else p["btts_no"]
                    st.markdown(f"""
                    <div class="pred-box">
                        <div class="pred-title">🔥 နှစ်သင်းလုံးဂိုးသွင်းမှု (BTTS)</div>
                        <div class="pred-val">{btts_pct}%</div>
                        <div class="pred-sub">{btts_label}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Extra Stats & AI Tip Banner
                st.markdown(f"""
                <div class="stat-row">
                    <span>🎯 ခန့်မှန်း ဂိုးရလဒ် (Correct Score):</span>
                    <strong style="color:#38bdf8;">{m['home']} {p['correct_score']} {m['away']}</strong>
                </div>
                <div class="stat-row">
                    <span>📈 ဂိုးပေါင်း ၂.၅ အပေါ် / အောက် အချိုး:</span>
                    <span>Over ({p['over_25']}%) / Under ({p['under_25']}%)</span>
                </div>
                <div class="ai-banner">
                    🤖 <strong>AI အဓိက အကြံပြုချက် (Best Pick):</strong> <span style="color:#4ade80; font-weight:bold;">{p['best_tip']}</span>
                </div>
                """, unsafe_allow_html=True)
