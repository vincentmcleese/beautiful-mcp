# Railway Deployment Guide

This guide covers deploying the Beautiful Gradient MCP Server to Railway.

## Project Structure

- **Backend**: Python FastAPI MCP server (`main.py`)
- **Frontend**: React/Vite SPA (`frontend/`)
- **Database**: PostgreSQL (Railway managed)
- **Static Assets**: Widgets served by backend

## Prerequisites

1. Railway account ([railway.app](https://railway.app))
2. GitHub repository connected to Railway
3. PostgreSQL database provisioned in Railway

## Deployment Steps

### 1. Create Railway Project

```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login to Railway
railway login

# Create new project (or use the dashboard)
railway init
```

### 2. Add PostgreSQL Database

1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` environment variable

### 3. Set Environment Variables

Add these in Railway dashboard under "Variables":

#### Required Variables

```env
# Stytch OAuth Configuration
STYTCH_PROJECT_ID=project-test-YOUR_PROJECT_ID
STYTCH_PUBLIC_TOKEN=public-token-test-YOUR_TOKEN
STYTCH_CLIENT_ID=connected-app-test-YOUR_CLIENT_ID
STYTCH_SECRET=secret-test-YOUR_SECRET
STYTCH_AUTHORIZATION_SERVER=https://YOUR_SERVER.customers.stytch.dev

# Frontend Build Variables (IMPORTANT!)
# This is baked into the JS bundle at BUILD TIME by Vite
# Must match STYTCH_PUBLIC_TOKEN above
VITE_STYTCH_PUBLIC_TOKEN=public-token-test-YOUR_TOKEN

# MCP Server URL (set after first deploy)
MCP_SERVER_URL=https://your-app.railway.app/mcp

# Database (automatically set by Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Cloudinary for image sharing
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Server Configuration
PORT=8000
SERVER_HOST=0.0.0.0
USE_HTTPS=false

# Logging
LOG_LEVEL=INFO
```

#### ⚠️ Important: Frontend Environment Variables

**Vite environment variables** (`VITE_*` prefix) are **baked into the JavaScript bundle at build time**, not runtime. This means:

1. `VITE_STYTCH_PUBLIC_TOKEN` must be set in Railway **before** building
2. Railway will inject this value during the `npm run build` step
3. The frontend source code is included in the deployment (not just `dist/`)
4. If you change `VITE_STYTCH_PUBLIC_TOKEN`, you must **rebuild** (redeploy) for it to take effect

**Why this works:**
- Railway runs the build command with environment variables set
- Vite reads `VITE_*` variables during build and embeds them in the bundle
- The built `frontend/dist/` contains the JavaScript with hardcoded values

#### Optional Variables

```env
# SSL Configuration (Railway provides HTTPS automatically)
SSL_CERT_PATH=
SSL_KEY_PATH=
```

### 4. Build Configuration

The project includes:
- `railway.toml` - Railway build configuration
- `Procfile` - Process definition
- `.railwayignore` - Files to exclude from deployment

**Build Process:**
1. Install frontend dependencies
2. Build React app (`npm run build` in frontend/)
3. Install Python dependencies
4. Start uvicorn server

### 5. Deploy

#### Option A: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Connect repository in Railway dashboard
3. Railway will auto-deploy on every push to main

#### Option B: Railway CLI

```bash
cd beautiful_gradient_mcp
railway up
```

### 6. Post-Deployment

#### Update MCP_SERVER_URL

After first deployment, update the `MCP_SERVER_URL` variable:

```env
MCP_SERVER_URL=https://your-app.railway.app/mcp
```

Trigger a redeploy for changes to take effect.

#### Initialize Database

The database will be automatically initialized on first run via `init_db()` in `main.py`.

#### Test Endpoints

- **MCP Endpoint**: `https://your-app.railway.app/mcp`
- **OAuth Metadata**: `https://your-app.railway.app/.well-known/oauth-protected-resource`
- **Frontend**: `https://your-app.railway.app/`
- **Login**: `https://your-app.railway.app/login`
- **Widget**: `https://your-app.railway.app/widget`

## Railway Configuration Files

### railway.toml

```toml
[build]
builder = "nixpacks"
buildCommand = "cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Procfile

```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Troubleshooting

### Build Fails

- Check that `requirements.txt` is in the root of `beautiful_gradient_mcp/`
- Ensure frontend build completes successfully locally first
- Check Railway build logs for specific errors

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL addon is running
- Check database logs in Railway dashboard

### Frontend Not Loading

- Verify frontend was built (`frontend/dist/` exists)
- Check static file mounting in `main.py:544`
- Ensure root route serves `index.html` (`main.py:789`)

### OAuth Issues

- Verify all Stytch environment variables are set
- Update Stytch redirect URIs to use Railway URL
- Check that `MCP_SERVER_URL` matches deployed URL

### Static Assets 404

- Ensure frontend is built before deployment
- Check `.railwayignore` doesn't exclude `frontend/dist/`
- Verify static file mounting is correct

## Local Testing Before Deploy

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/mcp
```

## Monitoring

- **Logs**: View in Railway dashboard under "Deployments"
- **Metrics**: Railway provides CPU, memory, and network metrics
- **Health Check**: Railway automatically monitors your service

## Scaling

Railway offers:
- Automatic scaling based on load
- Configurable resources (CPU/memory)
- Multiple deployment regions

Configure in Railway dashboard under "Settings" → "Resources"

## CI/CD

Railway automatically deploys on push to your configured branch (default: main).

To disable auto-deploy:
1. Go to Settings → General
2. Toggle "Auto-deploy" off

## Database Migrations

For schema changes, you may need to run migrations manually:

```bash
# Using Railway CLI
railway run python -c "from database import init_db; init_db()"
```

Or connect directly via `psql` using the Railway-provided connection string.

## Updating Stytch Configuration

After deploying, update your Stytch application settings:

1. Go to [Stytch Dashboard](https://stytch.com/dashboard)
2. Update OAuth redirect URIs:
   - `https://your-app.railway.app/callback`
3. Update allowed domains if needed

## Costs

- Railway offers a free tier with limitations
- PostgreSQL database usage counts toward your plan
- Monitor usage in Railway dashboard

## Support

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Stytch Docs: [stytch.com/docs](https://stytch.com/docs)
- MCP Docs: [modelcontextprotocol.io](https://modelcontextprotocol.io)
