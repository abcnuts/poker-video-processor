# 🚂 Railway Deployment Guide

**Deploy your poker video processor to run 24/7 in the cloud.**

---

## 🎯 What You'll Get

**After deployment:**
- ✅ Service runs 24/7 automatically
- ✅ Checks Airtable every 5 minutes
- ✅ Processes new content immediately
- ✅ No computer needed
- ✅ Works while you sleep

---

## 📋 Prerequisites

1. ✅ Railway account created (you have this)
2. ✅ GitHub account (for code hosting)
3. ⚠️ Code pushed to GitHub (we'll do this)

---

## 🚀 Deployment Steps

### **Step 1: Push Code to GitHub**

**Option A: Via GitHub Web Interface** (Easiest)

1. Go to: https://github.com/new
2. Create new repository: `poker-video-processor`
3. Make it **Private** (keep your tokens safe)
4. Don't initialize with README
5. Click "Create repository"

**Then upload your code:**
1. Download the zip file I gave you
2. Extract it
3. Go to your GitHub repo
4. Click "uploading an existing file"
5. Drag the entire `poker-video-processor` folder
6. Commit

---

**Option B: Via Git Command Line** (If you have Git installed)

```bash
cd /path/to/poker-video-processor

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - poker video processor v3"

# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/poker-video-processor.git

# Push
git push -u origin main
```

---

### **Step 2: Connect Railway to GitHub**

1. Go to your Railway project dashboard
2. Click "New Service" or "Deploy"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your `poker-video-processor` repository
6. Click "Deploy"

Railway will automatically:
- Detect it's a Python project
- Install dependencies from `requirements.txt`
- Use the `Procfile` to start the service

---

### **Step 3: Add Environment Variables**

**In Railway dashboard:**

1. Click on your deployed service
2. Go to "Variables" tab
3. Click "Add Variable"

**Add these variables:**

```
AIRTABLE_API_KEY=pat5n21FNol9aZo21.72ad91cc4f15dd0b12a2501bd11a8a41512eb7c60a9272591d5ad96ea068f2b5

AIRTABLE_BASE_ID=appd81rBXhVWHn2xu

AIRTABLE_TABLE_ID=tblCnNsHMyGjXCXL6

OPENAI_API_KEY=<your_openai_key>

POLL_INTERVAL_SECONDS=300
```

**Optional (for premium features):**
```
ASSEMBLYAI_API_KEY=<your_assemblyai_key>
```

**Important:** Replace `<your_openai_key>` with your actual OpenAI API key

---

### **Step 4: Deploy and Monitor**

**Railway will automatically:**
1. Build your project
2. Install dependencies
3. Start the service
4. Show you logs

**Check the logs:**
- Click "Deployments" tab
- Click on the latest deployment
- View logs in real-time

**Look for:**
```
✅ Airtable client initialized
✅ Unified processor initialized
🔄 Starting content processor...
Checking for new content...
```

---

## 🎯 Verify It's Working

### **Test 1: Add Content to Airtable**

1. Go to your Master Content Library
2. Add a new record:
   - **Source File/Link:** Any YouTube URL
   - **Status:** Raw
   - **Content Type:** Video

3. Wait 5 minutes

4. Check if:
   - Status changed to "Extracted"
   - Core Philosophy filled in
   - Key Quotes filled in

### **Test 2: Check Railway Logs**

Look for:
```
Found 1 pending videos
Processing: <your video URL>
✅ Downloaded: ...
✅ Transcribed: ...
✅ Updated Airtable
```

---

## 💰 Railway Pricing

### **Free Tier:**
- $5 of credits per month
- Enough for testing
- No credit card required

### **Paid Usage:**
- ~$5-10/month for your use case
- Pay only for what you use
- Includes:
  - 24/7 uptime
  - Automatic restarts
  - Logs and monitoring

**To add payment method:**
1. Go to Railway dashboard
2. Click your profile
3. Go to "Billing"
4. Add credit card

---

## 🔧 Troubleshooting

### **"Build failed"**
- Check logs for error message
- Usually missing dependency
- Make sure `requirements.txt` is complete

### **"Service keeps restarting"**
- Check environment variables are set
- Verify API keys are correct
- Look at logs for error messages

### **"No content being processed"**
- Check Airtable has records with Status = "Raw"
- Verify AIRTABLE_API_KEY has correct permissions
- Check Railway logs for errors

### **"Out of credits"**
- Add payment method in Railway dashboard
- Or wait until next month for free tier reset

---

## 📊 Monitoring Your Service

### **Railway Dashboard:**
- **Deployments:** See build history
- **Logs:** Real-time service logs
- **Metrics:** CPU, memory, network usage
- **Variables:** Manage environment variables

### **Airtable:**
- Check "Last Modified" timestamps
- Count records with Status = "Extracted"
- Review Core Philosophy and Key Quotes fields

### **Cost Tracking:**
- Railway dashboard shows usage
- Typical cost: $5-10/month
- Scales with processing volume

---

## 🎯 What Happens After Deployment

**Your service will:**

```
Every 5 minutes:
1. Wake up
2. Check Airtable for Status = "Raw"
3. Process any new content:
   - Download video/audio
   - Transcribe
   - Extract insights
   - Update Airtable
4. Sleep for 5 minutes
5. Repeat forever
```

**You just:**
1. Add content to Airtable
2. Wait 5 minutes
3. Check results

**That's it. Fully automated.**

---

## 🚀 Next Steps After Deployment

### **Week 1:**
- Add 10-20 pieces of content
- Verify all process correctly
- Monitor Railway costs

### **Week 2:**
- Optimize polling interval if needed
- Add AssemblyAI key for long content
- Process your content backlog

### **Week 3:**
- Build Twitter auto-poster
- Build email sequence builder
- Add more automation

---

## 📞 Support

**Railway Issues:**
- Docs: https://docs.railway.app/
- Discord: https://discord.gg/railway
- Support: help@railway.app

**Service Issues:**
- Check Railway logs first
- Verify environment variables
- Test locally to isolate issue

---

## ✅ Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] Railway connected to GitHub repo
- [ ] All environment variables set
- [ ] Service deployed successfully
- [ ] Logs show no errors
- [ ] Test content processed correctly
- [ ] Payment method added (if using >$5/month)

---

**Once deployed, your poker content empire runs on autopilot.**
