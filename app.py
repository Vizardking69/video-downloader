from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = "secretkey"  # needed for flash messages

# Ensure downloads folder exists
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        agree = request.form.get("agree")

        # Check if Terms & Conditions are accepted
        if not agree:
            flash("You must accept the Terms & Conditions to download.")
            return redirect(url_for("index"))

        # Check if URL is provided
        if not url:
            flash("Please enter a valid video URL.")
            return redirect(url_for("index"))

        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # download best quality
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,                     # avoid playlists
            'quiet': True,                          # minimal console output
            'merge_output_format': 'mp4',           # merge video+audio into mp4
        }

        try:
            # Start download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # Check if file exists and has size
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                flash("Download failed: The downloaded file is empty or not supported.")
                return redirect(url_for("index"))

            return send_file(filename, as_attachment=True)
        
        except yt_dlp.utils.DownloadError as e:
            flash(f"Download failed: {str(e)}")
            return redirect(url_for("index"))
        
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    # Use 0.0.0.0 to be accessible externally (needed for Render)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
