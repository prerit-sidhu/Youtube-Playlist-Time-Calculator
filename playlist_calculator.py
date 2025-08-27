#!/usr/bin/env python3
"""
YouTube Playlist Duration Calculator - GUI Application

A beautiful desktop application to calculate YouTube playlist durations
with modern UI design and comprehensive features.

Requirements:
    pip install google-api-python-client isodate python-dotenv pillow

Setup:
    1. Get a YouTube Data API v3 key from Google Cloud Console
    2. Create a .env file with: YOUTUBE_API_KEY=your_api_key_here
    3. Run the application
"""

import os
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, parse_qs
import webbrowser
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import isodate
    from dotenv import load_dotenv
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install google-api-python-client isodate python-dotenv pillow")
    sys.exit(1)

# Load environment variables
load_dotenv()

class ModernStyle:
    """Modern color scheme and styling constants."""
    # Colors
    PRIMARY = "#2563eb"      # Blue
    PRIMARY_DARK = "#1d4ed8"
    SUCCESS = "#059669"      # Green
    WARNING = "#d97706"      # Orange
    ERROR = "#dc2626"        # Red
    BACKGROUND = "#f8fafc"   # Light gray
    SURFACE = "#ffffff"      # White
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    BORDER = "#e2e8f0"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    TITLE_SIZE = 16
    SUBTITLE_SIZE = 12
    BODY_SIZE = 10
    SMALL_SIZE = 9


