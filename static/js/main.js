// This file contains JavaScript code for client-side functionality, such as form submission and dynamic content updates.

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("sentiment-form");
    const resultsDiv = document.getElementById("results");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const query = formData.get("query");
        const method = formData.get("method");

        fetch(`/analyze?query=${encodeURIComponent(query)}&method=${method}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error("Error:", error);
                resultsDiv.innerHTML = "<p>There was an error processing your request.</p>";
            });
    });

    function displayResults(data) {
        resultsDiv.innerHTML = ""; // Clear previous results

        if (data.error) {
            resultsDiv.innerHTML = `<p>${data.error}</p>`;
            return;
        }

        const summary = document.createElement("h2");
        summary.textContent = "Market Sentiment Summary";
        resultsDiv.appendChild(summary);

        const totalArticles = document.createElement("p");
        totalArticles.textContent = `Total Articles Analyzed: ${data.total}`;
        resultsDiv.appendChild(totalArticles);

        const sentimentCounts = document.createElement("ul");
        for (const [sentiment, count] of Object.entries(data.summary)) {
            const listItem = document.createElement("li");
            listItem.textContent = `${sentiment}: ${count} articles (${((count / data.total) * 100).toFixed(2)}%)`;
            sentimentCounts.appendChild(listItem);
        }
        resultsDiv.appendChild(sentimentCounts);

        const detailedResults = document.createElement("h3");
        detailedResults.textContent = "Detailed Results:";
        resultsDiv.appendChild(detailedResults);

        data.results.forEach(result => {
            const articleDiv = document.createElement("div");
            articleDiv.innerHTML = `
                <h4>${result.title}</h4>
                <p><a href="${result.link}" target="_blank">Read more</a></p>
                <p>Published: ${result.published}</p>
                <p>Sentiment: ${result.sentiment} (Polarity Score: ${result.polarity.toFixed(4)})</p>
                <hr>
            `;
            resultsDiv.appendChild(articleDiv);
        });
    }
});