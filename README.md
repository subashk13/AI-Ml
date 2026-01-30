**Create & activate virtual environment (recommended)**

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```
3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> If `requirements.txt` is missing, install manually:

```bash
pip install flask openai torch transformers==4.36.2 faster-whisper pydub sentencepiece
```


4. **Set OpenAI API Key**

```bash
set OPENAI_API_KEY="your_api_key_here"   # Windows
export OPENAI_API_KEY="your_api_key_here" # Linux / Mac
```

---

## Running the App

```bash
python main.py
```

Open your browser at:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## Project Structure

```
Meeting Summarizer/
├─ main.py             # Flask app entry
├─ templates/          # HTML files
├─ static/             # CSS & JS
├─ uploads/            # Uploaded audio files
├─ requirements.txt    # Python dependencies
```

---

## Notes / Troubleshooting

* `FutureWarning` from torch / transformers → **Safe to ignore**
* If you see `ModuleNotFoundError`, make sure your venv is active and dependencies installed
* Audio not working → likely FFmpeg PATH issue

---

## License

MIT License

---

Enjoy summarizing your meetings! 🚀

```

---

If you want, I can also **create a shorter “copy-paste friendly” version** for your friend that skips advanced troubleshooting and just works on Windows.  

Do you want me to do that?
```
