from flask import Flask, render_template, request
from concurrent.futures import ThreadPoolExecutor
from sentiment_analysis import fetch_news, summarize_sentiments, queries_create

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    query = request.form['query']
    method = request.form['method']
    
    queries = queries_create(query)
    all_articles = []
    max_workers = min(8, len(queries)) if queries else 0
    if max_workers > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for articles in executor.map(lambda q: fetch_news(q, num_articles=5), queries):
                all_articles.extend(articles)
    
    detailed_results, summary, total_articles = summarize_sentiments(all_articles, method)
    
    return render_template('results.html', detailed_results=detailed_results, summary=summary, total_articles=total_articles)

if __name__ == '__main__':
    app.run(debug=True)