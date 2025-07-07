import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import os
import base64
import requests
import pytz

# Set wide layout and robust background at the very top
st.set_page_config(
    page_title="Mario Kart 8 Deluxe Time Trial Dashboard",
    page_icon="🏁",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    color: white;
    min-height: 100vh;
    background-attachment: fixed;
}
html, body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    min-height: 100vh;
}
.stApp, .stApp * {
    color: white !important;
}

.main {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 5px;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #2c3e50, #34495e);
    border-radius: 8px;
    color: white;
    font-weight: bold;
    border: 1px solid #7f8c8d;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    border: 1px solid #e74c3c;
}

/* F1 Scoreboard styling */
.f1-header {
    background: linear-gradient(90deg, #1a1a2e 0%, #e74c3c 50%, #1a1a2e 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    border: 2px solid #e74c3c;
}

.f1-ranking-row {
    background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 12px 20px;
    margin: 2px 0;
    border-left: 4px solid;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Monaco', 'Consolas', monospace;
    font-weight: bold;
}

.f1-ranking-row.first {
    border-left-color: #f1c40f;
    background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%);
}

.f1-ranking-row.second {
    border-left-color: #95a5a6;
    background: linear-gradient(90deg, #95a5a6 0%, #7f8c8d 100%);
}

.f1-ranking-row.third {
    border-left-color: #cd7f32;
    background: linear-gradient(90deg, #cd7f32 0%, #a0522d 100%);
}

.f1-cup-container {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border: 1px solid #7f8c8d;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.f1-cup-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #7f8c8d;
}

.f1-cup-image {
    margin-right: 15px;
}

.f1-cup-title {
    color: white;
    font-weight: bold;
    font-size: 1.2em;
    font-family: 'Monaco', 'Consolas', monospace;
}

.f1-points-row {
    background: rgba(255,255,255,0.1);
    padding: 8px 12px;
    margin: 3px 0;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    font-family: 'Monaco', 'Consolas', monospace;
}

/* Hide default streamlit styling */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Override streamlit default colors */
.stSelectbox > div > div {
    background-color: #34495e;
    color: white;
}

.stTextInput > div > div > input {
    background-color: #34495e;
    color: white;
    border: 1px solid #7f8c8d;
}

.f1-cup-btn {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    border: 2px solid #e74c3c !important;
    border-radius: 8px !important;
    color: white !important;
    font-family: Monaco, Consolas, monospace !important;
    font-weight: bold !important;
    font-size: 1.3em !important;
    box-shadow: none !important;
    margin-bottom: 8px;
}
.f1-cup-btn:hover {
    filter: brightness(1.1);
    border-color: #f39c12 !important;
}
/* Remove default Streamlit button background */
button[data-testid^="baseButton-cup_"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    border: 2px solid #e74c3c !important;
    border-radius: 8px !important;
    color: white !important;
    font-family: Monaco, Consolas, monospace !important;
    font-weight: bold !important;
    font-size: 1.3em !important;
    box-shadow: none !important;
    margin-bottom: 8px;
}
button[data-testid^="baseButton-cup_"]:hover {
    filter: brightness(1.1);
    border-color: #f39c12 !important;
}
.element-container:has(#button-after) + div button {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    border: 2px solid #e74c3c !important;
    border-radius: 8px !important;
    color: white !important;
    font-family: Monaco, Consolas, monospace !important;
    font-weight: bold !important;
    font-size: 1.3em !important;
    box-shadow: none !important;
    margin-bottom: 8px;
}
.element-container:has(#button-after) + div button:hover {
    filter: brightness(1.1);
    border-color: #f39c12 !important;
}
</style>
""", unsafe_allow_html=True)

# MongoDB connection
@st.cache_resource
def init_connection():
    try:
        client = pymongo.MongoClient(st.secrets["mongo"]["connection_string"])
        return client[st.secrets["mongo"]["database"]]
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Mario Kart 8 Deluxe cups en races
CUPS_RACES = {
    "Mushroom Cup": ["Mario Kart Stadium", "Water Park", "Sweet Sweet Canyon", "Thwomp Ruins"],
    "Flower Cup": ["Mario Circuit", "Toad Harbor", "Twisted Mansion", "Shy Guy Falls"],
    "Star Cup": ["Sunshine Airport", "Dolphin Shoals", "Electrodrome", "Mount Wario"],
    "Special Cup": ["Cloudtop Cruise", "Bone-Dry Dunes", "Bowsers Castle", "Rainbow Road"],
    "Shell Cup": ["Moo Moo Meadows", "GBA Mario Circuit", "Cheep Cheep Beach", "Toads Turnpike"],
    "Banana Cup": ["Dry Dry Desert", "Donut Plains 3", "Royal Raceway", "DK Jungle"],
    "Leaf Cup": ["Wario Stadium", "Sherbet Land", "Music Park", "Yoshi Valley"],
    "Lightning Cup": ["Tick-Tock Clock", "Piranha Plant Slide", "Grumble Volcano", "N64 Rainbow Road"],
    "Egg Cup": ["Yoshi Circuit", "Excitebike Arena", "Dragon Driftway", "Mute City"],
    "Triforce Cup": ["Warios Gold Mine", "SNES Rainbow Road", "Ice Ice Outpost", "Hyrule Circuit"],
    "Crossing Cup": ["Baby Park", "Cheese Land", "Wild Woods", "Animal Crossing"],
    "Bell Cup": ["Neo Bowser City", "Ribbon Road", "Super Bell Subway", "Big Blue"]
}

# Mario Kart 8 Deluxe cups en races
def get_cup_image(cup_name, image_folder="MK_Dash/cup_images"):
    """Return image path for cup visualization"""
    # Define image filenames (you can adjust these to match your actual filenames)
    image_files = {
        "Mushroom Cup": "mushroom_cup.png",
        "Flower Cup": "flower_cup.png", 
        "Star Cup": "star_cup.png",
        "Special Cup": "special_cup.png",
        "Shell Cup": "shell_cup.png",
        "Banana Cup": "banana_cup.png",
        "Leaf Cup": "leaf_cup.png",
        "Lightning Cup": "lightning_cup.png",
        "Egg Cup": "egg_cup.png",
        "Triforce Cup": "triforce_cup.png",
        "Crossing Cup": "crossing_cup.png",
        "Bell Cup": "bell_cup.png"
    }
    
    filename = image_files.get(cup_name)
    if filename:
        image_path = os.path.join(image_folder, filename)
        if os.path.exists(image_path):
            return image_path
    
    # Fallback to emoji if image not found
    cup_emojis = {
        "Mushroom Cup": "🍄",
        "Flower Cup": "🌸",
        "Star Cup": "⭐",
        "Special Cup": "👑",
        "Shell Cup": "🐚",
        "Banana Cup": "🍌",
        "Leaf Cup": "🍃",
        "Lightning Cup": "⚡",
        "Egg Cup": "🥚",
        "Triforce Cup": "🔺",
        "Crossing Cup": "🚦",
        "Bell Cup": "🔔"
    }
    return cup_emojis.get(cup_name, "🏆")

def display_cup_image(cup_name, width=100):
    """Display cup image or emoji fallback"""
    image_path = get_cup_image(cup_name)
    
    if isinstance(image_path, str) and image_path.endswith(('.png', '.jpg', '.jpeg')):
        try:
            image = Image.open(image_path)
            st.image(image, width=width)
        except Exception as e:
            st.error(f"Error loading image {image_path}: {e}")
            st.write(image_path)  # Show emoji fallback
    else:
        # Display emoji with larger font
        st.markdown(f"<div style='font-size: {width//2}px; text-align: center;'>{image_path}</div>", 
                   unsafe_allow_html=True)

def get_race_image(race_name, image_folder="MK_Dash/race_images"):
    """Return image path for race visualization"""
    # Replace spaces and special characters for filename
    filename = race_name.replace(' ', '_').replace("'", "").replace(':', '').replace('/', '_') + ".png"
    image_path = os.path.join(image_folder, filename)
    if os.path.exists(image_path):
        return image_path
    return None

def time_to_seconds(time_str):
    """Convert time string (MM:SS.mmm) to total seconds"""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except:
        return float('inf')

def seconds_to_time(seconds):
    """Convert seconds to MM:SS.mmm format"""
    if seconds == float('inf'):
        return "N/A"
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"
    
def calculate_points(times_df):
    """Calculate points based on ranking system"""
    if times_df.empty:
        return pd.DataFrame()
    
    # Group by race and calculate points
    points_data = []
    
    for race in times_df['race'].unique():
        race_times = times_df[times_df['race'] == race].copy()
        race_times['seconds'] = race_times['tijd'].apply(time_to_seconds)
        race_times = race_times.sort_values('seconds')
        
        # Assign points based on ranking
        for idx, row in race_times.iterrows():
            rank = race_times.index.get_loc(idx) + 1
            if rank == 1:
                points = 3
            elif rank == 2:
                points = 2
            elif rank == 3:
                points = 1
            else:  # 4th place
                points = 1
            
            points_data.append({
                'speler': row['speler'],
                'cup': row['cup'],
                'race': row['race'],
                'tijd': row['tijd'],
                'rank': rank,
                'points': points
            })
    
    return pd.DataFrame(points_data)

def get_cup_from_race(race_name):
    for cup, races in CUPS_RACES.items():
        if race_name in races:
            return cup
    return None
    
def load_data():
    """Load data from MongoDB"""
    db = init_connection()
    if db is None:
        return pd.DataFrame()
    
    try:
        collection = db.time_trials
        data = list(collection.find({}, {'_id': 0}))
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_time_trial(speler, cup, race, tijd):
    """Save time trial to MongoDB"""
    db = init_connection()
    if db is None:
        return False
    
    try:
        collection = db.time_trials
        
        # Check if record already exists
        existing = collection.find_one({
            'speler': speler,
            'cup': cup,
            'race': race
        })
        
        if existing:
            # Update existing record
            collection.update_one(
                {'speler': speler, 'cup': cup, 'race': race},
                {'$set': {'tijd': tijd, 'timestamp': datetime.now()}}
            )
        else:
            # Insert new record
            collection.insert_one({
                'speler': speler,
                'cup': cup,
                'race': race,
                'tijd': tijd,
                'timestamp': datetime.now()
            })
        
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def send_telegram_photo(photo_path, caption):
    bot_token = st.secrets["telegram"]["bot_token"]
    chat_id = st.secrets["telegram"]["chat_id"]
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(photo_path, "rb") as photo_file:
        files = {"photo": photo_file}
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data, files=files, timeout=10)
            response.raise_for_status()
        except Exception as e:
            st.warning(f"Failed to send Telegram photo: {e}")
            if 'response' in locals():
                st.error(f"Telegram response: {response.text}")
    

def main():
    # F1 styled main title
    st.markdown("""
    <div class='f1-header'>
        <h1 style='margin: 0; font-size: 2.5em; font-family: Monaco, Consolas, monospace; letter-spacing: 3px;'>
            🏁 MARIO KART 8 DELUXE 🏁
        </h1>
        <h2 style='margin: 10px 0 0 0; font-size: 1.5em; font-family: Monaco, Consolas, monospace;'>
            TIME TRIAL CHAMPIONSHIP
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 DASHBOARD", "🏆 TIME TRIAL", "📈 PERFORMANCE ANALYSIS", "⏱️ SUBMIT TIMES", "🛠️ DEVELOPER"])
    
    with tab1:
        st.markdown("<h2 style='color: white; font-family: Monaco, Consolas, monospace;'>DRIVER STANDINGS</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            # Calculate points
            points_df = calculate_points(df)
            
            if not points_df.empty:
                # Overall ranking
                overall_ranking = points_df.groupby('speler')['points'].sum().sort_values(ascending=False)
                
                # F1 styled overall ranking header
                st.markdown("""
                <div style='background: linear-gradient(90deg, #1a1a2e 0%, #e74c3c 50%, #1a1a2e 100%); 
                            color: white; padding: 15px; border-radius: 8px; margin: 20px 0;
                            border: 2px solid #e74c3c; text-align: center;'>
                    <h3 style='margin: 0; font-family: Monaco, Consolas, monospace;'>🏆 CHAMPIONSHIP STANDINGS 🏆</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # F1 styled ranking entries
                for i, (speler, points) in enumerate(overall_ranking.items()):
                    position = i + 1
                    
                    if position == 1:
                        row_class = "first"
                        medal = "🏆"
                    elif position == 2:
                        row_class = "second"
                        medal = "🥈"
                    elif position == 3:
                        row_class = "third"
                        medal = "🥉"
                    else:
                        row_class = ""
                        medal = " "
                    
                    st.markdown(f"""
                    <div class='f1-ranking-row {row_class}' style='display: flex; align-items: center;'>
                        <span style='min-width: 2.2em; display: inline-block; text-align: right;'>{position}</span>
                        <span style='min-width: 2em; display: inline-block; text-align: center;'>{medal}</span>
                        <span style='margin-left: 0.5em; font-weight: bold;'>{speler.upper()}</span>
                        <span style='margin-left: auto; font-size: 1.2em; font-weight: bold;'>{points} PTS</span>
                    </div>
                    """, unsafe_allow_html=True)
            
                # Two lines of white space
                st.write(" ")
                st.write(" ")
                
                # Cup rankings with F1 styling
                st.markdown("""
                <div style='background: linear-gradient(90deg, #1a1a2e 0%, #e74c3c 50%, #1a1a2e 100%); 
                            color: white; padding: 15px; border-radius: 8px; margin: 30px 0 20px 0;
                            border: 2px solid #e74c3c; text-align: center;'>
                    <h3 style='margin: 0; font-family: Monaco, Consolas, monospace;'>🏁 CUP STANDINGS 🏁</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Create grid layout for cups
                cups_per_row = 2
                cups = list(CUPS_RACES.keys())
                
                for i in range(0, len(cups), cups_per_row):
                    cols = st.columns(cups_per_row)
                    
                    for j, cup in enumerate(cups[i:i+cups_per_row]):
                        if j < len(cols):
                            with cols[j]:
                                # F1 styled cup container
                                st.markdown(f"<div class='f1-cup-container'>", unsafe_allow_html=True)
                                col_img, col_name = st.columns([1, 9])
                                with col_img:
                                    display_cup_image(cup, width=60)
                                with col_name:
                                    st.markdown(f"<div class='f1-cup-title' style='font-size: 1.3em; font-family: Monaco, Consolas, monospace; color: white; display: flex; align-items: center; height: 60px; margin-left: 0;'>{cup.upper()}</div>", unsafe_allow_html=True)
                                
                                # Get cup-specific ranking
                                cup_points = points_df[points_df['cup'] == cup]
                                if not cup_points.empty:
                                    cup_ranking = cup_points.groupby('speler')['points'].sum().sort_values(ascending=False)
                                    for idx, (speler, points) in enumerate(cup_ranking.items()):
                                        position = idx + 1
                                        if position == 1:
                                            medal = "🏆"
                                        elif position == 2:
                                            medal = "🥈"
                                        elif position == 3:
                                            medal = "🥉"
                                        else:
                                            medal = " "
                                        st.markdown(f"""
                                        <div class='f1-points-row' style='display: flex; align-items: center;'>
                                            <span style='min-width: 2.2em; display: inline-block; text-align: right;'>{position}.</span>
                                            <span style='min-width: 2em; display: inline-block; text-align: center;'>{medal}</span>
                                            <span style='margin-left: 0.5em; font-weight: bold;'>{speler.upper()}</span>
                                            <span style='margin-left: auto;'>{points} PTS</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div style='color: #7f8c8d; font-style: italic; text-align: center; padding: 10px;'>
                                        No data available
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nog geen data beschikbaar. Voeg tijden toe in de 'Tijd Invoeren' tab.")
    
    with tab2:
        st.markdown("<h2 style='color: white; font-family: Monaco, Consolas, monospace;'>SELECT A CUP</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            # Add this once before the cup grid (before the for loop):
            st.markdown("""
            <style>
                .f1-cup-btn {
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
                    border: 2px solid #e74c3c !important;
                    border-radius: 8px !important;
                    color: white !important;
                    font-family: Monaco, Consolas, monospace !important;
                    font-weight: bold !important;
                    font-size: 1.3em !important;
                    box-shadow: none !important;
                    margin-bottom: 8px;
                }
                .f1-cup-btn:hover {
                    filter: brightness(1.1);
                    border-color: #f39c12 !important;
                }
                /* Remove default Streamlit button background */
                button[data-testid^="baseButton-cup_"] {
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
                    border: 2px solid #e74c3c !important;
                    border-radius: 8px !important;
                    color: white !important;
                    font-family: Monaco, Consolas, monospace !important;
                    font-weight: bold !important;
                    font-size: 1.3em !important;
                    box-shadow: none !important;
                    margin-bottom: 8px;
                }
                button[data-testid^="baseButton-cup_"]:hover {
                    filter: brightness(1.1);
                    border-color: #f39c12 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Create clickable cup grid
            cups_per_row = 4
            cups = list(CUPS_RACES.keys())
            
            selected_cup = st.session_state.get('selected_cup', None)
            
            for i in range(0, len(cups), cups_per_row):
                cols = st.columns(cups_per_row)
                
                for j, cup in enumerate(cups[i:i+cups_per_row]):
                    if j < len(cols):
                        with cols[j]:
                            # Create clickable cup button with image
                            image_path = get_cup_image(cup)
                            col_img, col_name = st.columns([1, 2])
                            with col_img:
                                if isinstance(image_path, str) and image_path.endswith(('.png', '.jpg', '.jpeg')):
                                    try:
                                        image = Image.open(image_path)
                                        st.image(image, width=60, use_container_width=False)
                                    except:
                                        st.markdown(f"<div style='font-size: 48px; text-align: center;'>{get_cup_image(cup)}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div style='font-size: 48px; text-align: center;'>{image_path}</div>", unsafe_allow_html=True)
                            with col_name:
                                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                                if st.button(f"{cup.upper()}", key=f"cup_{cup}", use_container_width=True):
                                    st.session_state.selected_cup = cup
                                    selected_cup = cup
            
            # Show selected cup details
            if selected_cup:
                # Display selected cup with F1 styling
                st.markdown(f"<div class='f1-cup-container' style='margin: 20px 0;'>", unsafe_allow_html=True)
                col_img, col_name = st.columns([1, 10])
                with col_img:
                    display_cup_image(selected_cup, width=80)
                with col_name:
                    st.markdown(f"<div class='f1-cup-title' style='font-size: 1.5em; font-family: Monaco, Consolas, monospace; color: white; display: flex; align-items: center; height: 80px; margin-left: 0;'>{selected_cup.upper()}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                cup_data = df[df['cup'] == selected_cup]
                
                if not cup_data.empty:
                    # Show race results
                    races = CUPS_RACES[selected_cup]
                    
                    for race in races:
                        race_data = cup_data[cup_data['race'] == race]
                        # Prepare race image or emoji for inline display
                        race_image_path = get_race_image(race)
                        if race_image_path:
                            try:
                                race_image = Image.open(race_image_path).resize((64, 96))
                                img_base64 = image_to_base64(race_image)
                                race_img_html = f"<img src='data:image/png;base64,{img_base64}' style='height:50px;width:50px;vertical-align:middle;margin-right:10px;'/>"
                            except Exception as e:
                                race_img_html = "🏎️ "
                        else:
                            race_img_html = "🏎️ "
                        # Always show the race image and name
                        st.markdown(f"""
                        <div style='background: rgba(255,255,255,0.1); padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e74c3c;'>
                            <h4 style='color: white; margin: 0 0 10px 0; font-family: Monaco, Consolas, monospace;'>
                                {race_img_html}{race.upper()}
                            </h4>
                        """, unsafe_allow_html=True)
                        if not race_data.empty:
                            # Sort by time
                            race_data = race_data.copy()
                            race_data['seconds'] = race_data['tijd'].apply(time_to_seconds)
                            race_data = race_data.sort_values('seconds')
                            # Display results in F1 style
                            for idx, (_, row) in enumerate(race_data.iterrows()):
                                rank = idx + 1
                                if rank == 1:
                                    medal = "🏆"
                                    style_class = "first"
                                elif rank == 2:
                                    medal = "🥈"
                                    style_class = "second"
                                elif rank == 3:
                                    medal = "🥉"
                                    style_class = "third"
                                else:
                                    medal = " "
                                    style_class = ""
                                st.markdown(f"""
                                <div class='f1-ranking-row {style_class}' style='margin: 5px 0; font-size: 0.9em; display: flex; align-items: center;'>
                                    <span style='min-width: 2.2em; display: inline-block; text-align: right;'>{rank}</span>
                                    <span style='min-width: 2em; display: inline-block; text-align: center;'>{medal}</span>
                                    <span style='margin-left: 0.5em; font-weight: bold;'>{row['speler'].upper()}</span>
                                    <span style='margin-left: auto; font-family: Monaco, Consolas, monospace;'>{row['tijd']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <p style='color: #7f8c8d; margin: 5px 0 0 0; font-style: italic;'>No times available</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"Nog geen tijden beschikbaar voor {selected_cup}")
        else:
            st.info("Nog geen data beschikbaar. Voeg tijden toe in de 'Tijd Invoeren' tab.")
    
    with tab3:
        st.markdown("<h2 style='color: white; font-family: Monaco, Consolas, monospace;'>PERFORMANCE ANALYSIS</h2>", unsafe_allow_html=True)
        # Player selection
        all_players = sorted(df['speler'].unique()) if not df.empty else []
        selected_player = st.selectbox("Select Player", all_players, key="perf_player")
        if selected_player:
            player_df = df[df['speler'] == selected_player].copy()
            # Calculate points and placements
            points_df = calculate_points(df)
            player_points = points_df[points_df['speler'] == selected_player]
            total_points = player_points['points'].sum()
            num_races = len(player_df)
            total_races = len(df['race'].unique()) if not df.empty else 0
            # Placement distribution
            place_counts = player_points['rank'].value_counts().sort_index()
            pie_labels = ['1st', '2nd', '3rd', '4th+']
            pie_values = [place_counts.get(1,0), place_counts.get(2,0), place_counts.get(3,0), place_counts.sum() - sum([place_counts.get(i,0) for i in [1,2,3]])]
            # Extended stats
            avg_placement = player_points['rank'].mean() if not player_points.empty else None
            podiums = sum([place_counts.get(i,0) for i in [1,2,3]])
            podium_pct = (podiums / num_races * 100) if num_races > 0 else 0
            # Best track (highest placement, then margin logic)
            best_track = None
            best_rows = []
            if not player_df.empty:
                for _, row in player_df.iterrows():
                    race = row['race']
                    tijd = row['tijd']
                    race_times = df[df['race'] == race].copy()
                    race_times['seconds'] = race_times['tijd'].apply(time_to_seconds)
                    race_times = race_times.sort_values('seconds').reset_index(drop=True)
                    placement = race_times[(race_times['speler'] == selected_player) & (race_times['tijd'] == tijd)]
                    if not placement.empty:
                        pos = placement.index[0] + 1
                        player_time = time_to_seconds(tijd)
                        fastest_time = race_times.iloc[0]['seconds'] if not race_times.empty else None
                        margin_to_fastest = player_time - fastest_time if fastest_time is not None else None
                        # Margin to 2nd place (if player is 1st)
                        if pos == 1 and len(race_times) > 1:
                            second_time = race_times.iloc[1]['seconds']
                            margin_to_2nd = second_time - player_time
                        else:
                            margin_to_2nd = None
                        best_rows.append({
                            'race': race,
                            'placement': pos,
                            'margin_to_2nd': margin_to_2nd,
                            'margin_to_fastest': margin_to_fastest
                        })
                # Find best placement (lowest number)
                if best_rows:
                    min_place = min(r['placement'] for r in best_rows)
                    best_place_rows = [r for r in best_rows if r['placement'] == min_place]
                    if min_place == 1:
                        # Pick the one with the biggest margin to 2nd
                        best_place_rows = [r for r in best_place_rows if r['margin_to_2nd'] is not None]
                        if best_place_rows:
                            best_track = max(best_place_rows, key=lambda r: r['margin_to_2nd'])['race']
                        else:
                            best_track = best_rows[0]['race']
                    else:
                        # Pick the one with the smallest margin to fastest
                        best_track = min(best_place_rows, key=lambda r: r['margin_to_fastest'] if r['margin_to_fastest'] is not None else float('inf'))['race']
            avg_placement_str = f"{avg_placement:.2f}" if avg_placement is not None else "N/A"
            # Player's overall rank by total points
            overall_ranking = points_df.groupby('speler')['points'].sum().sort_values(ascending=False)
            player_rank = None
            for idx, (speler, _) in enumerate(overall_ranking.items()):
                if speler == selected_player:
                    player_rank = idx + 1
                    break
            # Best Cup logic
            best_cup = None
            best_cup_points = None
            best_cup_placements = None
            if not player_points.empty:
                cup_points = player_points.groupby('cup')['points'].sum()
                max_points = cup_points.max()
                best_cups = cup_points[cup_points == max_points].index.tolist()
                if len(best_cups) == 1:
                    best_cup = best_cups[0]
                else:
                    # Tie: check for most higher placements
                    cup_placement_counts = {}
                    for cup in best_cups:
                        cup_races = player_points[player_points['cup'] == cup]
                        # Count 1st, 2nd, 3rd, 4th+ placements
                        counts = [sum(cup_races['rank'] == i) for i in [1,2,3,4]]
                        cup_placement_counts[cup] = counts
                    # Sort by most 1st, then 2nd, then 3rd, then 4th+
                    sorted_cups = sorted(best_cups, key=lambda c: (-cup_placement_counts[c][0], -cup_placement_counts[c][1], -cup_placement_counts[c][2], -cup_placement_counts[c][3]))
                    # Check for ties after sorting
                    top_counts = cup_placement_counts[sorted_cups[0]]
                    tied = [c for c in sorted_cups if cup_placement_counts[c] == top_counts]
                    if len(tied) == 1:
                        best_cup = tied[0]
                    else:
                        best_cup = ', '.join(tied)
            # Layout: left = stats, right = pie chart
            col_stats, col_pie = st.columns([2,2])
            with col_stats:
                st.markdown(f"""
                <div class='f1-message-box' style='background: linear-gradient(135deg, #232526 0%, #414345 100%); border: 3px solid #f1c40f; box-shadow: 0 4px 16px #000a; font-size: 1.1em;'>
                    <b style='font-size:1.3em;letter-spacing:2px;'>{selected_player.upper()}</b><br>
                    <span style='color:#7f8c8d;font-size:1.1em;'>🏅 Rank:</span> <b style='color:#f1c40f'>{player_rank if player_rank else '-'}</b><br>
                    <span style='color:#f1c40f;font-size:1.1em;'>🏆 Total Points:</span> <b style='color:#f1c40f'>{total_points}</b><br>
                    <span style='color:#e74c3c;font-size:1.1em;'>🏁 Races Submitted:</span> <b style='color:#f1c40f'>{num_races} / {total_races}</b><br>
                    <span style='color:#f39c12;font-size:1.1em;'>📊 Avg. Placement:</span> <b style='color:#f1c40f'>{avg_placement_str}</b><br>
                    <span style='color:#16a085;font-size:1.1em;'>🥇 Podium:</span> <b style='color:#f1c40f'>{podium_pct:.1f}%</b><br>
                    <span style='color:#8e44ad;font-size:1.1em;'>🏆 Best Cup:</span> <b style='color:#f1c40f'>{best_cup.upper() if best_cup else 'N/A'}</b><br>
                    <span style='color:#2980b9;font-size:1.1em;'>🚦 Best Track:</span> <b style='color:#f1c40f'>{best_track.upper() if best_track else 'N/A'}</b>
                </div>
                """, unsafe_allow_html=True)
            with col_pie:
                pie_colors = ['#f1c40f', '#95a5a6', '#cd7f32', '#34495e']
                fig = go.Figure(data=[go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    marker=dict(colors=pie_colors, line=dict(color='#232526', width=2)),
                    textinfo='label+percent',
                    hole=0.35,
                    pull=[0.06,0.03,0,0],
                    direction='clockwise',
                    rotation=45,
                    sort=False
                )])
                fig.update_traces(
                    textfont_size=18,
                    textfont_color='white',
                    textposition='inside',
                    showlegend=False,
                    opacity=0.98,
                    marker=dict(line=dict(color='#232526', width=2)),
                    sort=False
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='rgba(20,20,30,1)',
                    plot_bgcolor='rgba(20,20,30,1)',
                    font=dict(family='Monaco, Consolas, monospace', color='white', size=16),
                    height=340
                )
                st.plotly_chart(fig, use_container_width=True)
            # --- Worst performing tracks ---
            st.markdown("<h3 style='color: #e74c3c; font-family: Monaco, Consolas, monospace; margin-top: 2em;'>Worst Performing Tracks</h3>", unsafe_allow_html=True)
            # For each race, get placement and time diff to fastest
            worst_rows = []
            for _, row in player_df.iterrows():
                race = row['race']
                cup = row['cup']
                tijd = row['tijd']
                # Get all times for this race
                race_times = df[df['race'] == race].copy()
                race_times['seconds'] = race_times['tijd'].apply(time_to_seconds)
                race_times = race_times.sort_values('seconds')
                # Placement
                placement = race_times.reset_index(drop=True)
                placement = placement[(placement['speler'] == selected_player) & (placement['tijd'] == tijd)]
                if not placement.empty:
                    pos = placement.index[0] + 1
                else:
                    pos = None
                # Time diff to fastest
                best_time = race_times.iloc[0]['seconds'] if not race_times.empty else None
                player_time = time_to_seconds(tijd)
                time_diff = player_time - best_time if best_time is not None else None
                worst_rows.append({
                    'race': race,
                    'cup': cup,
                    'tijd': tijd,
                    'placement': pos,
                    'time_diff': time_diff
                })
            # Sort: biggest time diff first, then worst placement
            worst_rows = [r for r in worst_rows if r['placement'] is not None and r['time_diff'] is not None]
            worst_rows = sorted(worst_rows, key=lambda x: (-x['placement'], -x['time_diff']))
            # Show top 20 worst tracks
            for wr in worst_rows[:20]:
                race_img_path = get_race_image(wr['race'])
                if race_img_path:
                    try:
                        race_image = Image.open(race_img_path).resize((64, 96))
                        img_base64 = image_to_base64(race_image)
                        race_img_html = f"<img src='data:image/png;base64,{img_base64}' style='height:50px;width:50px;vertical-align:middle;margin-right:10px;'/>"
                    except Exception as e:
                        race_img_html = "🏎️ "
                else:
                    race_img_html = "🏎️ "
                time_diff_str = f"+{wr['time_diff']:.3f}s" if wr['time_diff'] is not None else "N/A"
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #232526 0%, #414345 100%); padding: 18px; margin: 16px 0; border-radius: 12px; border-left: 6px solid #e74c3c; box-shadow: 0 6px 24px #000b; position:relative;'>
                    <h4 style='color: #f1c40f; margin: 0 0 12px 0; font-family: Monaco, Consolas, monospace; letter-spacing:1px;'>
                        {race_img_html}{wr['race'].upper()}
                    </h4>
                    <div style='display: flex; align-items: center; font-family: Monaco, Consolas, monospace; font-size:1.1em;'>
                        <span style='min-width: 2.2em; display: inline-block; text-align: right; color:#e74c3c; font-weight:bold;'>Place: {wr['placement']}</span>
                        <span style='margin-left: 1.5em;'>Your time: <b style='color:#f1c40f'>{wr['tijd']}</b></span>
                        <span style='margin-left: 1.5em; font-size:1.15em;'><b style='color:#e74c3c; background: #fff2; padding: 2px 10px; border-radius: 8px; box-shadow:0 2px 8px #e74c3c55;'>{time_diff_str}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    
    with tab4:
        st.markdown("<h2 style='color: white; font-family: Monaco, Consolas, monospace;'>SUBMIT YOUR TIME</h2>", unsafe_allow_html=True)

        all_races = []
        for races in CUPS_RACES.values():
            all_races.extend(races)

        with st.form("time_entry_form"):
            speler = st.text_input("Player", placeholder="Voer spelernaam in")
            race = st.selectbox("Race", sorted(all_races))  # Gesorteerd voor betere UX
            tijd = st.text_input("Time", placeholder="MM:SS.mmm (bijv. 1:32.456)")
        
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Submit Time")
        
        if submitted:
            cup = get_cup_from_race(race)
            if speler and cup and race and tijd:
                # Validate time format
                test_seconds = time_to_seconds(tijd)
                if test_seconds != float('inf') and tijd[1] == ':' and tijd[4] == '.':
                    if save_time_trial(speler.strip(), cup, race, tijd):
                        # Format the message as on the page, using Amsterdam time
                        amsterdam_tz = pytz.timezone('Europe/Amsterdam')
                        now = datetime.now(amsterdam_tz).strftime('%d %B %Y %H:%M')

                        # --- Calculate new position for this time on this track ---
                        # Reload data to get the latest
                        df = load_data()
                        race_df = df[(df['cup'] == cup) & (df['race'] == race)].copy()
                        race_df['seconds'] = race_df['tijd'].apply(time_to_seconds)
                        race_df = race_df.sort_values('seconds')
                        # Find the position (1-based) of this speler's time
                        #position = race_df.reset_index(drop=True)
                        position = race_df[(race_df['speler'].str.strip().str.lower() == speler.strip().lower()) &
                                            (race_df['cup'] == cup) & (race_df['race'] == race)]
                        
                        if not position.empty:
                            pos = position.index[0] + 1
                            total = len(race_df)
                            if pos == 1:
                                pos_text = f"This is now the <b>fastest</b> time on this track! (P1/{total})"
                            elif pos == 2:
                                pos_text = f"This is now the <b>2nd fastest</b> time on this track! (P2/{total})"
                            elif pos == 3:
                                pos_text = f"This is now the <b>3rd fastest</b> time on this track! (P3/{total})"
                            else:
                                pos_text = f"This is now the <b>{pos}th fastest</b> time on this track! (P{pos}/{total})"
                        else:
                            pos_text = ""
                        # --- End position calculation ---

                        message = (
                                f"<em>{speler}</em> submitted a new time at <em>{cup}</em> - <em>{race}</em> "
                                f"and set a time of <em>{tijd}</em>.\n\n"
                                f"{pos_text}\n"
                                f"<i>{now}</i>"
                            )
                        race_image_path = get_race_image(race)
                        if race_image_path:
                            send_telegram_photo(race_image_path, message)
                        st.success(f"Tijd opgeslagen: {speler} - {race} - {tijd}")
                        st.rerun()
                    else:
                        st.error("Fout bij opslaan van tijd")
                else:
                    st.error("Ongeldige tijdformat. Gebruik MM:SS.mmm (bijv. 1:32.456)")
            else:
                st.error("Vul alle velden in")
        
        # Show recent entries as F1-styled message boxes
        if not df.empty:
            st.markdown("""
            <style>
            .f1-message-box {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                border: 2px solid #e74c3c;
                border-radius: 10px;
                color: white;
                font-family: Monaco, Consolas, monospace;
                font-weight: bold;
                box-shadow: 0 2px 8px rgba(0,0,0,0.25);
                margin-bottom: 18px;
                padding: 18px 22px 10px 22px;
                position: relative;
            }
            .f1-message-date {
                color: #f1c40f;
                font-size: 0.95em;
                font-weight: normal;
                font-family: Monaco, Consolas, monospace;
                position: absolute;
                bottom: 8px;
                right: 22px;
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown("<h3 style='color: white; font-family: Monaco, Consolas, monospace;'>RECENT TIMES</h3>", unsafe_allow_html=True)
            # Sort and display the 10 most recent submissions
            if 'timestamp' in df.columns:
                recent_df = df.sort_values('timestamp', ascending=False).head(10)
            else:
                recent_df = df.head(25)
            for _, row in recent_df.iterrows():
                speler = row['speler']
                cup = row['cup']
                race = row['race']
                tijd = row['tijd']
                # Format date
                if 'timestamp' in row and pd.notnull(row['timestamp']):
                    if isinstance(row['timestamp'], str):
                        try:
                            dt = pd.to_datetime(row['timestamp'])
                        except:
                            dt = None
                    else:
                        dt = row['timestamp']
                    if dt is not None:
                        date_str = dt.strftime('%d %B %Y %H:%M')
                    else:
                        date_str = ''
                else:
                    date_str = ''
                st.markdown(f"""
                <div class="f1-message-box">
                    <em>{speler}</em> submitted a new time at <em>{cup}</em> - <em>{race}</em> and set a time of <em style='color:#f1c40f'>{tijd}</em>.
                    <div class="f1-message-date">{date_str}</div>
                </div>
                """, unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='color: #e74c3c; font-family: Monaco, Consolas, monospace;'>Developer Environment</h2>", unsafe_allow_html=True)
        try:
            dev_password = st.secrets["developer"]["dev_password"]
        except KeyError:
            st.error("No developer password set in Streamlit secrets! Please add 'dev_password' to your secrets.")
            st.stop()
        if 'dev_env_authenticated' not in st.session_state:
            st.session_state['dev_env_authenticated'] = False
        if not st.session_state['dev_env_authenticated']:
            pw = st.text_input("Enter developer password", type="password")

            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            login_clicked = st.button("Login", key="dev_login_btn")
            # Patch the button class for theming
            st.markdown("""
            <script>
            const btn = window.parent.document.querySelector('button[data-testid="baseButton-dev_login_btn"]');
            if (btn) btn.classList.add('dev-login-btn');
            </script>
            """, unsafe_allow_html=True)
            if login_clicked:
                if pw == dev_password:
                    st.session_state['dev_env_authenticated'] = True
                    st.success("Access granted.")
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            st.stop()
        # Authenticated: show options
        st.markdown("<h3 style='color: #f1c40f;'>Select Action</h3>", unsafe_allow_html=True)
        action = st.radio("What do you want to do?", ["Update a record", "Delete a record"], horizontal=True)
        # Get all unique players, cups, races
        all_players = sorted(df['speler'].unique()) if not df.empty else []
        player = st.selectbox("Select Player", all_players, key="dev_player")
        cups = sorted(df[df['speler'] == player]['cup'].unique()) if player else []
        cup = st.selectbox("Select Cup", cups, key="dev_cup")
        races = sorted(df[(df['speler'] == player) & (df['cup'] == cup)]['race'].unique()) if player and cup else []
        race = st.selectbox("Select Race", races, key="dev_race")
        record = df[(df['speler'] == player) & (df['cup'] == cup) & (df['race'] == race)]
        if not record.empty:
            tijd = record.iloc[0]['tijd']
            st.markdown(f"<b>Current Time:</b> <span style='color:#f1c40f;font-size:1.2em'>{tijd}</span>", unsafe_allow_html=True)
            if action == "Update a record":
                new_time = st.text_input("Enter new time (MM:SS.mmm)", value=tijd, key="dev_new_time")
                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                if st.button("Update Time"):
                    db = init_connection()
                    if db is not None:
                        collection = db.time_trials
                        result = collection.update_one({'speler': player, 'cup': cup, 'race': race}, {'$set': {'tijd': new_time, 'timestamp': datetime.now()}})
                        if result.modified_count > 0:
                            st.success("Time updated successfully.")
                            st.rerun()
                        else:
                            st.warning("No changes made or update failed.")
            elif action == "Delete a record":
                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                if st.button("Delete Record", type="primary"):
                    db = init_connection()
                    if db is not None:
                        collection = db.time_trials
                        result = collection.delete_one({'speler': player, 'cup': cup, 'race': race})
                        if result.deleted_count > 0:
                            st.success("Record deleted successfully.")
                            st.rerun()
                        else:
                            st.warning("Delete failed.")
        else:
            st.info("No record found for this selection.")
                
if __name__ == "__main__":
    main()
