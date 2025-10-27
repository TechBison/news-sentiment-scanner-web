import feedparser
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob   
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from urllib.parse import quote

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from concurrent.futures import ThreadPoolExecutor

fibnert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
fibnert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")

labels = ['negative', 'neutral', 'positive']

def fetch_news(query, num_articles=10):
    query_encoded = quote(query)
    rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:num_articles]:
        # Use summary (if present) as a fallback content source
        summary_text = ''
        if hasattr(entry, 'summary') and entry.summary:
            # strip HTML tags from summary
            soup = BeautifulSoup(entry.summary, 'html.parser')
            summary_text = soup.get_text(separator=' ', strip=True)
        title_text = getattr(entry, 'title', '') or ''

        fetched = fetch_article_content(entry.link)
        # Prefer fetched content; if too short, fall back to summary/title
        base_fallback = f"{title_text} {summary_text}".strip()
        content = fetched if (fetched and len(fetched) >= 200) else (summary_text or title_text or fetched)
        if content and len(content) < 50 and base_fallback:
            content = base_fallback

        articles.append({
            'title': title_text,
            'link': entry.link,
            'published': getattr(entry, 'published', ''),
            'content': (content or '').strip(),
        })
    return articles

def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content.strip()
    except Exception as e:
        return "Content could not be fetched."

def analyze_sentiment(text, method='vader'):
    if method == 'vader':
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        polarity = scores['compound']
        if polarity >= 0.05:
            sentiment = 'Positive'
        elif polarity <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        return sentiment, polarity
    
    elif method == 'textblob':
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = 'Positive'
        elif polarity < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        return sentiment, polarity
    elif method == 'finbert':
        if not text.strip():
            return 'Neutral', 0.0
        inputs = fibnert_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = fibnert_model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).numpy()[0]
        sentiment_idx = np.argmax(probabilities)
        sentiment = labels[sentiment_idx].capitalize()
        polarity = probabilities[sentiment_idx]
        return sentiment, polarity
    
def summarize_sentiments(articles, method='vader'):
    summary = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    detailed_results = []

    max_workers = min(8, len(articles)) if articles else 0
    if max_workers > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(lambda a: analyze_sentiment(a['content'], method), articles))
        for article, (sentiment, polarity) in zip(articles, results):
            summary[sentiment] += 1
            detailed_results.append({
                'title': article['title'],
                'link': article['link'],
                'published': article['published'],
                'sentiment': sentiment,
                'polarity': polarity
            })

    total_len = len(articles)
    # Compute percentages for template consumption
    def pct(c):
        return (c / total_len * 100) if total_len > 0 else 0
    summary.update({
        'Positive_percentage': pct(summary['Positive']),
        'Negative_percentage': pct(summary['Negative']),
        'Neutral_percentage': pct(summary['Neutral']),
    })

    # Console summary for debugging/CLI visibility
    print("\n--------- Market Sentiment Summary ---------\n")
    print(f"Total Articles Analyzed: {total_len}")
    for key in ['Positive', 'Negative', 'Neutral']:
        count = summary[key]
        percentage = summary[f"{key}_percentage"]
        print(f"{key}: {count} articles ({percentage:.2f}%)")
    print("\n--------------------------------------------\n")

    # Return structure aligned with templates/results.html expectations
    return detailed_results, summary, total_len

def queries_create(query):
    appenders = [" stock news", " market analysis", " financial news", " economic outlook", " investment trends", " stock market updates"]
    queries = [query + appender for appender in appenders]
    return queries