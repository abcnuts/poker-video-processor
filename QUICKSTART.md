# ⚡ QUICK START - Get Running in 5 Minutes

**For people who just want it to work.**

---

## 🎯 Goal

Add a video to Airtable → Wait 5 minutes → Get transcription + insights automatically.

---

## ✅ Step 1: Test It RIGHT NOW (Local)

```bash
cd /home/ubuntu/poker-video-processor
source venv/bin/activate
cd src
python main.py --once
```

**What happens:**
- Checks your Airtable for videos with Status = "Raw"
- Processes the YouTube Short you added earlier
- Updates Airtable with results
- Exits

**Time: 1-2 minutes**

---

## ✅ Step 2: Run It Forever (Local)

```bash
cd /home/ubuntu/poker-video-processor
source venv/bin/activate
cd src
python main.py
```

**What happens:**
- Runs continuously
- Checks every 5 minutes for new videos
- Press Ctrl+C to stop

**Keep this terminal open while working.**

---

## ✅ Step 3: Deploy to Cloud (Railway)

**Why:** So it runs 24/7 even when your computer is off.

### A. Install Railway CLI
```bash
npm install -g @railway/cli
```

### B. Login
```bash
railway login
```

### C. Deploy
```bash
cd /home/ubuntu/poker-video-processor
railway init
railway up
```

### D. Add Environment Variables

Go to Railway dashboard → Your project → Variables

Add these:
```
AIRTABLE_API_KEY = [your token]
AIRTABLE_BASE_ID = appd81rBXhVWHn2xu
AIRTABLE_TABLE_ID = tblCnNsHMyGjXCXL6
OPENAI_API_KEY = [your OpenAI key]
POLL_INTERVAL_SECONDS = 300
```

**Done. It's now running 24/7.**

---

## 🎬 How to Use It

### Add a Video

1. Open Airtable: https://airtable.com/appd81rBXhVWHn2xu/tblCnNsHMyGjXCXL6
2. Click "+ New Record"
3. Fill in:
   - **Content Title**: Whatever you want
   - **Source File/Link**: Your YouTube URL
   - **Status**: Raw
   - **Content Type**: Video
4. Wait 5 minutes
5. Refresh - it's processed!

---

## 🔍 Check If It's Working

### Local:
Watch the terminal output. You'll see:
```
🔍 Checking for pending videos...
📹 Found 1 videos to process
Processing: Your Video Title
✅ Successfully processed
```

### Railway:
Go to Railway dashboard → Your project → Deployments → Logs

---

## 🚨 If Something Breaks

### Error: "No module named 'yt_dlp'"
```bash
source venv/bin/activate
```

### Error: "ffmpeg not found"
**Mac:**
```bash
brew install ffmpeg
```

**Ubuntu:**
```bash
sudo apt install ffmpeg
```

### Error: "Airtable API Error"
Check your token at: https://airtable.com/create/tokens

Make sure it has:
- ✅ data.records:read
- ✅ data.records:write
- ✅ schema.bases:read

---

## 💡 Pro Tips

**Process immediately instead of waiting 5 minutes:**
```bash
python main.py --once
```

**Change check interval to 1 minute:**
Edit `.env`:
```
POLL_INTERVAL_SECONDS=60
```

**See detailed logs:**
```bash
tail -f ../logs/processor.log
```

---

## 🎯 What's Next?

Once this is working:
1. ✅ **You have automated video processing**
2. 🔜 Build content derivative generator (turn 1 video → 20 posts)
3. 🔜 Add social media distribution
4. 🔜 Track performance metrics

**But first: Make sure this works with 2-3 videos.**

---

**Questions? Check the full README.md**
