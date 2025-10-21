from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re
from typing import List, Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Initialize clients
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ============================================================================
# AGENT 1: DATA ACQUISITION AGENT
# ============================================================================

class DataAcquisitionAgent:
    """Fetches YouTube channel data, video metadata, comments, and transcripts"""
    
    def __init__(self, youtube_client):
        self.youtube = youtube_client
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get basic channel information"""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            ).execute()
            
            if not response['items']:
                return {'error': 'Channel not found'}
            
            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'subscriber_count': channel['statistics'].get('subscriberCount', 'Hidden'),
                'video_count': channel['statistics']['videoCount'],
                'view_count': channel['statistics']['viewCount'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent videos from a channel"""
        try:
            # Get uploads playlist ID
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return []
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                playlist_response = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
                
                # Get detailed video statistics
                video_details = self.youtube.videos().list(
                    part='statistics,snippet,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                for video in video_details['items']:
                    videos.append({
                        'id': video['id'],
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'published_at': video['snippet']['publishedAt'],
                        'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                        'view_count': int(video['statistics'].get('viewCount', 0)),
                        'like_count': int(video['statistics'].get('likeCount', 0)),
                        'comment_count': int(video['statistics'].get('commentCount', 0)),
                        'duration': video['contentDetails']['duration'],
                        'tags': video['snippet'].get('tags', [])
                    })
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch top comments from a video"""
        try:
            comments = []
            next_page_token = None
            
            while len(comments) < max_results:
                response = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    order='relevance',
                    pageToken=next_page_token
                ).execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'text': comment['textDisplay'],
                        'author': comment['authorDisplayName'],
                        'like_count': comment['likeCount'],
                        'published_at': comment['publishedAt']
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []
    
    def get_video_transcript(self, video_id: str) -> str:
        """Fetch video transcript"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([entry['text'] for entry in transcript_list])
            return transcript
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return ""


# ============================================================================
# AGENT 2: TREND ANALYSIS AGENT
# ============================================================================

class TrendAnalysisAgent:
    """Analyzes video performance and identifies trends using Groq"""
    
    def __init__(self, groq_client):
        self.groq = groq_client
    
    def analyze_performance_patterns(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze video performance patterns"""
        if not videos:
            return {'error': 'No videos to analyze'}
        
        # Calculate engagement metrics
        for video in videos:
            views = video['view_count']
            if views > 0:
                video['engagement_rate'] = (video['like_count'] + video['comment_count']) / views
            else:
                video['engagement_rate'] = 0
        
        # Sort by performance
        sorted_videos = sorted(videos, key=lambda x: x['view_count'], reverse=True)
        top_performers = sorted_videos[:10]
        
        # Prepare data for Groq analysis
        analysis_prompt = self._create_analysis_prompt(top_performers, videos)
        
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert YouTube content analyst. Analyze video performance data and identify patterns, trends, and insights. Provide structured, actionable analysis."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'top_performers': top_performers[:5],
                'average_views': sum(v['view_count'] for v in videos) / len(videos),
                'average_engagement': sum(v['engagement_rate'] for v in videos) / len(videos),
                'groq_analysis': analysis,
                'total_videos_analyzed': len(videos)
            }
        except Exception as e:
            return {'error': f'Groq analysis failed: {str(e)}'}
    
    def _create_analysis_prompt(self, top_performers: List[Dict], all_videos: List[Dict]) -> str:
        """Create a detailed prompt for Groq analysis"""
        prompt = f"""Analyze the following YouTube channel performance data:

CHANNEL OVERVIEW:
- Total videos analyzed: {len(all_videos)}
- Average views: {sum(v['view_count'] for v in all_videos) / len(all_videos):.0f}

TOP 5 PERFORMING VIDEOS:
"""
        for i, video in enumerate(top_performers[:5], 1):
            prompt += f"""
{i}. Title: {video['title']}
   - Views: {video['view_count']:,}
   - Likes: {video['like_count']:,}
   - Comments: {video['comment_count']:,}
   - Engagement Rate: {video['engagement_rate']:.4f}
   - Published: {video['published_at'][:10]}
   - Tags: {', '.join(video['tags'][:5])}
"""
        
        prompt += """
ANALYSIS REQUIRED:
1. What patterns do you see in the top-performing videos (titles, topics, timing)?
2. What title/thumbnail strategies appear most effective?
3. What topics or themes generate the most engagement?
4. What posting patterns correlate with success?
5. What are 3 specific hypotheses about why these videos performed well?

Provide structured, data-driven insights."""
        
        return prompt
    
    def analyze_comment_sentiment(self, comments: List[Dict], video_title: str) -> Dict[str, Any]:
        """Analyze comment sentiment and themes using Groq"""
        if not comments:
            return {'error': 'No comments to analyze'}
        
        # Prepare comments for analysis
        comment_texts = [c['text'] for c in comments[:50]]  # Analyze top 50 comments
        
        prompt = f"""Analyze the following comments from the YouTube video "{video_title}":

COMMENTS:
{chr(10).join(f"- {comment}" for comment in comment_texts[:30])}

ANALYSIS REQUIRED:
1. Overall sentiment (positive/negative/mixed)
2. Main themes and topics discussed
3. Common questions or concerns
4. Audience pain points or desires
5. Content improvement suggestions based on feedback

Provide a structured analysis."""
        
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing YouTube comments to understand audience sentiment and needs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                'sentiment_analysis': response.choices[0].message.content,
                'total_comments_analyzed': len(comments)
            }
        except Exception as e:
            return {'error': f'Sentiment analysis failed: {str(e)}'}


# ============================================================================
# AGENT 3: STRATEGY GENERATION AGENT
# ============================================================================

class StrategyGenerationAgent:
    """Generates content strategy based on trend analysis"""
    
    def __init__(self, groq_client):
        self.groq = groq_client
    
    def generate_content_strategy(self, trend_analysis: Dict, channel_info: Dict) -> Dict[str, Any]:
        """Generate comprehensive content strategy"""
        
        prompt = f"""Based on the following YouTube channel analysis, create a comprehensive content strategy:

CHANNEL: {channel_info.get('title', 'Unknown')}
SUBSCRIBERS: {channel_info.get('subscriber_count', 'Unknown')}

PERFORMANCE ANALYSIS:
{trend_analysis.get('groq_analysis', 'No analysis available')}

TOP PERFORMING VIDEOS:
{json.dumps([{'title': v['title'], 'views': v['view_count']} for v in trend_analysis.get('top_performers', [])[:3]], indent=2)}

TASK: Generate a detailed content strategy with:

1. **5 SPECIFIC VIDEO IDEAS**
   For each idea provide:
   - Video title (attention-grabbing, SEO-optimized)
   - Video description (2-3 sentences)
   - Target audience
   - Key talking points (3-5 bullet points)
   - Why this will perform well (based on data)

2. **CONTENT CALENDAR**
   - Optimal posting schedule (days/times)
   - Content mix (topic distribution)
   - Frequency recommendation

3. **OPTIMIZATION STRATEGIES**
   - Title/thumbnail best practices
   - SEO keywords to target
   - Engagement tactics

4. **GROWTH RECOMMENDATIONS**
   - Trending topics to cover
   - Collaboration opportunities
   - Community engagement strategies

Make it actionable and data-driven. Format as structured JSON."""
        
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert YouTube content strategist. Create detailed, actionable content strategies based on data analysis. Always return well-structured, implementable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            strategy = response.choices[0].message.content
            
            # Also generate quick wins
            quick_wins = self._generate_quick_wins(trend_analysis)
            
            return {
                'strategy': strategy,
                'quick_wins': quick_wins,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Strategy generation failed: {str(e)}'}
    
    def _generate_quick_wins(self, trend_analysis: Dict) -> List[str]:
        """Generate immediate action items"""
        quick_wins = []
        
        top_performers = trend_analysis.get('top_performers', [])
        if top_performers:
            # Extract patterns from top performers
            common_tags = defaultdict(int)
            for video in top_performers[:5]:
                for tag in video.get('tags', [])[:3]:
                    common_tags[tag] += 1
            
            if common_tags:
                top_tags = sorted(common_tags.items(), key=lambda x: x[1], reverse=True)[:3]
                quick_wins.append(f"Focus on tags: {', '.join([tag for tag, _ in top_tags])}")
        
        avg_views = trend_analysis.get('average_views', 0)
        if avg_views > 0:
            quick_wins.append(f"Target view benchmark: {avg_views:.0f} views")
        
        quick_wins.append("Analyze top 3 video titles for pattern replication")
        quick_wins.append("Engage with comments within first 24 hours of posting")
        
        return quick_wins


# ============================================================================
# INITIALIZE AGENTS
# ============================================================================

data_agent = DataAcquisitionAgent(youtube) if youtube else None
trend_agent = TrendAnalysisAgent(groq_client) if groq_client else None
strategy_agent = StrategyGenerationAgent(groq_client) if groq_client else None


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'youtube_api': 'configured' if YOUTUBE_API_KEY else 'missing',
        'groq_api': 'configured' if GROQ_API_KEY else 'missing',
        'timestamp': datetime.now().isoformat()
    })


def _resolve_channel_id(channel_identifier: str) -> str | None:
    """Resolve a YouTube channel URL/handle/custom name to a channel ID."""
    if not channel_identifier:
        return None

    s = channel_identifier.strip()
    # strip query/fragments and trailing slash
    s = s.split('?', 1)[0].split('#', 1)[0].rstrip('/')

    # If it's already a channel ID (starts with UC)
    if re.fullmatch(r'UC[0-9A-Za-z_-]{22}', s):
        return s

    # Attempt to parse common YouTube URL patterns
    m = re.search(r'youtube\.com/(?:channel/([A-Za-z0-9_-]+)|c/([^/?#]+)|user/([^/?#]+)|@([^/?#]+))', s)
    if m:
        # direct channel ID in /channel/{id}
        if m.group(1):
            return m.group(1)
        # custom name /c/ or /user/ or handle @name -> search to resolve
        candidate = m.group(2) or m.group(3) or m.group(4)
        if candidate:
            try:
                resp = youtube.search().list(part='snippet', q=candidate, type='channel', maxResults=1).execute()
                items = resp.get('items', [])
                if items:
                    return items[0]['snippet']['channelId']
            except Exception as e:
                print(f"_resolve_channel_id search error: {e}")
                return None

    # If string starts with @handle
    if s.startswith('@'):
        handle = s[1:]
        try:
            resp = youtube.search().list(part='snippet', q=handle, type='channel', maxResults=1).execute()
            items = resp.get('items', [])
            if items:
                return items[0]['snippet']['channelId']
        except Exception as e:
            print(f"_resolve_channel_id handle search error: {e}")
            return None

    # Fallback: try a search with the raw input (best-effort)
    try:
        resp = youtube.search().list(part='snippet', q=s, type='channel', maxResults=1).execute()
        items = resp.get('items', [])
        if items:
            return items[0]['snippet']['channelId']
    except Exception as e:
        print(f"_resolve_channel_id fallback search error: {e}")

    return None

@app.route('/api/analyze-channel', methods=['POST'])
def analyze_channel():
    """Main endpoint: Analyze channel and generate strategy"""
    data = request.json
    channel_id_input = data.get('channel_id')
    max_videos = data.get('max_videos', 20)

    if not channel_id_input:
        return jsonify({'error': 'channel_id is required'}), 400

    # Resolve URL/handle/custom name to real channel ID
    resolved_channel_id = _resolve_channel_id(channel_id_input)
    if not resolved_channel_id:
        return jsonify({'error': 'Unable to resolve channel ID from input. Provide a channel ID, channel URL, or handle (e.g., @handle).'}), 400

    if not all([data_agent, trend_agent, strategy_agent]):
        return jsonify({'error': 'API keys not configured'}), 500

    try:
        # Step 1: Data Acquisition
        channel_info = data_agent.get_channel_info(resolved_channel_id)
        if 'error' in channel_info:
            return jsonify(channel_info), 404

        videos = data_agent.get_channel_videos(resolved_channel_id, max_videos)
        if not videos:
            return jsonify({'error': 'No videos found'}), 404

        # Step 2: Trend Analysis
        trend_analysis = trend_agent.analyze_performance_patterns(videos)

        # Step 3: Strategy Generation
        strategy = strategy_agent.generate_content_strategy(trend_analysis, channel_info)

        return jsonify({
            'success': True,
            'channel': channel_info,
            'analysis': trend_analysis,
            'strategy': strategy,
            'videos_analyzed': len(videos)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _extract_video_id(video_id_or_url: str) -> str | None:
    """Extract a 11-char YouTube video ID from a URL or return it if already an ID."""
    if not video_id_or_url:
        return None

    vid_raw = video_id_or_url.strip()

    # Remove query string or fragments (e.g. "g8L6-yyJVSs?si=..." or "https://youtu.be/ID?si=...")
    vid = vid_raw.split('?', 1)[0].split('#', 1)[0]

    # Direct 11-char ID after stripping queries
    if re.fullmatch(r'[0-9A-Za-z_-]{11}', vid):
        return vid

    # v= param in full URL
    m = re.search(r'[?&]v=([0-9A-Za-z_-]{11})', vid_raw)
    if m:
        return m.group(1)

    # youtu.be short link, /embed/ or /v/
    m = re.search(r'youtu\.be/([0-9A-Za-z_-]{11})', vid)
    if m:
        return m.group(1)
    m = re.search(r'/embed/([0-9A-Za-z_-]{11})', vid)
    if m:
        return m.group(1)
    m = re.search(r'/v/([0-9A-Za-z_-]{11})', vid)
    if m:
        return m.group(1)

    return None

@app.before_request
def log_request():
    # lightweight request logging to help debug missing routes / payloads
    try:
        print(f"[REQ] {request.method} {request.path} body={request.get_json(silent=True)}")
    except Exception:
        print(f"[REQ] {request.method} {request.path} (no-json)")

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """Analyze a specific video with comments and transcript"""
    data = request.json or {}
    raw_id = data.get('video_id') or data.get('videoUrl') or data.get('url')
    video_id = _extract_video_id(raw_id)
    print(f"analyze_video: raw_id={raw_id} -> video_id={video_id}")

    if not video_id:
        return jsonify({'error': 'video_id is required (or provide a valid YouTube URL/ID)'}), 400

    if not all([data_agent, trend_agent]):
        return jsonify({'error': 'API keys not configured'}), 500

    try:
        # Fetch video details
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return jsonify({'error': 'Video not found'}), 404

        video = video_response['items'][0]
        video_info = {
            'id': video.get('id'),
            'title': video['snippet'].get('title'),
            'views': int(video['statistics'].get('viewCount', 0)),
            'likes': int(video['statistics'].get('likeCount', 0)),
            'comments': int(video['statistics'].get('commentCount', 0))
        }

        # Fetch comments
        comments = data_agent.get_video_comments(video_id, 50)

        # Fetch transcript
        transcript = data_agent.get_video_transcript(video_id)

        # Analyze sentiment
        sentiment = trend_agent.analyze_comment_sentiment(comments, video_info['title'])

        return jsonify({
            'success': True,
            'video': video_info,
            'comments': comments[:10],  # Return top 10
            'sentiment': sentiment,
            'has_transcript': bool(transcript),
            'transcript_preview': transcript[:500] if transcript else None
        })

    except Exception as e:
        print(f"analyze_video error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-channels', methods=['POST'])
def search_channels():
    """Search for channels by keyword"""
    data = request.json
    query = data.get('query')
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    if not youtube:
        return jsonify({'error': 'YouTube API not configured'}), 500
    
    try:
        response = youtube.search().list(
            part='snippet',
            q=query,
            type='channel',
            maxResults=max_results
        ).execute()
        
        channels = []
        for item in response['items']:
            channels.append({
                'id': item['snippet']['channelId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            })
        
        return jsonify({'success': True, 'channels': channels})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-ideas', methods=['POST'])
def generate_ideas():
    """Generate content ideas based on niche"""
    data = request.json
    niche = data.get('niche')
    count = data.get('count', 5)
    
    if not niche:
        return jsonify({'error': 'niche is required'}), 400
    
    if not groq_client:
        return jsonify({'error': 'Groq API not configured'}), 500
    
    try:
        prompt = f"""Generate {count} viral YouTube video ideas for the niche: {niche}

For each idea provide:
1. Video Title (clickable, SEO-optimized)
2. Description (2 sentences)
3. Target Keywords
4. Hook (first 10 seconds)
5. Why it will go viral

Make them trending, data-driven, and actionable."""
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a YouTube content strategy expert specializing in viral content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        return jsonify({
            'success': True,
            'ideas': response.choices[0].message.content,
            'niche': niche
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Multi-Agent YouTube Content Strategist API")
    print(f"📊 YouTube API: {'✅ Configured' if YOUTUBE_API_KEY else '❌ Not configured'}")
    print(f"🤖 Groq API: {'✅ Configured' if GROQ_API_KEY else '❌ Not configured'}")
    
    print("\nEndpoints:")
    print("  POST /api/analyze-channel - Analyze channel and generate strategy")
    print("  POST /api/analyze-video - Deep dive into specific video")
    print("  POST /api/search-channels - Search for channels")
    print("  POST /api/generate-ideas - Generate content ideas by niche")
    print("  GET  /api/health - Health check\n")
    
    app.run(debug=True, port=5000)