class YouTubePlaylistCalculator:
    """YouTube Playlist Duration Calculator backend."""
    
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_playlist_id(self, url_or_id: str) -> str:
        """Extract playlist ID from various YouTube URL formats."""
        if re.match(r'^[A-Za-z0-9_-]{18,}$', url_or_id) and not url_or_id.startswith('http'):
            return url_or_id
        
        try:
            parsed_url = urlparse(url_or_id)
            if parsed_url.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']:
                query_params = parse_qs(parsed_url.query)
                if 'list' in query_params:
                    return query_params['list'][0]
        except Exception:
            pass
        
        raise ValueError(f"Invalid playlist URL or ID: {url_or_id}")
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """Get basic playlist information."""
        request = self.youtube.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        )
        response = request.execute()
        
        if not response['items']:
            raise ValueError(f"Playlist not found: {playlist_id}")
        
        playlist = response['items'][0]
        return {
            'title': playlist['snippet']['title'],
            'description': playlist['snippet'].get('description', ''),
            'channel': playlist['snippet']['channelTitle'],
            'item_count': playlist['contentDetails']['itemCount'],
            'published': playlist['snippet']['publishedAt'],
            'thumbnail': playlist['snippet']['thumbnails'].get('medium', {}).get('url', '')
        }
    
    def get_playlist_videos(self, playlist_id: str, progress_callback=None) -> List[str]:
        """Retrieve all video IDs from a playlist."""
        videos = []
        next_page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            if progress_callback:
                progress_callback(f"Fetching videos - Page {page_count}")
            
            request = self.youtube.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                video_title = item['snippet']['title']
                
                if video_title not in ['Deleted video', 'Private video']:
                    videos.append(video_id)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return videos
    
    def get_video_durations(self, video_ids: List[str], progress_callback=None) -> Tuple[List[float], Dict]:
        """Get durations for all videos."""
        durations = []
        stats = {
            'total_videos': len(video_ids),
            'processed_videos': 0,
            'failed_videos': 0
        }
        
        total_batches = (len(video_ids) - 1) // 50 + 1
        
        for i in range(0, len(video_ids), 50):
            batch_num = i // 50 + 1
            if progress_callback:
                progress_callback(f"Processing durations - Batch {batch_num}/{total_batches}")
            
            batch = video_ids[i:i+50]
            request = self.youtube.videos().list(
                part='contentDetails',
                id=','.join(batch)
            )
            response = request.execute()
            
            video_data = {item['id']: item for item in response['items']}
            
            for video_id in batch:
                if video_id in video_data:
                    try:
                        duration_iso = video_data[video_id]['contentDetails']['duration']
                        duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
                        durations.append(duration_seconds)
                        stats['processed_videos'] += 1
                    except Exception:
                        stats['failed_videos'] += 1
                else:
                    stats['failed_videos'] += 1
        
        return durations, stats
    
    def format_duration(self, total_seconds: float) -> str:
        """Format duration into human-readable format."""
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def calculate_playlist_duration(self, playlist_input: str, progress_callback=None) -> Dict:
        """Calculate playlist duration with progress updates."""
        try:
            if progress_callback:
                progress_callback("Extracting playlist ID...")
            
            playlist_id = self.extract_playlist_id(playlist_input)
            
            if progress_callback:
                progress_callback("Getting playlist information...")
            
            playlist_info = self.get_playlist_info(playlist_id)
            
            if progress_callback:
                progress_callback("Fetching video list...")
            
            video_ids = self.get_playlist_videos(playlist_id, progress_callback)
            
            if not video_ids:
                return {'error': 'No accessible videos found in playlist'}
            
            durations, stats = self.get_video_durations(video_ids, progress_callback)
            
            if not durations:
                return {'error': 'No video durations could be retrieved'}
            
            total_seconds = sum(durations)
            
            results = {
                'playlist_info': playlist_info,
                'stats': stats,
                'total_duration_seconds': total_seconds,
                'total_duration_formatted': self.format_duration(total_seconds),
                'average_duration': self.format_duration(total_seconds / len(durations)),
                'longest_video': self.format_duration(max(durations)),
                'shortest_video': self.format_duration(min(durations)),
                'median_duration': self.format_duration(sorted(durations)[len(durations) // 2]),
                'success': True
            }
            
            if progress_callback:
                progress_callback("Calculation complete!")
            
            return results
            
        except Exception as e:
            return {'error': str(e), 'success': False}


class PlaylistCalculatorApp:
    """Main GUI Application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Playlist Duration Calculator")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Configure style
        self.setup_styles()
        
        # Initialize calculator
        self.calculator = None
        self.setup_api_key()
        
        # Create GUI
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure modern styling."""
        style = ttk.Style()
        
        # Configure colors
        self.root.configure(bg=ModernStyle.BACKGROUND)
        
        # Configure ttk styles
        style.configure("Title.TLabel", 
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.TITLE_SIZE, "bold"),
                       background=ModernStyle.BACKGROUND,
                       foreground=ModernStyle.TEXT_PRIMARY)
        
        style.configure("Subtitle.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.SUBTITLE_SIZE),
                       background=ModernStyle.BACKGROUND,
                       foreground=ModernStyle.TEXT_SECONDARY)
        
        style.configure("Primary.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE, "bold"))
        
        style.configure("Success.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE),
                       background=ModernStyle.BACKGROUND,
                       foreground=ModernStyle.SUCCESS)
        
        style.configure("Error.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE),
                       background=ModernStyle.BACKGROUND,
                       foreground=ModernStyle.ERROR)
    
    def setup_api_key(self):
        """Initialize API key and calculator."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            self.show_api_key_dialog()
        else:
            try:
                self.calculator = YouTubePlaylistCalculator(api_key)
            except Exception as e:
                messagebox.showerror("API Error", f"Failed to initialize YouTube API: {e}")
    
    def show_api_key_dialog(self):
        """Show API key input dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("YouTube API Key Required")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.configure(bg=ModernStyle.BACKGROUND)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Content frame
        content_frame = tk.Frame(dialog, bg=ModernStyle.BACKGROUND, padx=30, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(content_frame, text="YouTube API Key Required", style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = """To use this application, you need a YouTube Data API v3 key.

1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create API credentials (API Key)
5. Enter your API key below"""
        
        instruction_label = ttk.Label(content_frame, text=instructions, style="Subtitle.TLabel", justify=tk.LEFT)
        instruction_label.pack(pady=(0, 20), anchor=tk.W)
        
        # API key input
        api_key_label = ttk.Label(content_frame, text="API Key:", style="Subtitle.TLabel")
        api_key_label.pack(anchor=tk.W)
        
        api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(content_frame, textvariable=api_key_var, font=(ModernStyle.FONT_FAMILY, 10), width=50)
        api_key_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=ModernStyle.BACKGROUND)
        button_frame.pack(fill=tk.X)
        
        def save_api_key():
            api_key = api_key_var.get().strip()
            if not api_key:
                messagebox.showwarning("Warning", "Please enter an API key")
                return
            
            try:
                self.calculator = YouTubePlaylistCalculator(api_key)
                # Save to .env file
                with open('.env', 'w') as f:
                    f.write(f'YOUTUBE_API_KEY={api_key}\n')
                dialog.destroy()
                messagebox.showinfo("Success", "API key saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid API key: {e}")
        
        def open_console():
            webbrowser.open("https://console.cloud.google.com/apis/api/youtube.googleapis.com")
        
        ttk.Button(button_frame, text="Open Google Console", command=open_console).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save API Key", command=save_api_key, style="Primary.TButton").pack(side=tk.RIGHT)
        
        api_key_entry.focus()
    
    def create_widgets(self):
        """Create main application widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=ModernStyle.BACKGROUND, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create header section."""
        header_frame = tk.Frame(parent, bg=ModernStyle.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🎬 YouTube Playlist Duration Calculator", style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Calculate total duration of any YouTube playlist", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(5, 0))
    
    def create_input_section(self, parent):
        """Create input section."""
        input_frame = tk.LabelFrame(parent, text="Playlist Input", bg=ModernStyle.SURFACE, 
                                   relief=tk.FLAT, bd=1, padx=20, pady=15,
                                   font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE, "bold"))
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # URL input
        url_label = ttk.Label(input_frame, text="Enter YouTube Playlist URL or ID:", style="Subtitle.TLabel")
        url_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(input_frame, textvariable=self.url_var, 
                             font=(ModernStyle.FONT_FAMILY, 11), width=70)
        url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Example
        example_label = ttk.Label(input_frame, 
                                 text="Example: https://www.youtube.com/playlist?list=PLxxxxxx", 
                                 style="Subtitle.TLabel")
        example_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Calculate button
        self.calculate_btn = ttk.Button(input_frame, text="🔍 Calculate Duration", 
                                       command=self.start_calculation, style="Primary.TButton")
        self.calculate_btn.pack()
        
        # Bind Enter key
        url_entry.bind('<Return>', lambda e: self.start_calculation())
        url_entry.focus()
    
    def create_progress_section(self, parent):
        """Create progress section."""
        self.progress_frame = tk.LabelFrame(parent, text="Progress", bg=ModernStyle.SURFACE,
                                           relief=tk.FLAT, bd=1, padx=20, pady=15,
                                           font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE, "bold"))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to calculate...")
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress_var, style="Subtitle.TLabel")
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
    
    def create_results_section(self, parent):
        """Create results section."""
        self.results_frame = tk.LabelFrame(parent, text="Results", bg=ModernStyle.SURFACE,
                                          relief=tk.FLAT, bd=1, padx=20, pady=15,
                                          font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE, "bold"))
        
        # Results will be created dynamically
        self.results_content = tk.Frame(self.results_frame, bg=ModernStyle.SURFACE)
    
    def create_footer(self, parent):
        """Create footer section."""
        footer_frame = tk.Frame(parent, bg=ModernStyle.BACKGROUND)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        footer_text = "Made with ❤️ for YouTube playlist analysis"
        footer_label = ttk.Label(footer_frame, text=footer_text, style="Subtitle.TLabel")
        footer_label.pack()
    
    def start_calculation(self):
        """Start playlist calculation in background thread."""
        if not self.calculator:
            messagebox.showerror("Error", "YouTube API not initialized. Please set up your API key.")
            return
        
        playlist_input = self.url_var.get().strip()
        if not playlist_input:
            messagebox.showwarning("Warning", "Please enter a playlist URL or ID")
            return
        
        # Show progress
        self.show_progress()
        
        # Disable button
        self.calculate_btn.configure(state='disabled', text="Calculating...")
        
        # Start calculation in thread
        thread = threading.Thread(target=self.calculate_duration, args=(playlist_input,))
        thread.daemon = True
        thread.start()
    
    def show_progress(self):
        """Show progress section."""
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        self.progress_label.pack(pady=(0, 10))
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.start(10)
    
    def hide_progress(self):
        """Hide progress section."""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
    
    def update_progress(self, message):
        """Update progress message."""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def calculate_duration(self, playlist_input):
        """Calculate duration (runs in background thread)."""
        try:
            results = self.calculator.calculate_playlist_duration(playlist_input, self.update_progress)
            self.root.after(0, self.show_results, results)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def show_results(self, results):
        """Display calculation results."""
        self.hide_progress()
        self.calculate_btn.configure(state='normal', text="🔍 Calculate Duration")
        
        if not results.get('success', False):
            self.show_error(results.get('error', 'Unknown error'))
            return
        
        # Clear previous results
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Show results frame
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.results_content.pack(fill=tk.BOTH, expand=True)
        
        # Playlist info
        info = results['playlist_info']
        stats = results['stats']
        
        # Title and channel
        title_label = ttk.Label(self.results_content, text=f"📋 {info['title']}", 
                               font=(ModernStyle.FONT_FAMILY, ModernStyle.SUBTITLE_SIZE, "bold"),
                               background=ModernStyle.SURFACE, foreground=ModernStyle.TEXT_PRIMARY)
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        channel_label = ttk.Label(self.results_content, text=f"👤 {info['channel']}", 
                                 style="Subtitle.TLabel")
        channel_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Main duration result
        duration_frame = tk.Frame(self.results_content, bg="#f0f9ff", relief=tk.FLAT, bd=1, padx=20, pady=15)
        duration_frame.pack(fill=tk.X, pady=(0, 15))
        
        duration_title = ttk.Label(duration_frame, text="⏱️ Total Duration", 
                                  font=(ModernStyle.FONT_FAMILY, ModernStyle.SUBTITLE_SIZE, "bold"),
                                  background="#f0f9ff", foreground=ModernStyle.PRIMARY)
        duration_title.pack()
        
        duration_value = ttk.Label(duration_frame, text=results['total_duration_formatted'],
                                  font=(ModernStyle.FONT_FAMILY, 18, "bold"),
                                  background="#f0f9ff", foreground=ModernStyle.PRIMARY)
        duration_value.pack(pady=(5, 0))
        
        seconds_label = ttk.Label(duration_frame, text=f"{results['total_duration_seconds']:,.0f} seconds",
                                 font=(ModernStyle.FONT_FAMILY, ModernStyle.SMALL_SIZE),
                                 background="#f0f9ff", foreground=ModernStyle.TEXT_SECONDARY)
        seconds_label.pack()
        
        # Statistics grid
        stats_frame = tk.Frame(self.results_content, bg=ModernStyle.SURFACE)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create 2x2 grid
        stats_data = [
            ("📊 Videos Processed", f"{stats['processed_videos']:,}"),
            ("📈 Average Duration", results['average_duration']),
            ("⏰ Longest Video", results['longest_video']),
            ("⏱️ Shortest Video", results['shortest_video'])
        ]
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_frame, bg="#f8fafc", relief=tk.FLAT, bd=1, padx=15, pady=10)
            stat_frame.grid(row=row, column=col, sticky="ew", padx=(0, 10), pady=(0, 10))
            
            stat_label = ttk.Label(stat_frame, text=label, 
                                  font=(ModernStyle.FONT_FAMILY, ModernStyle.SMALL_SIZE),
                                  background="#f8fafc", foreground=ModernStyle.TEXT_SECONDARY)
            stat_label.pack()
            
            stat_value = ttk.Label(stat_frame, text=value,
                                  font=(ModernStyle.FONT_FAMILY, ModernStyle.BODY_SIZE, "bold"),
                                  background="#f8fafc", foreground=ModernStyle.TEXT_PRIMARY)
            stat_value.pack(pady=(2, 0))
        
        # Configure grid weights
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        # Export button
        export_btn = ttk.Button(self.results_content, text="💾 Export Results", 
                               command=lambda: self.export_results(results))
        export_btn.pack(pady=(10, 0))
    
    def show_error(self, error_message):
        """Display error message."""
        self.hide_progress()
        self.calculate_btn.configure(state='normal', text="🔍 Calculate Duration")
        
        messagebox.showerror("Error", f"Failed to calculate playlist duration:\n\n{error_message}")
    
    def export_results(self, results):
        """Export results to text file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Results"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                info = results['playlist_info']
                stats = results['stats']
                
                f.write("YouTube Playlist Duration Calculator - Results\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Playlist: {info['title']}\n")
                f.write(f"Channel: {info['channel']}\n")
                f.write(f"Total Videos: {info['item_count']}\n")
                f.write(f"Processed Videos: {stats['processed_videos']}\n")
                f.write(f"Failed Videos: {stats['failed_videos']}\n\n")
                f.write(f"Total Duration: {results['total_duration_formatted']}\n")
                f.write(f"Total Seconds: {results['total_duration_seconds']:,.0f}\n\n")
                f.write("Statistics:\n")
                f.write(f"  Average Duration: {results['average_duration']}\n")
                f.write(f"  Longest Video: {results['longest_video']}\n")
                f.write(f"  Shortest Video: {results['shortest_video']}\n")
                f.write(f"  Median Duration: {results['median_duration']}\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {e}")
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function."""
    app = PlaylistCalculatorApp()
    app.run()


if __name__ == '__main__':
    main()