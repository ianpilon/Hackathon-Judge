# YouTube Video Content Search App

This application uses CrewAI's YoutubeVideoSearchTool to perform semantic searches within YouTube video content. It provides a simple web interface built with Streamlit.

## Features

- Search within specific YouTube videos by providing a URL
- Perform general YouTube content searches
- AI-powered semantic search using RAG (Retrieval-Augmented Generation)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser (it will open automatically when you run the app)
2. Optionally enter a YouTube video URL if you want to search within a specific video
3. Enter your search query
4. Click the "Search" button to get results

## Note

Make sure you have proper API credentials set up if you're using custom models or embeddings.
