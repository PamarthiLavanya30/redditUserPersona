import praw
reddit = praw.Reddit(
    client_id="55gDGuRGc17g8dGjaY2iw",
    client_secret="6Y5L4uBjdTqSb8Evb5bxCTLE5erpAg",
    user_agent="PersonaGenerator/1.0"
)
print(reddit.user.me())  # Should print YOUR username