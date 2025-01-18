# YouTube Video Search Tool

The YoutubeVideoSearchTool is a powerful component of the crewai_tools package designed to perform semantic searches within YouTube video content using Retrieval-Augmented Generation (RAG) techniques.

## Description

This tool enables:
- Semantic searches within YouTube video content
- Flexible search capabilities across any YouTube video content
- Targeted searches within specific YouTube videos using URLs
- RAG-based retrieval for improved search accuracy

## Installation

Install the tool using pip:

```bash
pip install 'crewai[tools]'
```

## Usage Example

```python
from crewai_tools import YoutubeVideoSearchTool

# General search across Youtube content
tool = YoutubeVideoSearchTool()

# Targeted search within a specific video
tool = YoutubeVideoSearchTool(
    youtube_video_url='https://youtube.com/watch?v=example'
)
```

## Arguments

- `youtube_video_url`: Optional at initialization but required for targeting specific videos. Specifies the YouTube video URL to search within.

## Custom Configuration

The tool supports customization of both the language model and embeddings:

```python
tool = YoutubeVideoSearchTool(
    config=dict(
        llm=dict(
            provider="ollama",  # Alternatives: google, openai, anthropic, llama2
            config=dict(
                model="llama2",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google",  # Alternatives: openai, ollama
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
            ),
        ),
    )
)
```

By default, the tool uses OpenAI for both embeddings and summarization, but can be configured to use alternative providers as shown above.
