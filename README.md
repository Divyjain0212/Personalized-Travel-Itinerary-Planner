# Personalized Travel Itinerary Planner

**Skill Wallet Capstone Project 4**

Personalized Travel Itinerary Planner is a full-stack travel planning application. It helps travelers create a structured, budget-aware itinerary based on:

- Destination or travel mood
- Trip duration
- Budget
- Travel dates
- Travel party and group size
- Travel pace
- Food, adventure, history, and nightlife interests

The application includes a React dashboard, a FastAPI backend, demo itinerary generation, destination recommendations, activity swaps, trip history, and Supabase-ready persistence.

---

## What the application can do

### Smart trip builder

Users can enter a destination or leave it blank and describe the kind of trip they want. When no destination is provided, the application recommends three matching cities.

### Day-by-day itinerary generation

Generated itineraries contain four time slots per day:

1. Morning sightseeing
2. Lunch recommendation
3. Afternoon leisure
4. Evening dining and entertainment

Activities are grouped by neighbourhood or area to reduce unnecessary travel and backtracking.

### Budget tracking

Each activity includes an estimated cost. The itinerary also calculates:

- Daily local-currency cost
- Running cumulative cost
- Total cost in local currency
- Approximate USD cost
- Approximate INR cost

### Activity customization

Users can regenerate one activity without rebuilding the entire itinerary. Example requests include:

- `Find a vegetarian lunch spot`
- `Swap the museum for an outdoor market`
- `Add a relaxed café break`

### AI provider configuration

The trip builder supports:

- Demo mode, which requires no API key
- Google Gemini
- Groq

API keys entered in the browser are masked, kept in memory only, sent only with the relevant request, and never saved to trip history.

---

## Project architecture

```text
travel-planner/
|
|-- frontend/                 React + TypeScript + Vite dashboard
|   |-- src/App.tsx           Main user interface
|   |-- src/api.ts            Backend API client and TypeScript types
|   |-- src/styles.css        Application styling
|   |-- .env                  Frontend environment variables
|
|-- backend/                  FastAPI service
|   |-- app/main.py           REST API routes
|   |-- app/schemas.py        Pydantic request and response models
|   |-- app/engine.py         Demo recommendations and itinerary engine
|   |-- app/repository.py     Supabase/local JSON persistence
|   |-- app/config.py         Environment configuration
|   |-- app/ai.py             Gemini/Groq provider integration seam
|   |-- requirements.txt      Python dependencies
|
|-- supabase/schema.sql       Database table and row-level security policy
|-- travel_planner/           Original Streamlit prototype
|-- app.py                    Original Streamlit entry point
```

The recommended production path is:

```text
React frontend -> FastAPI backend -> Supabase database
                         |
                         -> Gemini or Groq
```

The application can also run without Supabase or an AI key. In that case, it uses deterministic demo generation and stores trips in `data/trips.json`.

---

## Requirements

Install the following software before starting:

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Optional: a Supabase project
- Optional: a Gemini or Groq API key

Check the installed versions:

```powershell
python --version
node --version
npm --version
```

---

## Run the application locally

Run the backend and frontend in two separate terminals.

### Terminal 1: start the FastAPI backend

```powershell
cd D:\travel-planner\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8082
```

The backend will be available at:

```text
http://localhost:8082
```

Verify that it is running:

```text
http://localhost:8082/health
```

The expected response is similar to:

```json
{
  "status": "ok",
  "environment": "development"
}
```

### Terminal 2: start the React frontend

```powershell
cd D:\travel-planner\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

The frontend is configured to call the backend at `http://localhost:8082`.

If your backend uses a different port, edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8082
```

After changing `.env`, restart the Vite development server.

---

## Using the application

1. Open `http://localhost:5173`.
2. Select **Demo mode**, or select Gemini/Groq and enter an API key.
3. Enter a destination, or leave it blank to receive recommendations.
4. Choose trip length, group size, pace, budget, and interests.
5. Click **Build my itinerary**.
6. If recommendations appear, click a recommended city to generate its itinerary.
7. Open **My itinerary** to review the daily plan and costs.
8. Open **Vibe & swaps** to regenerate an individual activity.
9. Open **Saved trips** to view stored trips when persistence is configured.

---

## API key configuration

### Per-user API key

Use the **AI generation** panel in the trip builder:

1. Select **Google Gemini** or **Groq**.
2. Enter the key in the masked API key field.
3. Build or regenerate the itinerary.

The key is:

