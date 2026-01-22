import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 你家住哪裡？", 
    page_icon="🏠", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (森林部落風格 🌲) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Fredoka:wght@600&display=swap');

    /* 全局背景：清新的森林淺綠背景 */
    .stApp { 
        background-color: #E8F5E9; /* 淺綠 */
        background-image: radial-gradient(#A5D6A7 2px, transparent 2px);
        background-size: 30px 30px;
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* --- 1. 頂部 Hero 區塊 --- */
    .header-container {
        background: white;
        border-radius: 30px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 8px 0px #388E3C; /* 深綠陰影 */
        border: 4px solid #1B5E20; /* 森林綠邊框 */
        margin-bottom: 30px;
        position: relative;
    }
    
    .main-title {
        font-family: 'Fredoka', sans-serif;
        color: #1B5E20;
        font-size: 32px; /* 字數較多稍微縮小 */
        margin: 0;
        line-height: 1.3;
        font-weight: 900;
    }
    
    .sub-title {
        color: #5D4037; /* 大地色 */
        font-size: 20px;
        font-weight: 700;
        margin-top: 5px;
    }
    
    .teacher-tag {
        display: inline-block;
        background: #66BB6A;
        color: white;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: bold;
        margin-top: 15px;
        box-shadow: 0 4px 0 #2E7D32;
        font-size: 14px;
    }

    /* --- 2. 單字卡片 --- */
    .word-card {
        background: white;
        border-radius: 25px;
        padding: 15px 10px;
        text-align: center;
        border: 3px solid #FFF;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        height: 100%;
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
    }
    
    .word-card:hover {
        transform: translateY(-5px) scale(1.02);
        border-color: #81C784;
    }
    
    /* 卡片頂部顏色條 (草綠色) */
    .card-top {
        height: 8px;
        width: 100%;
        background: #81C784;
        position: absolute;
        top: 0; left: 0;
    }

    .icon-box {
        font-size: 45px;
        margin-bottom: 5px;
        filter: drop-shadow(0 4px 4px rgba(0,0,0,0.1));
    }
    
    .amis-word {
        font-size: 18px;
        font-weight: 900;
        color: #1B5E20;
        margin-bottom: 2px;
    }
    
    .zh-word {
        font-size: 14px;
        color: #5D4037;
        font-weight: 500;
    }

    /* --- 3. 對話框設計 --- */
    .chat-box {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 8px solid #66BB6A;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
    }
    
    .chat-icon {
        font-size: 30px;
        margin-right: 15px;
        min-width: 40px;
        text-align: center;
    }
    
    .chat-content { flex-grow: 1; }
    
    .chat-amis {
        font-size: 18px;
        font-weight: 700;
        color: #2E7D32;
    }
    
    .chat-zh {
        font-size: 15px;
        color: #795548;
    }

    /* --- 4. 按鈕與 Tab --- */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(to bottom, #66BB6A 0%, #43A047 100%);
        color: white !important;
        font-weight: 900;
        border: none;
        box-shadow: 0 5px 0 #2E7D32;
        padding: 10px 0;
        margin-top: 5px;
    }
    .stButton>button:active {
        box-shadow: none;
        transform: translateY(5px);
    }

    /* Tab 樣式 */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.8);
        border-radius: 50px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px;
        font-weight: bold;
        color: #5D4037 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* 測驗區 */
    .quiz-card {
        background: white;
        padding: 30px;
        border-radius: 30px;
        text-align: center;
        border: 4px dashed #81C784;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料與圖示設定 ---

VOCABULARY = [
    {"amis": "cuwa",        "zh": "哪裡",           "emoji": "🗺️", "file": "v_cuwa"},
    {"amis": "luma’",       "zh": "家",             "emoji": "🏠", "file": "v_luma"},
    {"amis": "misu",        "zh": "你(的)",         "emoji": "🫵", "file": "v_misu"},
    {"amis": "niyaru’",     "zh": "村莊/部落",       "emoji": "🏞️", "file": "v_niyaru"},
    {"amis": "pina",        "zh": "多少",           "emoji": "🔢", "file": "v_pina"},
    {"amis": "pina tu",     "zh": "多少了",         "emoji": "📊", "file": "v_pinatu"},
    {"amis": "remiad",      "zh": "天",             "emoji": "☀️", "file": "v_remiad"},
    {"amis": "namilipayan", "zh": "做完禮拜後(週)",  "emoji": "⛪", "file": "v_namilipayan"},
    {"amis": "anini",       "zh": "現在/今天",       "emoji": "👇", "file": "v_anini"},
    {"amis": "kukay",       "zh": "謝謝",           "emoji": "🙏", "file": "v_kukay"},
    {"amis": "uli haw",     "zh": "再見",           "emoji": "👋", "file": "v_ulihaw"},
    {"amis": "naunen",      "zh": "小心/慢慢地",     "emoji": "🐢", "file": "v_naunen"},
]

SENTENCES = [
    {"amis": "I cuwa ku luma’ nu misu?", "zh": "你家住哪裡？", "emoji": "🏡", "file": "s_icuwa_luma"},
    {"amis": "I cuwa ku niyaru’ nu misu?", "zh": "你的部落在哪兒？", "emoji": "⛰️", "file": "s_icuwa_niyaru"},
    {"amis": "Pina tu ku remiad namilipayan anini?", "zh": "今天星期幾了？", "emoji": "🗓️", "file": "s_pina_remiad"},
    {"amis": "Aray kukay!", "zh": "謝謝！", "emoji": "💖", "file": "s_aray_kukay"},
    {"amis": "Uli haw! Naunen!", "zh": "再見！小心!", "emoji": "🚶", "file": "s_ulihaw_naunen"},
]

QUIZ_DATA = [
    {"q": "I ______ ku luma’ nu misu?", "zh": "你家住哪裡？", "ans": "cuwa", "opts": ["cuwa", "pina", "anini"]},
    {"q": "I cuwa ku ______ nu misu?", "zh": "你的部落在哪兒？", "ans": "niyaru’", "opts": ["niyaru’", "luma’", "remiad"]},
    {"q": "______ tu ku remiad namilipayan anini?", "zh": "今天星期幾了？", "ans": "Pina", "opts": ["Pina", "Cuwa", "Maan"]},
    {"q": "Aray ______!", "zh": "謝謝！", "ans": "kukay", "opts": ["kukay", "uli haw", "naunen"]},
    {"q": "Uli haw! ______!", "zh": "再見！小心!", "ans": "Naunen", "opts": ["Naunen", "Kukay", "Kapah"]},
]

# --- 1.5 語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        for ext in ['mp3', 'm4a']:
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                st.audio(path, format=f'audio/{ext}')
                return
    try:
        tts = gTTS(text=text, lang='id') 
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 隨機出題邏輯 (含防呆) ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2
    q2_data = random.choice(QUIZ_DATA)
    random.shuffle(q2_data['opts'])
    st.session_state.q2_data = q2_data

    # Q3
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

# 檢查數據是否過期 (防呆機制：如果讀不到 emoji 就重置)
if 'q1_data' in st.session_state:
    try:
        _ = st.session_state.q1_data['target']['emoji']
    except KeyError:
        init_quiz() 

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面呈現 ---

def show_learning_mode():
    st.markdown("<h3 style='color:#1B5E20; text-align:center; margin-bottom:20px;'>🌲 部落單字卡</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            # 安全讀取 emoji
            emoji_icon = item.get('emoji', '🌟')
                
            st.markdown(f"""
            <div class="word-card">
                <div class="card-top"></div>
                <div class="icon-box">{emoji_icon}</div>
                <div class="amis-word">{item['amis']}</div>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            st.write("") 
    
    st.markdown("---")
    st.markdown("<h3 style='color:#1B5E20; text-align:center; margin-bottom:20px;'>💬 部落對話</h3>", unsafe_allow_html=True)
    
    for s in SENTENCES:
        emoji_icon = s.get('emoji', '💬')
        st.markdown(f"""
        <div class="chat-box">
            <div class="chat-icon">{emoji_icon}</div>
            <div class="chat-content">
                <div class="chat-amis">{s['amis']}</div>
                <div class="chat-zh">{s['zh']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #2E7D32;'>🏹 狩獵挑戰</h3>", unsafe_allow_html=True)
    st.progress(st.session_state.current_q / 3)
    st.write("")

    # Q1
    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        
        st.markdown(f"""
        <div class="quiz-card">
            <div style="font-size:60px;">🔊</div>
            <h3>請聽語音，選出正確圖案</h3>
        </div>
        """, unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        
        st.write("")
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                emoji_icon = opt.get('emoji', '❓')
                if st.button(f"{emoji_icon} {opt['zh']}", key=f"q1_{idx}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("答對了！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("再試一次！")

    # Q2
    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown(f"""
        <div class="quiz-card">
            <div style="font-size:60px;">🧩</div>
            <h3>句子填空</h3>
            <h2 style="color:#2E7D32; background:#E8F5E9; padding:10px; border-radius:10px;">
                {data['q'].replace('______', '❓')}
            </h2>
            <p>{data['zh']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        ans = st.radio("請選擇缺少的字：", data['opts'])
        if st.button("送出答案"):
            if ans == data['ans']:
                st.balloons()
                st.success("太棒了！")
                time.sleep(1)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("加油！再想一下！")

    # Q3
    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown(f"""
        <div class="quiz-card">
            <div style="font-size:60px;">🎧</div>
            <h3>這句話是什麼意思？</h3>
        </div>
        """, unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("恭喜通關！🎉")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("再聽一次看看！")

    # 結算
    else:
        st.markdown(f"""
        <div class="quiz-card" style="border-color:#66BB6A;">
            <h1 style='color: #2E7D32;'>🎉 挑戰成功！</h1>
            <p>你已經學會詢問地點了！</p>
            <div style='font-size: 80px; margin: 20px 0;'>🏡</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 再玩一次"):
            init_quiz()
            st.rerun()

# --- 4. 主程式 ---
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <div style="font-size: 80px; margin-bottom: 10px;">🏠</div>
        <h1 class="main-title">I cuwa ku luma’ nu misu?</h1>
        <div class="sub-title">你家住哪裡？</div>
        <div class="teacher-tag">
            講師：胡美芳 &nbsp;|&nbsp; 教材提供者：胡美芳
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模式", "🎮 測驗挑戰"])
    
    with tab1:
        show_learning_mode()
    
    with tab2:
        show_quiz_mode()

if __name__ == "__main__":
    main()
