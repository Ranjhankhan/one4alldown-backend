import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from social_dl_lib import SocialDownloaderLib
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "One4Alldown Backend is active and running!"}

@app.get("/download")
def download_info(url: str):
    data = SocialDownloaderLib.get_media_data(url)
    return data

@app.get("/convert-stream")
def convert_stream(url: str, bitrate: str = "128k"):
    try:
        def dummy_progress(percent, status):
            pass
        
        result = SocialDownloaderLib.download_real_mp3_with_progress(url, bitrate, dummy_progress)
        
        if not result.get("success"):
            return JSONResponse(content={"success": False, "error": result.get("error")})
        
        file_path = result["path"]
        filename = result["filename"]
        
        if not os.path.exists(file_path):
            return JSONResponse(content={"success": False, "error": "File not found."})
            
        encoded_filename = urllib.parse.quote(filename)
        return FileResponse(
            path=file_path, 
            filename=filename, 
            media_type='audio/mpeg',
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

@app.get("/download-video")
def download_video(url: str, quality: str = "720p"):
    try:
        def dummy_progress(percent, status):
            pass
        
        result = SocialDownloaderLib.download_real_video_with_progress(url, quality, dummy_progress)
        
        if not result.get("success"):
            return JSONResponse(content={"success": False, "error": result.get("error")})
        
        file_path = result["path"]
        filename = result["filename"]
        
        if not os.path.exists(file_path):
            return JSONResponse(content={"success": False, "error": "Video file not found on disk."})
            
        encoded_filename = urllib.parse.quote(filename)
        return FileResponse(
            path=file_path, 
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
        
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
