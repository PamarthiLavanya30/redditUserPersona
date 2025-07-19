import praw
import os
from datetime import datetime
from collections import defaultdict
import time
import textwrap
import re
from typing import Dict, List, Tuple

class RedditPersonaGenerator:
    def __init__(self):
        """Initialize Reddit API connection with error handling"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID", "-55gDGuRGc17g8dGjaY2iw"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET", "6Y5L4uBjdTqSb8Evb5bxCTLE5erpAg"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "PersonaGenerator/1.0 by pamarthi_lavanya")
            )
            # Test authentication
            self.reddit.user.me()
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            print("Please verify your:")
            print("1. Client ID and Secret at https://www.reddit.com/prefs/apps")
            print("2. User Agent format (must include your username)")
            raise SystemExit(1)

    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        return re.sub(r'[^\w\s]', '', text.lower())

    def analyze_writing_style(self, texts: List[str]) -> Dict:
        """Analyzes writing characteristics with more metrics"""
        if not texts:
            return {
                "Description": "No text available",
                "Average Word Count": 0,
                "Emoji Usage": 0,
                "Formality Score": 0,
                "Readability": "N/A"
            }

        total_words = sum(len(t.split()) for t in texts)
        avg_word_count = total_words / len(texts)
        
        # Enhanced style analysis
        style = {
            "Average Word Count": avg_word_count,
            "Emoji Usage": sum(1 for t in texts if any(c in t for c in ["😂","😊","❤️"])),
            "Formality Score": sum(1 for t in texts if any(w in self._clean_text(t) 
                               for w in ["however","therefore","moreover"])),
            "Question Frequency": sum(1 for t in texts if "?" in t),
            "Exclamation Frequency": sum(1 for t in texts if "!" in t)
        }
        
        # Determine style
        if style["Average Word Count"] > 75:
            style["Description"] = "Detailed and analytical"
        elif style["Average Word Count"] > 40:
            style["Description"] = "Balanced and thoughtful"
        elif style["Emoji Usage"] > 3:
            style["Description"] = "Casual and expressive"
        elif style["Formality Score"] > 5:
            style["Description"] = "Formal and structured"
        else:
            style["Description"] = "Straightforward and concise"
            
        return style

    def detect_interests(self, text: str) -> List[str]:
        """Detect interests from text with more categories"""
        interests = []
        text = self._clean_text(text)
        
        interest_keywords = {
            "Technology": ["python", "programming", "javascript", "linux", "github"],
            "Gaming": ["game", "gaming", "playstation", "xbox", "nintendo"],
            "Sports": ["football", "basketball", "soccer", "nba", "nfl"],
            "Movies/TV": ["movie", "netflix", "marvel", "star wars", "tv show"],
            "Science": ["space", "physics", "biology", "research", "astronomy"]
        }
        
        for category, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(category)
                
        return interests

    def detect_personality_traits(self, text: str) -> List[str]:
        """Detect personality traits with more nuance"""
        traits = []
        text = self._clean_text(text)
        
        if any(w in text for w in ["i think", "in my opinion", "i believe"]):
            traits.append("Opinionated")
        if any(w in text for w in ["lol", "haha", "funny", "joke"]):
            traits.append("Humorous")
        if any(w in text for w in ["help", "advice", "suggestion"]):
            traits.append("Helpful")
        if any(w in text for w in ["why", "how", "explain"]):
            traits.append("Curious")
            
        return traits

    def generate_persona(self, username: str) -> Dict:
        """Generates comprehensive persona with error handling"""
        try:
            user = self.reddit.redditor(username)
            comments = list(user.comments.new(limit=100))
            posts = list(user.submissions.new(limit=100))
            
            if not comments and not posts:
                return {"error": "No public activity found"}
                
            # Analyze writing style from both comments and posts
            all_texts = [c.body for c in comments] + [p.title for p in posts]
            
            persona = {
                "Username": f"u/{username}",
                "Account Age": str(datetime.fromtimestamp(user.created_utc)),
                "Writing Style": self.analyze_writing_style(all_texts),
                "Preferred Subreddits": defaultdict(int),
                "Interests & Hobbies": defaultdict(list),
                "Personality Traits": defaultdict(list),
                "Activity Summary": {
                    "Total Comments": len(comments),
                    "Total Posts": len(posts),
                    "Comment Karma": user.comment_karma,
                    "Post Karma": user.link_karma,
                    "First Seen": min(
                        datetime.fromtimestamp(c.created_utc) for c in comments
                    ) if comments else "N/A"
                },
                "Citations": {
                    "Comments": [c.permalink for c in comments[:3]],
                    "Posts": [p.permalink for p in posts[:3]]
                }
            }

            # Analyze content
            for comment in comments:
                subreddit = comment.subreddit.display_name
                persona["Preferred Subreddits"][subreddit] += 1
                
                for interest in self.detect_interests(comment.body):
                    persona["Interests & Hobbies"][interest].append(comment.permalink)
                    
                for trait in self.detect_personality_traits(comment.body):
                    persona["Personality Traits"][trait].append(comment.permalink)

            return persona
            
        except Exception as e:
            return {"error": str(e)}

    def format_output(self, persona: Dict) -> str:
        """Creates beautifully formatted output with more sections"""
        if "error" in persona:
            return f"❌ Error generating persona: {persona['error']}"
            
        output = []
        output.append(f"🔹 REDDIT USER PERSONA: {persona['Username']}")
        output.append(f"📅 Account Created: {persona['Account Age']}")
        
        # Writing Style
        output.append("\n✍️ WRITING STYLE ANALYSIS:")
        ws = persona["Writing Style"]
        output.append(f"- Primary Style: {ws['Description']}")
        output.append(f"- Avg. words per post: {ws['Average Word Count']:.1f}")
        output.append(f"- Emoji usage: {ws['Emoji Usage']} times")
        output.append(f"- Questions asked: {ws['Question Frequency']} times")
        output.append(f"- Exclamations used: {ws['Exclamation Frequency']} times")

        # Subreddit Activity
        output.append("\n🏆 SUBREDDIT ACTIVITY:")
        top_subs = sorted(persona["Preferred Subreddits"].items(), 
                         key=lambda x: x[1], reverse=True)[:5]
        for sub, count in top_subs:
            output.append(f"- r/{sub}: {count} interactions")

        # Interests
        output.append("\n🎯 DETECTED INTERESTS:")
        for interest, urls in persona["Interests & Hobbies"].items():
            output.append(f"- {interest} (cited {len(urls)} times)")

        # Personality
        output.append("\n🧠 PERSONALITY TRAITS:")
        for trait, urls in persona["Personality Traits"].items():
            output.append(f"- {trait} (cited {len(urls)} times)")

        # Activity Summary
        output.append("\n📊 ACTIVITY SUMMARY:")
        activity = persona["Activity Summary"]
        output.append(f"- Comments: {activity['Total Comments']} (Karma: {activity['Comment Karma']})")
        output.append(f"- Posts: {activity['Total Posts']} (Karma: {activity['Post Karma']})")
        output.append(f"- First seen: {activity['First Seen']}")

        # Example Content
        output.append("\n🔍 EXAMPLE CONTENT:")
        output.append("- Recent comments:")
        for url in persona["Citations"]["Comments"][:3]:
            output.append(f"  • {url}")
        output.append("- Recent posts:")
        for url in persona["Citations"]["Posts"][:3]:
            output.append(f"  • {url}")

        return "\n".join(output)

    def save_to_file(self, username: str, content: str) -> str:
        """Saves output to file with timestamp"""
        os.makedirs("personas", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"personas/{username}_persona_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return filename

if __name__ == "__main__":
    print("=== Reddit User Persona Generator ===")
    print("Analyzes a Reddit user's activity to create a comprehensive profile\n")
    
    generator = RedditPersonaGenerator()
    
    while True:
        username = input("Enter Reddit username (or 'quit' to exit): ").strip()
        if username.lower() == 'quit':
            break
            
        if "/user/" in username:
            username = username.split("/user/")[1].rstrip("/")
        
        print(f"\n🚀 Analyzing u/{username}...")
        
        try:
            start_time = time.time()
            persona = generator.generate_persona(username)
            output = generator.format_output(persona)
            saved_file = generator.save_to_file(username, output)
            
            print(f"\n✅ Analysis completed in {time.time()-start_time:.1f} seconds\n")
            print(output)
            print(f"\n📄 Full report saved to: {saved_file}")
            
        except Exception as e:
            print(f"❌ Error analyzing user: {str(e)}")
        
        print("\n" + "="*50 + "\n")