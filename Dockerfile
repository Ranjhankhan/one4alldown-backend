FROM python:3.9-slim

# Linux ke liye FFmpeg install karna aur system dependencies update rakhna
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# yt-dlp aur baqi libraries ko hamesha latest version par update karne ke liye --upgrade use kiya hai
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir --upgrade yt-dlp

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
