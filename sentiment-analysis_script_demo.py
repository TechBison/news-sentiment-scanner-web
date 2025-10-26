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

fibnert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
fibnert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")

labels = ['negative', 'neutral', 'positive']

def fetch_news(query, num_articles=10):
    query_encoded = quote(query)
    rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:num_articles]:
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'content': fetch_article_content(entry.link)

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
    
    for article in articles:
        sentiment, polarity = analyze_sentiment(article['content'], method)
        summary[sentiment] += 1
        detailed_results.append({
            'title': article['title'],
            'link': article['link'],
            'published': article['published'],
            'sentiment': sentiment,
            'polarity': polarity
        })
    
    total_len = len(articles)
    print("\n--------- Market Sentiment Summary ---------\n")
    print(f"Total Articles Analyzed: {total_len}")
    for sentiment, count in summary.items():
        percentage = (count / total_len) * 100 if total_len > 0 else 0
        print(f"{sentiment}: {count} articles ({percentage:.2f}%)")
    print("\n--------------------------------------------\n")
    return detailed_results

def queries_create(query):
    appenders = [" stock news", " market analysis", " financial news", " economic outlook", " investment trends", " stock market updates"]
    queries = [query + appender for appender in appenders]
    return queries

if __name__ == "__main__":
    query = input("Enter the topic or stock symbol to analyze sentiment for: ")
    method = input("Choose sentiment analysis method (vader/textblob/finbert): ").strip().lower()


    queries = queries_create(query)
    all_articles = []
    for q in queries:
        articles = fetch_news(q, num_articles=5)
        all_articles.extend(articles)
    detailed_results = summarize_sentiments(all_articles, method)
    
    for result in detailed_results:
        print(f"Title: {result['title']}")
        print(f"Link: {result['link']}")
        print(f"Published: {result['published']}")
        print(f"Sentiment: {result['sentiment']} (Polarity Score: {result['polarity']:.4f})")
        print("--------------------------------------------------\n")