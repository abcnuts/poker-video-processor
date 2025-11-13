# 🎯 AssemblyAI Setup Guide

**Get premium transcription with auto-chapters and speaker detection.**

---

## Why AssemblyAI?

**Without AssemblyAI:**
- ✅ System still works perfectly
- ✅ Handles all content types
- ❌ Large files take longer (chunking)
- ❌ No auto-chapter detection
- ❌ No speaker identification

**With AssemblyAI:**
- ✅ Faster processing for long content
- ✅ **Auto-chapter detection** (perfect for courses)
- ✅ **Speaker labels** (great for podcasts/interviews)
- ✅ Higher transcription accuracy
- ✅ Automatic for files >100MB or >1 hour

---

## 💰 Cost Comparison

### OpenAI Whisper (Default):
- $0.006 per minute
- 1 hour = $0.36
- 3 hours = $1.08

### AssemblyAI (Premium):
- $0.015 per minute
- 1 hour = $0.90
- 3 hours = $2.70

**Extra cost: ~$0.50/hour**

**What you get:**
- Auto-chapters with timestamps
- Speaker identification
- Higher accuracy
- Faster processing

---

## 🚀 Setup (5 Minutes)

### Step 1: Create Account

Go to: https://www.assemblyai.com/

Click "Sign Up" (free tier available)

### Step 2: Get API Key

1. Log in to dashboard
2. Go to "API Keys" section
3. Copy your API key (starts with `your_api_key_here`)

### Step 3: Add to Your Service

**Option A: Environment Variable (Recommended)**
```bash
cd /home/ubuntu/poker-video-processor
nano .env
```

Add this line:
```
ASSEMBLYAI_API_KEY=your_api_key_here
```

Save and exit (Ctrl+X, Y, Enter)

**Option B: Railway Deployment**
```bash
railway variables set ASSEMBLYAI_API_KEY=your_api_key_here
```

### Step 4: Restart Service

```bash
cd /home/ubuntu/poker-video-processor
source venv/bin/activate
cd src
python main.py --once
```

---

## ✅ Verify It's Working

**Check the logs:**
```bash
tail -f ../logs/processor.log
```

**Look for:**
```
AssemblyAI service initialized
Using AssemblyAI for 90.5 minute audio
Detected 8 chapters
```

**If you see:**
```
AssemblyAI API key not found - service disabled
```

Then the key isn't set correctly. Double-check step 3.

---

## 🎯 When AssemblyAI is Used

**Automatically used for:**
- Files over 100MB
- Audio/video over 1 hour
- When you want chapters

**Not used for:**
- Documents (no transcription needed)
- Short videos (<1 hour)
- Files under 100MB

**You don't choose - the system decides automatically.**

---

## 📊 Free Tier Limits

AssemblyAI free tier includes:
- **5 hours** of transcription per month
- All features (chapters, speakers, etc.)

**After free tier:**
- Pay-as-you-go: $0.00025 per second ($0.015/min)
- No monthly minimums
- Only pay for what you use

---

## 🎬 Example Output with Chapters

**Input:** 90-minute poker strategy video

**Output:**
```
TRANSCRIPTION:
[Full transcription text...]

--- CHAPTERS ---

1. [00:00] Introduction to GTO Strategy
   Overview of game theory optimal play and why it matters

2. [15:30] Pre-Flop Ranges
   Detailed breakdown of opening ranges by position

3. [32:15] Post-Flop Decision Trees
   How to navigate common board textures

4. [58:00] River Play and Bluffing
   When to bluff and how to size your bets

5. [75:20] Live Tells and Adjustments
   Reading opponents in live poker games
```

**Perfect for:**
- Course modules
- YouTube chapters
- Podcast show notes
- Content repurposing

---

## 🔧 Advanced Configuration

### Force AssemblyAI for All Content

Edit `unified_processor.py`:
```python
# Always use AssemblyAI (ignore size/duration)
if self.assemblyai.enabled:
    transcription = self._transcribe_with_assemblyai(audio_path, duration)
```

### Disable Chapter Detection

Edit `unified_processor.py`:
```python
# Disable chapters
result = self.assemblyai.transcribe(audio_path, detect_chapters=False)
```

### Enable Speaker Detection

Edit `unified_processor.py`:
```python
# Enable speakers
result = self.assemblyai.transcribe(
    audio_path, 
    detect_chapters=True,
    detect_speakers=True  # Add this
)
```

---

## 🚨 Troubleshooting

### "AssemblyAI service not enabled"
- API key not set in .env file
- Check spelling: `ASSEMBLYAI_API_KEY`
- Restart the service after adding key

### "Transcription failed: insufficient credits"
- Free tier limit reached (5 hours/month)
- Add payment method in AssemblyAI dashboard
- Or wait until next month

### "Service falls back to chunking"
- AssemblyAI had an error
- System automatically uses chunk & stitch instead
- Check AssemblyAI dashboard for status

---

## 💡 Recommendation

**Start without AssemblyAI:**
1. Test the system with default settings
2. Process 10-20 pieces of content
3. See if you need chapters/speakers

**Add AssemblyAI when:**
- You're processing lots of long content (>1 hour)
- You want auto-chapters for courses
- You need speaker labels for podcasts
- You're willing to pay ~$0.50/hour extra

**For most users:**
- Default chunking works great
- Only add AssemblyAI if you need the premium features
- The system works perfectly either way

---

## 📞 Support

**AssemblyAI Issues:**
- Dashboard: https://www.assemblyai.com/dashboard
- Docs: https://www.assemblyai.com/docs
- Support: support@assemblyai.com

**System Issues:**
- Check logs: `tail -f logs/processor.log`
- Verify API key is set correctly
- System will fall back to chunking if AssemblyAI fails

---

**AssemblyAI is optional but powerful. Add it when you're ready.**
