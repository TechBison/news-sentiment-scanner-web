# News Sentiment Scanner Web Application

This project is a web application that allows users to analyze the sentiment of news articles based on a given topic or stock symbol. It utilizes various sentiment analysis methods to provide insights into the market sentiment.

## Project Structure

- **app.py**: Main entry point of the web application, setting up the Flask app and defining routes.
- **sentiment_analysis.py**: Contains the sentiment analysis logic, including functions to fetch news articles and analyze sentiment.
- **requirements.txt**: Lists the dependencies required for the project.
- **templates/**: Contains HTML templates for the web application.
  - **layout.html**: Base layout for the web application.
  - **index.html**: Home page with a form for user input.
  - **results.html**: Displays the results of the sentiment analysis.
- **static/**: Contains static files such as CSS and JavaScript.
  - **css/styles.css**: Styles for the web application.
  - **js/main.js**: JavaScript code for client-side functionality.
- **tests/**: Contains unit tests for the sentiment analysis functions.
  - **test_sentiment.py**: Unit tests to ensure functionality works as expected.
- **Dockerfile**: Instructions for building a Docker image for the web application.
- **.devcontainer/**: Configuration for the development container.
  - **devcontainer.json**: Development container settings.
  - **Dockerfile**: Used to build the development container.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd news-sentiment-scanner-web
   ```

2. **Install dependencies**:
   You can install the required Python packages using pip:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the Flask application by running:
   ```
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

4. **Docker Setup** (optional):
   If you prefer to run the application in a Docker container, build the Docker image using:
   ```
   docker build -t news-sentiment-scanner .
   ```
   Then run the container:
   ```
  docker run --rm -p 5000:5000 --security-opt seccomp=unconfined news-sentiment-scanner
   ```

## Usage

- Navigate to the home page and enter a topic or stock symbol to analyze sentiment.
- Choose the sentiment analysis method (VADER, TextBlob, or FinBERT).
- Submit the form to view the results, which will display a summary and detailed analysis of the articles.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.