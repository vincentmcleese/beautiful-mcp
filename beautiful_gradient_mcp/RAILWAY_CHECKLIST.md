# Railway Deployment Checklist

Quick reference for deploying Beautiful Gradient MCP to Railway.

## Pre-Deployment Checklist

- [ ] **Code is committed to Git**
  ```bash
  git add .
  git commit -m "Prepare for Railway deployment"
  git push origin main
  ```

- [ ] **Frontend builds successfully locally** (optional test)
  ```bash
  cd frontend
  npm install
  npm run build
  cd ..
  ```

- [ ] **Have all required credentials ready:**
  - [ ] Stytch Project ID, Public Token, Client ID, Secret
  - [ ] Cloudinary URL (from cloudinary.com/console)

## Railway Setup

### 1. Create Project

- [ ] Go to [railway.app](https://railway.app)
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Connect your repository
- [ ] Select the `beautiful_gradient_mcp` directory as root (if needed)

### 2. Add PostgreSQL Database

- [ ] In project dashboard, click "New"
- [ ] Select "Database" → "PostgreSQL"
- [ ] Wait for provisioning to complete
- [ ] Verify `DATABASE_URL` appears in environment variables

### 3. Configure Environment Variables

Copy from `.env.railway` template and set these in Railway Dashboard → Variables:

#### Backend Variables
- [ ] `STYTCH_PROJECT_ID`
- [ ] `STYTCH_PUBLIC_TOKEN`
- [ ] `STYTCH_CLIENT_ID`
- [ ] `STYTCH_SECRET`
- [ ] `STYTCH_AUTHORIZATION_SERVER`
- [ ] `CLOUDINARY_URL`

#### Frontend Variables (Build-time)
- [ ] `VITE_STYTCH_PUBLIC_TOKEN` (must match `STYTCH_PUBLIC_TOKEN`)

#### Server Variables
- [ ] `PORT` = `8000`
- [ ] `SERVER_HOST` = `0.0.0.0`
- [ ] `USE_HTTPS` = `false`
- [ ] `LOG_LEVEL` = `INFO`

#### To Set After First Deploy
- [ ] `MCP_SERVER_URL` (e.g., `https://your-app.railway.app/mcp`)

### 4. Deploy

- [ ] Click "Deploy"
- [ ] Monitor build logs
- [ ] Wait for deployment to complete
- [ ] Copy your Railway app URL (e.g., `https://your-app.railway.app`)

### 5. Post-Deployment Configuration

- [ ] Update `MCP_SERVER_URL` environment variable with your Railway URL
- [ ] Trigger a redeploy (Railway → Deployments → Redeploy)
- [ ] Update Stytch redirect URIs:
  - [ ] Go to [Stytch Dashboard](https://stytch.com/dashboard)
  - [ ] Add redirect URI: `https://your-app.railway.app/login`
  - [ ] Add authorized domain if needed

## Testing Deployment

Test these endpoints to verify deployment:

- [ ] **Root**: `https://your-app.railway.app/` → Should show frontend
- [ ] **Login**: `https://your-app.railway.app/login` → Should show OAuth login
- [ ] **MCP Endpoint**: `https://your-app.railway.app/mcp` → Should return MCP response
- [ ] **OAuth Metadata**: `https://your-app.railway.app/.well-known/oauth-protected-resource` → Should return JSON
- [ ] **Health Check**: `https://your-app.railway.app/widget` → Should serve widget HTML

### Expected Responses

```bash
# Test MCP endpoint
curl https://your-app.railway.app/mcp

# Test OAuth metadata
curl https://your-app.railway.app/.well-known/oauth-protected-resource

# Test frontend
curl https://your-app.railway.app/
```

## Connect to ChatGPT

- [ ] Go to ChatGPT Settings → Connectors
- [ ] Click "Add Connector"
- [ ] Enter your MCP Server URL: `https://your-app.railway.app/mcp`
- [ ] Follow OAuth flow to authorize
- [ ] Test by asking ChatGPT: "Create a gradient tweet"

## Troubleshooting Checklist

### Build Fails
- [ ] Check build logs in Railway dashboard
- [ ] Verify `requirements.txt` exists
- [ ] Verify `frontend/package.json` exists
- [ ] Check that all `VITE_*` variables are set **before** build

### Frontend Shows Blank Page
- [ ] Check browser console for errors
- [ ] Verify `VITE_STYTCH_PUBLIC_TOKEN` is set correctly
- [ ] Rebuild deployment to pick up new environment variables
- [ ] Check that `frontend/dist/` was created during build

### Database Connection Errors
- [ ] Verify PostgreSQL is running
- [ ] Check `DATABASE_URL` environment variable
- [ ] Check Railway database logs
- [ ] Ensure database is in same Railway project

### OAuth Errors
- [ ] Verify all Stytch environment variables are set
- [ ] Check Stytch redirect URIs match Railway URL
- [ ] Verify `MCP_SERVER_URL` is set to deployed URL
- [ ] Check Stytch dashboard for error logs

### 404 Errors on Assets
- [ ] Verify frontend was built during deployment
- [ ] Check that frontend source is not excluded in `.railwayignore`
- [ ] Verify static file mounting in `main.py:544`

## Environment Variables Quick Reference

```env
# Copy these exact variable names to Railway dashboard

# Stytch (get from stytch.com/dashboard)
STYTCH_PROJECT_ID=
STYTCH_PUBLIC_TOKEN=
STYTCH_CLIENT_ID=
STYTCH_SECRET=
STYTCH_AUTHORIZATION_SERVER=

# Frontend (must match STYTCH_PUBLIC_TOKEN)
VITE_STYTCH_PUBLIC_TOKEN=

# MCP (set after deploy)
MCP_SERVER_URL=

# Cloudinary (get from cloudinary.com/console)
CLOUDINARY_URL=

# Database (auto-set by Railway)
DATABASE_URL=

# Server
PORT=8000
SERVER_HOST=0.0.0.0
USE_HTTPS=false
LOG_LEVEL=INFO
```

## Maintenance

### Update Frontend Code
1. Make changes to `frontend/src/`
2. Commit and push to GitHub
3. Railway will auto-rebuild frontend with environment variables
4. No need to manually run `npm run build`

### Update Backend Code
1. Make changes to `main.py` or other Python files
2. Commit and push to GitHub
3. Railway will auto-deploy

### Update Environment Variables
1. Go to Railway dashboard → Variables
2. Update value
3. Trigger redeploy if needed (especially for `VITE_*` variables)

### View Logs
1. Railway dashboard → Deployments
2. Click on deployment
3. View "Build Logs" or "Deploy Logs"

## Security Notes

- [ ] Never commit `.env` files to Git
- [ ] Use Railway environment variables for all secrets
- [ ] `STYTCH_PUBLIC_TOKEN` is safe to expose in frontend (it's public)
- [ ] `STYTCH_SECRET` must remain backend-only
- [ ] Review CORS settings in production (`main.py:788`)

## Cost Optimization

- [ ] Monitor Railway usage dashboard
- [ ] Set up usage alerts
- [ ] Consider scaling settings for production traffic
- [ ] Review database connection pooling

## Support Resources

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Stytch Docs: [stytch.com/docs](https://stytch.com/docs)
- MCP Docs: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Project README: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

---

**Ready to deploy?** Start from the top and check off each item! 🚀
