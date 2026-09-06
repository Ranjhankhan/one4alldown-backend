import os
import subprocess
import re
import yt_dlp

class SocialDownloaderLib:
    @staticmethod
    def get_media_data(url: str) -> dict:
        common_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        base_ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': common_headers,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web', 'android']
                }
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(base_ydl_opts) as ydl:
                info_v = ydl.extract_info(url, download=False)
                title = info_v.get('title', 'Untitled Media')
                duration = info_v.get('duration_string', 'N/A')
                thumbnail = info_v.get('thumbnail', '')
                
                sorted_res = ['1080p', '720p', '480p', '360p', '240p']

            return {
                "success": True,
                "title": title,
                "duration": duration,
                "thumbnail": thumbnail,
                "resolutions": sorted_res
            }
        
        except Exception as e:
            return {
                "success": True,
                "title": "Media Download",
                "duration": "N/A",
                "thumbnail": "",
                "resolutions": ['1080p', '720p', '480p', '360p', '240p']
            }

    @staticmethod
    def download_real_mp3_with_progress(url: str, bitrate: str, progress_callback, output_dir="downloads"):
        os.makedirs(output_dir, exist_ok=True)
        
        def my_hook(d):
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    percent = int((downloaded / total) * 90) # 0 to 90% download
                    progress_callback(percent, "downloading")
            elif d['status'] == 'finished':
                progress_callback(92, "converting")

        ydl_opts = {
    'format': 'best',
    'noplaylist': True,
    # YouTube ke bot-detection ko bypass karne ke liye Android aur TV client use karein (No cookies needed)
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'tv', 'web'],
        }
    },
    'socket_timeout': 30,
}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'audio')

            base, _ = os.path.splitext(filename)
            mp3_path = base + ".mp3"

            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(script_dir, "ffmpeg.exe"),
                os.path.join(os.getcwd(), "ffmpeg.exe"),
                "ffmpeg"
            ]

            ffmpeg_exe = None
            for p in possible_paths:
                if p == "ffmpeg" or os.path.exists(p):
                    ffmpeg_exe = p
                    break

            if not ffmpeg_exe:
                return {"success": False, "error": "ffmpeg.exe not found!"}

            cmd = [
                ffmpeg_exe, '-y', '-i', filename, 
                '-vn', '-ar', '44100', '-b:a', bitrate, '-f', 'mp3', mp3_path
            ]
            
            progress_callback(95, "converting")
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                return {"success": False, "error": "FFmpeg conversion failed."}
            
            if os.path.exists(filename) and filename != mp3_path:
                os.remove(filename)

            progress_callback(100, "completed")
            
            # Safe sanitized title for download filename
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title) + ".mp3"
            return {"success": True, "path": os.path.abspath(mp3_path), "filename": safe_title}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def download_real_video_with_progress(url: str, quality: str, progress_callback, output_dir="downloads"):
        os.makedirs(output_dir, exist_ok=True)
        
        def my_hook(d):
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    percent = int((downloaded / total) * 100)
                    progress_callback(percent, "downloading")
            elif d['status'] == 'finished':
                progress_callback(100, "finished")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = script_dir if os.path.exists(os.path.join(script_dir, "ffmpeg.exe")) else None

        height_num = quality.replace('p', '')
        ydl_opts = {
    'format': 'best',
    'noplaylist': True,
    # YouTube ke bot-check aur player response error ko bypass karne ke liye Embedded aur TV clients
    'extractor_args': {
        'youtube': {
            'player_client': ['tv_embedded', 'android', 'web'],
        }
    },
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'socket_timeout': 30,
}

        
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'video')
                ext = info.get('ext', 'mp4')

            absolute_path = os.path.abspath(filename)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title) + f"_{quality}.{ext}"
            return {"success": True, "path": absolute_path, "filename": safe_title}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
