import praw
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import os
import re
from typing import Dict, List

# --- Streamlit Config ---
st.set_page_config(page_title="Reddit Persona Analyzer", layout="wide", page_icon="🔍")
st.title("🔍 Reddit User Persona Analyzer")
st.caption("Generate comprehensive personality profiles from Reddit activity")

# --- Initialize PRAW ---
@st.cache_resource
def init_reddit():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID", "-55gDGuRGc17g8dGjaY2iw"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET", "6Y5L4uBjdTqSb8Evb5bxCTLE5erpAg"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "PersonaGenerator/1.0 by pamarthi_lavanya")
    )

reddit = init_reddit()

# --- Analysis Functions ---
def clean_text(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text.lower())

def analyze_writing_style(texts: List[str]) -> Dict:
    if not texts:
        return {"Description": "No text available"}
    
    metrics = {
        "avg_word_count": sum(len(t.split()) for t in texts) / len(texts),
        "emoji_use": sum(1 for t in texts if any(c in t for c in ["😂","😊","❤️"])),
        "formality": sum(1 for t in texts if any(w in clean_text(t) for w in ["however","therefore"]))
    }
    
    if metrics["avg_word_count"] > 75:
        metrics["style"] = "Detailed/analytical"
    elif metrics["emoji_use"] > 3:
        metrics["style"] = "Casual/expressive"
    else:
        metrics["style"] = "Straightforward"
    
    return metrics

def detect_interests(text: str) -> List[str]:
    text = clean_text(text)
    categories = {
        "Technology": ["python", "programming", "javascript"],
        "Gaming": ["game", "gaming", "playstation"],
        "Sports": ["football", "basketball", "soccer"]
    }
    return [cat for cat, terms in categories.items() if any(term in text for term in terms)]

# --- Streamlit UI Components ---
def show_persona_summary(persona):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Basic Info")
        st.metric("Account Age", persona["account_age"])
        st.metric("Total Karma", f"{persona['post_karma'] + persona['comment_karma']:,}")
        
        st.subheader("✍️ Writing Style")
        st.write(f"**{persona['writing_style']['style']}**")
        st.caption(f"Avg. {persona['writing_style']['avg_word_count']:.1f} words per post")
    
    with col2:
        st.subheader("🧠 Personality Traits")
        for trait in persona["traits"]:
            st.success(f"✓ {trait}")
        
        st.subheader("🎯 Top Interests")
        for interest in persona["interests"]:
            st.info(f"• {interest}")

def show_activity_charts(persona):
    tab1, tab2 = st.tabs(["Subreddit Activity", "Posting Times"])
    
    with tab1:
        df_subs = pd.DataFrame(persona["subreddit_activity"].items(), 
                             columns=["Subreddit", "Count"]).sort_values("Count", ascending=False)
        st.bar_chart(df_subs.set_index("Subreddit"), height=300)
    
    with tab2:
        if persona["activity_hours"]:
            fig, ax = plt.subplots()
            ax.hist(persona["activity_hours"], bins=24)
            ax.set_xlabel("Hour of Day (UTC)")
            st.pyplot(fig)
        else:
            st.warning("No timing data available")

# --- Main Analysis Function ---
def generate_persona(username: str) -> Dict:
    try:
        user = reddit.redditor(username)
        comments = list(user.comments.new(limit=100))
        posts = list(user.submissions.new(limit=100))
        
        if not comments and not posts:
            return {"error": "No public activity found"}
        
        # Process data
        all_texts = [c.body for c in comments] + [p.title for p in posts]
        subreddits = [c.subreddit.display_name for c in comments] + [p.subreddit.display_name for p in posts]
        
        return {
            "username": f"u/{username}",
            "account_age": datetime.fromtimestamp(user.created_utc).strftime("%Y-%m-%d"),
            "post_karma": user.link_karma,
            "comment_karma": user.comment_karma,
            "writing_style": analyze_writing_style(all_texts),
            "interests": list(set(interest for text in all_texts for interest in detect_interests(text))),
            "traits": ["Opinionated"] if any("i think" in clean_text(t) for t in all_texts) else [],
            "subreddit_activity": dict(Counter(subreddits).most_common(10)),
            "activity_hours": [datetime.fromtimestamp(c.created_utc).hour for c in comments],
            "sample_comments": [c.body[:200] + "..." for c in comments[:3]],
            "sample_posts": [p.title for p in posts[:3]]
        }
    except Exception as e:
        return {"error": str(e)}

# --- Main App Flow ---
username = st.text_input("Enter Reddit username (without u/):", "spez")

if st.button("Analyze", type="primary"):
    with st.spinner(f"Analyzing u/{username}..."):
        persona = generate_persona(username)
    
    if "error" in persona:
        st.error(f"Error: {persona['error']}")
    else:
        show_persona_summary(persona)
        st.divider()
        show_activity_charts(persona)
        
        with st.expander("📝 View Sample Content"):
            st.subheader("Recent Comments")
            for comment in persona["sample_comments"]:
                st.text(comment)
            
            st.subheader("Recent Post Titles")
            for post in persona["sample_posts"]:
                st.text(post)

# --- Sidebar ---
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool analyzes public Reddit activity to generate:
    - Personality traits
    - Writing style
    - Community engagement
    - Posting patterns
    """)
    
    st.divider()
    st.caption("Note: Only analyzes publicly available data")
    st.caption("Respect privacy and Reddit's API terms")

# --- How to Run ---
"""
To run this app:
1. Install requirements: `pip install streamlit praw pandas matplotlib`
2. Create `.streamlit/secrets.toml` with your Reddit API credentials
3. Run: `streamlit run reddit_persona_app.py`
"""