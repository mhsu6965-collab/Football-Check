import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="MM Football AI Predictor",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS for Myanmar Font & Modern Dark UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Padauk:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Padauk', sans-serif;
    }
    .match-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        color: white;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .upcoming-badge {
        background-color: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
    }
    .score-box {
        font-size: 28px;
        font-weight: bold;
        color: #38bdf8;
        text-align: center;
    }
    .pred-pill {
        background: #0f172a;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ မြန်မာ ဘောလုံးပွဲစဉ်နှင့် AI ခန့်မှန်းချက်များ")
st.caption("တိုက်ရိုက်ရမှတ်များ၊ Win/Draw/Lose, ဂိုးပေါင်း (Over/Under) နှင့် BTTS ခန့်မှန်းချက်များ")

# Sample Match Data
matches = [
    {
        "id": 1, "league": "ပရီးမီးယားလိဂ်", "status": "LIVE 68'",
        "home": "အာဆင်နယ်", "away": "လီဗာပူးလ်",
        "home_score": 2, "away_score": 1,
        "win_prob": 55, "draw_prob": 25, "lose_prob": 20,
        "over_25": 78, "btts": 85,
        "tip": "ဂိုးပေါင်း အပေါ် (Over 2.5) & နှစ်သင်းလုံးဂိုးသွင်းမည် (BTTS - Yes)"
    },
    {
        "id": 2, "league": "ပရီးမီးယားလိဂ်", "status": "LIVE 34'",
        "home": "မန်စီးတီး", "away": "ချဲလ်ဆီး",
        "home_score": 1, "away_score": 0,
        "win_prob": 68, "draw_prob": 20, "lose_prob": 12,
        "over_25": 64, "btts": 58,
        "tip": "မန်စီးတီး နိုင် (Home Win) & Over 2.5"
    },
    {
        "id": 3, "league": "လာလီဂါ", "status": "ယနေ့ ည ၁၁:၃၀",
        "home": "ရီးရဲလ်မက်ဒရစ်", "away": "ဘာစီလိုနာ",
        "home_score": 0, "away_score": 0,
        "win_prob": 45, "draw_prob": 25, "lose_prob": 30,
        "over_25": 82, "btts": 80,
        "tip": "နှစ်သင်းလုံးဂိုးသွင်းမည် (BTTS - Yes) & Over 2.5"
    }
]

# Sidebar Filters
st.sidebar.header("🔍 ပွဲစဉ် စစ်ထုတ်ရန်")
selected_league = st.sidebar.selectbox("လိဂ် ရွေးချယ်ပါ", ["အားလုံး", "ပရီးမီးယားလိဂ်", "လာလီဂါ"])

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 AI ဂိုးတွက်ချက်စက် (Simulator)")
home_xg = st.sidebar.slider("အိမ်ရှင် တိုက်စစ်အား (Expected Goals)", 0.5, 4.0, 1.8, 0.1)
away_xg = st.sidebar.slider("ဧည့်သည် တိုက်စစ်အား (Expected Goals)", 0.5, 4.0, 1.2, 0.1)

total_xg = home_xg + away_xg
sim_over25 = min(95, max(10, int((total_xg / 3.5) * 100)))
sim_btts = min(92, max(15, int(((min(home_xg, away_xg) / 1.8) * 100))))

st.sidebar.info(f"""
**တွက်ချက်မှု ရလဒ် -**
- ခန့်မှန်း ဂိုးပေါင်း: **{total_xg:.1f} ဂိုး**
- Over 2.5 ဖြစ်နိုင်ခြေ: **{sim_over25}%**
- BTTS (နှစ်သင်းလုံးဂိုးသွင်းရန်): **{sim_btts}%**
""")

# Display Matches
for m in matches:
    if selected_league != "အားလုံး" and m["league"] != selected_league:
        continue
        
    badge_class = "live-badge" if "LIVE" in m["status"] else "upcoming-badge"
    
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span style="color:#94a3b8; font-weight:bold;">🏆 {m['league']}</span>
            <span class="{badge_class}">{m['status']}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin: 15px 0;">
            <div style="font-size:20px; font-weight:bold; width:35%; text-align:right;">{m['home']}</div>
            <div class="score-box" style="width:20%;">{m['home_score']} - {m['away_score']}</div>
            <div style="font-size:20px; font-weight:bold; width:35%; text-align:left;">{m['away']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**နိုင်/သရေ/ရှုံး (1X2)**")
        st.progress(m["win_prob"] / 100)
        st.caption(f"အိမ်ရှင် {m['win_prob']}% | သရေ {m['draw_prob']}% | ဧည့်သည် {m['lose_prob']}%")
    with col2:
        st.metric(label="ဂိုးပေါင်း အပေါ်/အောက် (Over 2.5)", value=f"{m['over_25']}%", delta="Over 2.5 အကြံပြု" if m['over_25'] >= 60 else "Under 2.5 အကြံပြု")
    with col3:
        st.metric(label="နှစ်သင်းလုံးဂိုးသွင်းမှု (BTTS)", value=f"{m['btts']}%", delta="BTTS - Yes" if m['btts'] >= 60 else "BTTS - No")
        
    st.success(f"💡 **AI အကြံပြုချက်:** {m['tip']}")
    st.markdown("---")
