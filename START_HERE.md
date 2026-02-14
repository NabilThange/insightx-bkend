# 🚀 START HERE - InsightX Backend

## Quick Start (3 Steps)

### Step 1: Add Your Service Role Key

1. Open this URL in your browser:
   ```
   https://supabase.com/dashboard/project/xvtqbvavwbowyyoevolo/settings/api
   ```

2. Find the **service_role** key (NOT the anon key)

3. Copy it and paste into `backend/.env`:
   ```
   SUPABASE_SERVICE_KEY=paste-your-key-here
   ```

### Step 2: Run the Server

**Windows:**
```bash
cd backend
run.bat
```

**Mac/Linux:**
```bash
cd backend
chmod +x run.sh
./run.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Start the server

### Step 3: Test It

Open in browser: `http://localhost:8000/docs`

Click on **POST /api/upload** → Try it out → Upload `sample_data.csv`

That's it! 🎉

---

## What You Just Built

✅ Complete FastAPI backend with 9 endpoints
✅ CSV → Parquet conversion
✅ Supabase Storage integration
✅ Data DNA generation (pandas profiling)
✅ DuckDB query engine with caching
✅ Chat system (stubbed for AI later)

---

## Next Steps

1. **Test all endpoints** in `/docs`
2. **Check Supabase** - verify files uploaded
3. **Connect frontend** - update API URLs
4. **Deploy to Railway** - push to GitHub
5. **Add AI** - replace stubbed chat endpoint

---

## Need Help?

- **Setup issues?** → Read `SETUP_GUIDE.md`
- **Quick commands?** → Check `QUICK_REFERENCE.md`
- **Full docs?** → See `README.md`
- **What's built?** → Read `BUILD_SUMMARY.md`

---

## File Structure

```
backend/
├── START_HERE.md          ← You are here
├── SETUP_GUIDE.md         ← Detailed setup
├── QUICK_REFERENCE.md     ← Quick commands
├── BUILD_SUMMARY.md       ← What's implemented
├── README.md              ← Full documentation
│
├── main.py                ← FastAPI app
├── .env                   ← Add service key here!
├── sample_data.csv        ← Test data
│
├── routes/                ← API endpoints
├── services/              ← Business logic
├── models/                ← Pydantic schemas
└── db/                    ← Supabase client
```

---

## Common Issues

**"SUPABASE_SERVICE_KEY must be set"**
→ Edit `.env` and add your service role key

**"Module not found"**
→ Run `pip install -r requirements.txt`

**"Port 8000 in use"**
→ Run `uvicorn main:app --reload --port 8001`

---

## Test Flow

```
1. Upload CSV
   ↓
2. Explore (generates Data DNA)
   ↓
3. Get Session (see Data DNA)
   ↓
4. Create Chat
   ↓
5. Send Message
   ↓
6. Get Response (stubbed for now)
```

---

**Ready?** Add your service key to `.env` and run `run.bat` (Windows) or `./run.sh` (Mac/Linux)!
