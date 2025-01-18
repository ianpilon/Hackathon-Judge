__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from crewai import Agent, Task, Crew, Process
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set your OpenAI API key in the .env file")
    st.stop()

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_transcript(video_id):
    """Get video transcript using youtube_transcript_api"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Error getting transcript: {str(e)}")
        return None

def get_video_info(url):
    """Get video information using requests and BeautifulSoup"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get video title from meta tags
        title = soup.find('meta', property='og:title')
        title = title['content'] if title else 'Unknown Title'
        
        # Get video description from meta tags
        description = soup.find('meta', property='og:description')
        description = description['content'] if description else 'No description available'
        
        # Get channel name from meta tags
        author = soup.find('link', itemprop='name')
        author = author['content'] if author else 'Unknown Author'
        
        return {
            'title': title,
            'description': description,
            'author': author,
            'length': 0  # We'll skip video length as it's not critical
        }
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def analyze_video_content(video_url, search_query):
    """Analyze video content using CrewAI"""
    video_id = get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"

    # Get video information and transcript
    video_info = get_video_info(video_url)
    transcript = get_video_transcript(video_id)

    if not video_info or not transcript:
        return "Could not retrieve video content"

    # Create an agent to analyze the content
    evaluator = Agent(
        role='Hackathon Project Evaluator',
        goal='Evaluate hackathon project submissions based on multiple criteria',
        backstory="""You are an expert at evaluating hackathon projects, with deep 
        knowledge of blockchain technology, AI, and sponsor integrations. You provide 
        detailed scoring across multiple categories.""",
        verbose=True,
        allow_delegation=False
    )

    # Create evaluation criteria
    evaluation_prompt = f"""
    Analyze the following hackathon project video and provide a detailed evaluation. For each category, provide a score and detailed justification.
    Use EXACTLY this format for each category (including the exact text "Score /5:" in the headers):

    1. Innovation (Score /5):
    Score: X
    [Detailed justification...]

    2. Technical Complexity (Score /5):
    Score: X
    [Detailed justification...]

    3. Functionality (Score /5):
    Score: X
    [Detailed justification...]

    4. User Experience (Score /5):
    Score: X
    [Detailed justification...]

    5. Presentation (Score /5):
    Score: X
    [Detailed justification...]

    6. Strategic Vision (Score /5):
    Score: X
    [Detailed justification...]

    7. Accessibility (Score /5):
    Score: X
    [Detailed justification...]

    8. Sponsor Protocol Integration (Score /5):
    Score: X
    [CRITICAL SCORING INSTRUCTIONS FOR SPONSORS]
    You must follow these rules EXACTLY:
    1. ONLY award points if the video EXPLICITLY mentions using a sponsor's technology
    2. Do NOT infer or assume sponsor usage - it must be clearly stated
    3. Award points ONLY for sponsors that are explicitly mentioned as being used:
       - Story Protocol: 2 points ONLY if they explicitly say they used Story Protocol
       - FXN: 2 points ONLY if they explicitly say they used FXN
       - Alliances: 1 point ONLY if they explicitly say they used Alliances
    4. Score MUST be 0 if no sponsors are explicitly mentioned as being used
    5. You must quote the EXACT words from the video that mention using each sponsor
    
    Format your response as:
    - Story Protocol: [Yes/No] - If Yes, provide EXACT quote showing usage
    - FXN: [Yes/No] - If Yes, provide EXACT quote showing usage
    - Alliances: [Yes/No] - If Yes, provide EXACT quote showing usage
    
    [Final score justification showing exact calculation based on explicit mentions]

    9. Transaction Analysis (Score /5):
    Score: X
    [Detailed justification...]

    10. Autonomy Assessment (Score /5):
    Score: X
    [Detailed justification...]

    Scoring Guidelines:
    - Innovation: Evaluate uniqueness, creativity, and novel approaches
    - Technical Complexity: Consider implementation sophistication and technology usage
    - Functionality: Assess feature completeness and reliability
    - User Experience: Evaluate interface design and usability
    - Presentation: Consider explanation clarity and demo quality
    - Strategic Vision: Assess market understanding and growth potential
    - Accessibility: Evaluate inclusive design and ease of adoption
    - Sponsor Integration: 
      * ONLY award points for EXPLICIT mentions of using sponsor technology
      * Must quote exact words from video for any points awarded
      * Zero points if no explicit sponsor usage is mentioned
    - Transaction Analysis: Evaluate efficiency and security
    - Autonomy: Assess automation level and independence

    Video to analyze:
    Title: {video_info['title']}
    Author: {video_info['author']}
    Content: {transcript}
    
    Additional Focus: {search_query}

    Remember:
    1. Use the EXACT format specified above
    2. Include "Score: X" for each category
    3. For sponsor integration, ONLY award points for EXPLICIT mentions of using sponsor technology
    4. Quote EXACT words for any sponsor points awarded
    5. Score MUST be 0 for sponsors if no explicit usage is mentioned
    """

    # Create a task for the agent
    analysis_task = Task(
        description=evaluation_prompt,
        expected_output="""A detailed evaluation report with scores and justifications for each category,
        with special attention to sponsor integrations.""",
        agent=evaluator
    )

    # Create and run the crew
    crew = Crew(
        agents=[evaluator],
        tasks=[analysis_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result

def format_analysis_result(result):
    """Format the analysis result into clean markdown with scores"""
    try:
        # If result is a dictionary with 'raw' key, extract the content
        if isinstance(result, dict) and 'raw' in result:
            content = result['raw']
        else:
            content = str(result)

        # Custom CSS for the evaluation cards
        st.markdown("""
            <style>
            .evaluation-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }
            .eval-card {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .eval-card h3 {
                color: #1E88E5;
                margin: 0 0 1rem 0;
                font-size: 1.2rem;
            }
            .score {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1E88E5;
                margin: 0.5rem 0;
                text-align: center;
            }
            .stars {
                color: #FFD700;
                margin-bottom: 1rem;
                text-align: center;
                font-size: 1.2rem;
            }
            .section-content {
                color: #666;
                font-size: 0.9rem;
                line-height: 1.6;
            }
            .final-score {
                background: #f8f9fe;
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                margin-top: 2rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .score-circle {
                width: 150px;
                height: 150px;
                margin: 0 auto;
                position: relative;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
            }
            .percentage {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1E88E5;
            }
            .sponsor-list {
                list-style: none;
                padding: 0;
                margin: 1rem 0;
            }
            .sponsor-item {
                padding: 0.5rem 0;
                border-bottom: 1px solid #eee;
            }
            .sponsor-item:last-child {
                border-bottom: none;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Extract title and create header
        title_match = re.search(r'"([^"]+)"', content)
        if title_match:
            st.markdown(f"## Analysis of: {title_match.group(1)}")
        
        # Create evaluation grid
        st.markdown('<div class="evaluation-grid">', unsafe_allow_html=True)
        
        # Process each section using the new format
        scores = []
        sections = content.split('\n\n')
        
        for section in sections:
            # Look for numbered sections with scores
            if match := re.match(r'(\d+)\.\s+(.*?)\(Score\s+/5\):', section, re.DOTALL):
                category = match.group(2).strip()
                section_content = section[match.end():].strip()
                
                # Extract score
                score_match = re.search(r'Score:\s*(\d+\.?\d*)', section_content)
                if score_match:
                    score = float(score_match.group(1))
                    scores.append(score)
                    
                    # Remove the "Score: X" line from content
                    content_text = re.sub(r'Score:\s*\d+\.?\d*\n?', '', section_content).strip()
                    
                    # Special formatting for sponsor section
                    if "Sponsor Protocol Integration" in category:
                        sponsor_content = '<div class="sponsor-list">'
                        for line in content_text.split('\n'):
                            if any(s in line for s in ["Story Protocol:", "FXN:", "Alliances:"]):
                                sponsor_content += f'<div class="sponsor-item">{line}</div>'
                        sponsor_content += '</div>'
                        content_text = sponsor_content
                    
                    # Create card
                    st.markdown(f"""
                        <div class="eval-card">
                            <h3>{category}</h3>
                            <div class="score">{score}/5</div>
                            <div class="stars">{'★' * int(score)}{'☆' * (5-int(score))}</div>
                            <div class="section-content">{content_text}</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Calculate and display final score
        if scores:
            final_score = (sum(scores) / len(scores)) * 20  # Convert to percentage
            st.markdown(f"""
                <div class="final-score">
                    <h2>Final Score</h2>
                    <div class="score-circle">
                        <div class="percentage">{int(final_score)}%</div>
                    </div>
                    <p>Grade: {chr(65 + min(int((100 - final_score) / 10), 25))}</p>
                </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error formatting result: {str(e)}")
        st.write("Debug - Exception details:", e)
        st.write("Debug - Result type:", type(result))
        return str(result)

def main():
    st.set_page_config(page_title="YouTube Video Content Analysis", layout="wide")
    
    # Custom CSS for the main app
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #f8f9fe;
        }
        h1 {
            color: #1E88E5;
            margin-bottom: 2rem;
            text-align: center;
        }
        .stButton button {
            width: 100%;
            margin-top: 1rem;
            background-color: #1E88E5;
            color: white;
        }
        .stTextInput > div > div {
            background-color: white;
        }
        .url-input {
            max-width: 800px;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("YouTube Video Content Analysis")

    # Default analysis query
    DEFAULT_QUERY = "Analyze the video project evaluation for innovation, technical complexity, functionality, user experience, presentation, strategic vision, accessibility, and sponsor protocol. Provide a detailed assessment including transaction analysis and autonomy assessment."
    
    # Centered URL input
    st.markdown('<div class="url-input">', unsafe_allow_html=True)
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://youtube.com/watch?v=..."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Analyze"):
        if not youtube_url:
            st.warning("Please enter a YouTube URL")
            return

        with st.spinner("Analyzing video content..."):
            try:
                result = analyze_video_content(youtube_url, DEFAULT_QUERY)
                format_analysis_result(result)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