- Stored only in React memory
- Sent only with the generation or swap request
- Not written to `data/trips.json`
- Not written to Supabase
- Not returned by the backend
- Cleared when the page is refreshed

### Server-managed API key

For a server-managed deployment, add one of these to `backend/.env`:

```env
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```

Never commit `.env` files or API keys to source control.

---

## Supabase setup

Supabase is optional for local demo mode.

1. Create a Supabase project.
2. Open the Supabase SQL Editor.
3. Run [supabase/schema.sql](./supabase/schema.sql).
4. Add the project settings to `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

5. Restart the FastAPI backend.

When both Supabase variables are present, the backend uses the `trips` table. Without them, the backend falls back to local JSON persistence.

### Security note

The Supabase service key is a server-side secret. It must only be used by the FastAPI backend and must never be placed in the React frontend or committed to the repository.

---

## Backend API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check whether the backend is running |
| `POST` | `/api/recommendations` | Return destination recommendations |
| `POST` | `/api/itineraries/generate` | Generate an itinerary or recommendations |
| `POST` | `/api/itineraries/swap` | Regenerate one activity slot |
| `GET` | `/api/trips` | List saved trips |
| `POST` | `/api/trips` | Save a trip |

Interactive API documentation is available while the backend is running:

```text
http://localhost:8082/docs
```

---

## Production build

Build the React frontend:

```powershell
cd D:\travel-planner\frontend
npm run build
```

The production files are written to `frontend/dist`.

Run the backend without the auto-reloader:

```powershell
cd D:\travel-planner\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

---

## Deployment

The frontend and backend are deployed separately:

- **Vercel** hosts the React/Vite frontend.
- **Render, Railway, Fly.io, or Azure App Service** hosts the FastAPI backend.
- **Supabase** provides the production database.

### Deploy the frontend to Vercel

The repository includes [vercel.json](./vercel.json), so Vercel can build the frontend from the repository root.

#### Option A: Vercel dashboard

1. Open [Vercel](https://vercel.com) and choose **Add New Project**.
2. Import `Divyjain0212/Personalized-Travel-Itinerary-Planner`.
3. Keep the repository root as the project root.
4. Add this environment variable:

   ```env
   VITE_API_URL=https://your-fastapi-service.example.com
   ```

5. Click **Deploy**.

Vercel will use:

```text
Install command: npm --prefix frontend install
Build command: npm --prefix frontend run build
Output directory: frontend/dist
```

#### Option B: Vercel CLI

Install and authenticate with the Vercel CLI:

```powershell
npm install --global vercel
vercel login
```

From the repository root:

```powershell
vercel
```

For a production deployment:

```powershell
vercel --prod
```

When prompted, link the project to the existing GitHub repository and add `VITE_API_URL` with the public backend URL.

### Deploy the backend

Deploy the `backend` directory to a Python hosting service such as:

- Render
- Railway
- Fly.io
- Azure App Service

Configure these environment variables in the hosting provider:

```env
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-domain.com
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

Use this backend start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deployment, verify:

```text
https://your-fastapi-service.example.com/health
```

Then set the backend URL as the Vercel `VITE_API_URL` environment variable and redeploy the frontend.

Configure CORS and Supabase secrets through the platform secret manager; never commit `.env` files.

---

## Troubleshooting

### The frontend says it cannot reach the planner API

Check that:

1. The backend terminal is still running.
2. `http://localhost:8082/health` opens successfully.
3. `frontend/.env` contains:

   ```env
   VITE_API_URL=http://localhost:8082
   ```

4. The frontend was restarted after editing `.env`.

### The itinerary is not generated without a destination

Click **Build my itinerary** first. The application will show three recommended cities. Click one of those cities to automatically generate the complete itinerary.

### Gemini or Groq generation does not work

Confirm that:

- The correct provider is selected.
- The API key is entered in the masked field.
- The key belongs to the selected provider.
- The backend is running.
- The browser can reach the backend URL.

Demo mode can always be used to verify the rest of the application.

### Supabase trips are not saved

Check that:

- `SUPABASE_URL` is correct.
- `SUPABASE_SERVICE_KEY` is the server-side service role key.
- `supabase/schema.sql` was executed.
- The backend was restarted after changing `.env`.

---

## Backwards-compatible Streamlit prototype

The original Streamlit implementation remains in [app.py](./app.py) and [travel_planner](./travel_planner). It is retained for reference and backwards compatibility.

To run it separately:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The React/FastAPI application is the recommended full-stack version.
