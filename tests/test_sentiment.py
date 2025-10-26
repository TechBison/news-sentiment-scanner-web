import unittest
from sentiment_analysis import fetch_news, analyze_sentiment, summarize_sentiments

class TestSentimentAnalysis(unittest.TestCase):

    def test_fetch_news(self):
        query = "Tesla"
        articles = fetch_news(query, num_articles=5)
        self.assertGreater(len(articles), 0)
        for article in articles:
            self.assertIn('title', article)
            self.assertIn('link', article)
            self.assertIn('published', article)
            self.assertIn('content', article)

    def test_analyze_sentiment_vader(self):
        text = "The stock market is doing great!"
        sentiment, polarity = analyze_sentiment(text, method='vader')
        self.assertEqual(sentiment, 'Positive')
        self.assertGreater(polarity, 0)

    def test_analyze_sentiment_textblob(self):
        text = "I am not happy with the current situation."
        sentiment, polarity = analyze_sentiment(text, method='textblob')
        self.assertEqual(sentiment, 'Negative')
        self.assertLess(polarity, 0)

    def test_analyze_sentiment_finbert(self):
        text = "The company's performance has been stable."
        sentiment, polarity = analyze_sentiment(text, method='finbert')
        self.assertIn(sentiment, ['Positive', 'Neutral', 'Negative'])
        self.assertGreaterEqual(polarity, 0)

    def test_summarize_sentiments(self):
        articles = [
            {'content': "I love this stock!", 'title': "Positive News", 'link': "", 'published': ""},
            {'content': "This is a bad investment.", 'title': "Negative News", 'link': "", 'published': ""},
            {'content': "It's okay, not great.", 'title': "Neutral News", 'link': "", 'published': ""}
        ]
        summary = summarize_sentiments(articles, method='vader')
        self.assertEqual(summary[0]['sentiment'], 'Positive')
        self.assertEqual(summary[1]['sentiment'], 'Negative')
        self.assertEqual(summary[2]['sentiment'], 'Neutral')

if __name__ == '__main__':
    unittest.main()