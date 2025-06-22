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
    "Special Cup": ["Cloudtop Cruise", "Bone-Dry Dunes", "Bowser's Castle", "Rainbow Road"],
    "Shell Cup": ["Wii Moo Moo Meadows", "GBA Peach Circuit", "Wii Grumble Volcano", "N64 Rainbow Road"],
    "Banana Cup": ["GCN Dry Dry Desert", "SNES Donut Plains 3", "N64 Royal Raceway", "3DS DK Jungle"],
    "Leaf Cup": ["DS Wario Stadium", "GCN Sherbet Land", "3DS Music Park", "N64 Yoshi Valley"],
    "Lightning Cup": ["DS Tick-Tock Clock", "3DS Piranha Plant Slide", "Wii Grumble Volcano", "N64 Rainbow Road"],
    "Egg Cup": ["GCN Yoshi Circuit", "Excitebike Arena", "Dragon Driftway", "Mute City"],
    "Triforce Cup": ["Wii Wario's Gold Mine", "SNES Rainbow Road", "Ice Ice Outpost", "Hyrule Circuit"],
    "Crossing Cup": ["GCN Baby Park", "GBA Cheese Land", "Wild Woods", "Animal Crossing"],
    "Bell Cup": ["3DS Neo Bowser City", "GBA Ribbon Road", "Super Bell Subway", "Big Blue"]
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
    tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "🏆 TIME TRIAL", "⏱️ SUBMIT TIMES"])
    
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
                        medal = ""
                    
                    st.markdown(f"""
                    <div class='f1-ranking-row {row_class}'>
                        <div style='display: flex; align-items: center;'>
                            <span style='font-size: 1.2em; font-weight: bold; margin-right: 20px; min-width: 30px;'>{position}</span>
                            <span style='font-size: 1.1em; margin-right: 10px;'>{medal}</span>
                            <span style='font-size: 1.1em; font-weight: bold;'>{speler.upper()}</span>
                        </div>
                        <div style='font-size: 1.2em; font-weight: bold;'>{points} PTS</div>
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
                                st.markdown(f"""
                                <div class='f1-cup-container'>
                                    <div class='f1-cup-header'>
                                        <div class='f1-cup-image'>
                                """, unsafe_allow_html=True)
                                
                                display_cup_image(cup, width=60)
                                
                                st.markdown(f"""
                                        </div>
                                        <div class='f1-cup-title'>{cup.upper()}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
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
                                            medal = f"{position}."
                                        
                                        st.markdown(f"""
                                        <div class='f1-points-row'>
                                            <span>{position}. {medal} {speler.upper()}</span>
                                            <span>{points} PTS</span>
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
                st.markdown(f"""
                <div class='f1-cup-container' style='margin: 20px 0;'>
                    <div class='f1-cup-header'>
                        <div class='f1-cup-image'>
                """, unsafe_allow_html=True)
                
                display_cup_image(selected_cup, width=80)
                
                st.markdown(f"""
                        </div>
                        <div class='f1-cup-title' style='font-size: 1.5em;'>{selected_cup.upper()}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
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
                                race_image = Image.open(race_image_path).resize((64, 128))
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
                                    medal = f"{rank}."
                                    style_class = ""
                                
                                st.markdown(f"""
                                <div class='f1-ranking-row {style_class}' style='margin: 5px 0; font-size: 0.9em;'>
                                    <div style='display: flex; align-items: center;'>
                                        <span style='margin-right: 15px; min-width: 25px;'>{rank}</span>
                                        <span style='margin-right: 10px;'>{medal}</span>
                                        <span>{row['speler'].upper()}</span>
                                    </div>
                                    <span style='font-family: Monaco, Consolas, monospace;'>{row['tijd']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <p style='color: #7f8c8d; margin: 5px 0 0 0; font-style: italic;'>Geen tijden beschikbaar</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"Nog geen tijden beschikbaar voor {selected_cup}")
        else:
            st.info("Nog geen data beschikbaar. Voeg tijden toe in de 'Tijd Invoeren' tab.")
    
    with tab3:
        st.markdown("<h2 style='color: white; font-family: Monaco, Consolas, monospace;'>SUBMIT YOUR TIME</h2>", unsafe_allow_html=True)
        
        with st.form("time_entry_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                speler = st.text_input("Speler", placeholder="Voer spelernaam in")
                cup = st.selectbox("Cup", list(CUPS_RACES.keys()))
            
            with col2:
                race = st.selectbox("Race", CUPS_RACES[cup] if cup else [])
                tijd = st.text_input("Tijd", placeholder="MM:SS.mmm (bijv. 1:32.456)")
            
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Tijd Opslaan")
            
            if submitted:
                if speler and cup and race and tijd:
                    # Validate time format
                    test_seconds = time_to_seconds(tijd)
                    if test_seconds != float('inf'):
                        if save_time_trial(speler, cup, race, tijd):
                            st.success(f"Tijd opgeslagen: {speler} - {race} - {tijd}")
                            st.rerun()
                        else:
                            st.error("Fout bij opslaan van tijd")
                    else:
                        st.error("Ongeldige tijdformat. Gebruik MM:SS.mmm (bijv. 1:32.456)")
                else:
                    st.error("Vul alle velden in")
        
        # Show recent entries
        if not df.empty:
            st.markdown("<h3 style='color: white; font-family: Monaco, Consolas, monospace;'>RECENT TIMES</h3>", unsafe_allow_html=True)
            recent_df = df.sort_values('timestamp', ascending=False).head(25) if 'timestamp' in df.columns else df.head(10)
            
            display_df = recent_df[['speler', 'cup', 'race', 'tijd']].copy().reset_index(drop=True)
            st.dataframe(display_df, hide_index=True,use_container_width=True)

if __name__ == "__main__":
    main()
