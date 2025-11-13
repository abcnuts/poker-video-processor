# 🎯 Poker Video Processor

**Automatically process poker videos from Airtable** - downloads, transcribes, extracts insights, and updates records.

---

## 🚀 What It Does

1. **Polls Airtable** every 5 minutes for videos with Status = "Raw"
2. **Downloads videos** from YouTube, Google Drive, or direct URLs
3. **Extracts audio** using ffmpeg
4. **Transcribes** using OpenAI Whisper
5. **Extracts insights** using GPT-4:
   - Key quotes (tweetable)
   - Core poker philosophy
6. **Updates Airtable** with results and sets Status = "Extracted"

---

## 📋 Prerequisites

- **Python 3.11+**
- **ffmpeg** (for audio extraction)
- **Airtable Personal Access Token** (with read/write access)
- **OpenAI API Key** (for transcription and insights)

---

## 🛠️ Local Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
AIRTABLE_API_KEY=your_personal_access_token
AIRTABLE_BASE_ID=appd81rBXhVWHn2xu
AIRTABLE_TABLE_ID=tblCnNsHMyGjXCXL6
OPENAI_API_KEY=your_openai_api_key
POLL_INTERVAL_SECONDS=300
```

### 3. Run the Service

**Continuous mode** (runs forever, checking every 5 minutes):
```bash
cd src
python main.py
```

**One-shot mode** (process once and exit):
```bash
cd src
python main.py --once
```

---

## ☁️ Deploy to Railway

Railway is a simple platform for hosting Python services. Free tier available.

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login and Initialize

```bash
railway login
railway init
```

### 3. Set Environment Variables

```bash
railway variables set AIRTABLE_API_KEY=your_token
railway variables set AIRTABLE_BASE_ID=appd81rBXhVWHn2xu
railway variables set AIRTABLE_TABLE_ID=tblCnNsHMyGjXCXL6
railway variables set OPENAI_API_KEY=your_key
railway variables set POLL_INTERVAL_SECONDS=300
```

### 4. Create Procfile

Create a file named `Procfile` in the root directory:
```
worker: cd src && python main.py
```

### 5. Deploy

```bash
railway up
```

Your service will now run 24/7 in the cloud!

---

## 🎬 How to Use

### Add a Video to Process

1. Go to your Airtable "Master Content Library"
2. Create a new record:
   - **Content Title**: "My Poker Strategy Video"
   - **Source File/Link**: https://youtube.com/watch?v=...
   - **Status**: "Raw"
   - **Content Type**: "Video"
3. Wait 5 minutes (or run `python main.py --once`)
4. Check the record - it will be updated with:
   - Transcription in "Core Philosophy" field
   - Key quotes in "Key Quotes" field
   - Status changed to "Extracted"

---

## 📁 Project Structure

```
poker-video-processor/
├── src/
│   ├── main.py              # Main service orchestrator
│   ├── video_processor.py   # Video download, transcription, insights
│   └── airtable_client.py   # Airtable integration
├── downloads/               # Temporary video/audio storage
├── logs/                    # Service logs
├── .env                     # Your credentials (DO NOT COMMIT)
├── .env.example            # Template for credentials
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🔧 Troubleshooting

### "No module named 'yt_dlp'"
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### "ffmpeg not found"
Install ffmpeg:
- **Mac**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/

### "Airtable API Error"
- Check your Personal Access Token has correct scopes:
  - `data.records:read`
  - `data.records:write`
  - `schema.bases:read`
- Verify Base ID and Table ID are correct

### Videos Not Processing
- Check logs in `logs/processor.log`
- Verify video URL is accessible
- Make sure Status is exactly "Raw" (case-sensitive)

---

## 🎨 Customization

### Change Poll Interval
Edit `.env`:
```
POLL_INTERVAL_SECONDS=600  # Check every 10 minutes
```

### Modify Insight Extraction
Edit `src/video_processor.py`, method `_extract_insights()`:
- Change the prompt
- Add more fields
- Use different AI models

### Add More Status Values
Edit `src/airtable_client.py` to handle additional statuses like "Published", "Monetized", etc.

---

## 💰 Cost Estimates

**OpenAI API Costs** (per video):
- Whisper transcription: ~$0.006 per minute of audio
- GPT-4 Mini insights: ~$0.01 per video
- **Total: ~$0.05 per 5-minute video**

**Railway Hosting**:
- Free tier: $5 credit/month (plenty for this service)
- Paid: $5/month for 24/7 uptime

---

## 🚦 Next Steps

1. **Test locally** with one video
2. **Deploy to Railway** for 24/7 automation
3. **Build Workflow 2**: Content Derivative Generator
4. **Add social media distribution**
5. **Track performance metrics**

---

## 📞 Support

Check logs first:
```bash
tail -f logs/processor.log
```

Common issues are usually:
- Missing credentials
- Wrong Airtable field names
- Video URL not accessible

---

**Built with ❤️ for poker content creators**
