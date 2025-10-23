from flask import Flask, render_template, request, send_file, redirect, url_for, flash, after_this_request
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = "secretkey"  # needed for flash messages

# Ensure downloads folder exists
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Path to cookies.txt
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        agree = request.form.get("agree")

        # Check Terms & Conditions
        if not agree:
            flash("You must accept the Terms & Conditions to download.")
            return redirect(url_for("index"))

        # Validate URL
        if not url or not url.strip():
            flash("Please enter a valid video URL.")
            return redirect(url_for("index"))

        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
        }

        # Use cookies.txt if it exists
        if os.path.exists(COOKIES_PATH):
            ydl_opts['cookiefile'] = COOKIES_PATH
        else:
            print("⚠️ Warning: cookies.txt not found — YouTube downloads may fail with 429 error.")

        try:
            # Start download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Check if file exists
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                flash("Download failed: file is empty or unsupported.")
                return redirect(url_for("index"))

            # Delete file after sending
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(filename)
                except Exception as e:
                    print("⚠️ Error deleting file:", e)
                return response

            return send_file(filename, as_attachment=True)

        except yt_dlp.utils.DownloadError as e:
            flash("Download failed: YouTube may be blocking automated downloads. Try again later or update cookies.txt.")
            print("yt-dlp error:", e)
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
            print("General error:", e)
            return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
