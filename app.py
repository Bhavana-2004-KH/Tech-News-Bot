from flask import Flask, render_template, request
import requests
from transformers import pipeline 
import torch


# --------------------------
# CONFIG
# --------------------------
NEWS_API_KEY = "2a041428774e44668e3f4bc293c31c5d"  # Replace with your own from https://newsapi.org
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

app = Flask(__name__)

# --------------------------
# Fetch Tech News (query-specific)
# --------------------------
def get_tech_news_by_query(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        return []
    return articles[:5]  # Return top 5 articles

# --------------------------
# Summarize News
# --------------------------
def summarize_news(articles):
    if not articles:
        return "No news found."
    
    # Combine titles + descriptions
    text_to_summarize = " ".join([f"{a.get('title', '')}. {a.get('description', '')}" for a in articles])
    
    # Limit size (BART can't handle very long input)
    if len(text_to_summarize.split()) > 500:
        text_to_summarize = " ".join(text_to_summarize.split()[:500])
    
    summary = summarizer(text_to_summarize, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

# --------------------------
# ROUTES
# --------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    summary = ""
    user_input = ""
    articles = []
    if request.method == "POST":
        user_input = request.form.get("question")
        articles = get_tech_news_by_query(user_input)
        summary = summarize_news(articles) if articles else f"No news found for '{user_input}'."
    return render_template("index.html", summary=summary, user_input=user_input, articles=articles)

# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
