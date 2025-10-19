# Beautiful Gradient MCP Server

A Model Context Protocol (MCP) server that generates beautiful gradient tweet mockups with Twitter OAuth authentication via Stytch.

## Features

- ✅ **Twitter OAuth** via Stytch - Users authenticate with real Twitter accounts
- ✅ **Auto-populated profiles** - Twitter handle, name, and avatar automatically loaded
- ✅ **25 beautiful gradients** - Curated presets for vibrant backgrounds
- ✅ **Comprehensive logging** - OAuth, MCP requests, database ops, errors
- ✅ **PostgreSQL/SQLite support** - Production & development database options

## Prerequisites

- Python 3.10+
- PostgreSQL (optional, SQLite works for development)
- Stytch account with Twitter OAuth configured
- ngrok (for testing with ChatGPT)

## Quick Start

### 1. Install Dependencies

```bash
cd beautiful_gradient_mcp
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
STYTCH_PROJECT_ID=project-test-1635b418-0599-4f50-b59b-de4f5489cb13
STYTCH_PUBLIC_TOKEN=public-token-test-ccb9309a-61fb-480e-99e9-f6d07ef1e545
STYTCH_CLIENT_ID=connected-app-test-fd392e29-366c-489c-a0e8-e4123d635779
DATABASE_URL=sqlite:///./gradient_mcp.db
```

### 3. Run Server

```bash
python main.py
```

Server starts on http://localhost:8000

### 4. Test OAuth Metadata Endpoint

```bash
curl http://localhost:8000/.well-known/oauth-authorization-server
```

Should return:
```json
{
  "issuer": "https://test.stytch.com",
  "authorization_endpoint": "https://test.stytch.com/v1/public/oauth/authorize",
  "token_endpoint": "https://test.stytch.com/v1/public/oauth/token",
  ...
}
```

### 5. Expose with ngrok (for ChatGPT testing)

```bash
# In another terminal
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok-free.app`)

### 6. Add to ChatGPT

1. Enable Developer Mode in ChatGPT
2. Settings → Connectors → Add Connector
3. Enter: `https://abc123.ngrok-free.app/mcp`
4. ChatGPT will initiate OAuth flow
5. Test: "Create a gradient tweet saying 'Hello World!'"

## Project Structure

```
beautiful_gradient_mcp/
├── main.py                 # FastMCP server + OAuth metadata endpoint
├── auth.py                 # Stytch token verification with logging
├── database.py             # PostgreSQL/SQLite models
├── gradients.py            # 25 gradient presets
├── logger.py               # Comprehensive logging setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── logs/                  # Log files (auto-created)
    ├── oauth.log          # OAuth flow events
    ├── mcp.log            # MCP requests
    ├── database.log       # Database operations
    ├── error.log          # Errors only
    └── startup.log        # Server startup
```

## Logging & Debugging

### View Logs in Real-Time

```bash
# OAuth flow
tail -f logs/oauth.log

# MCP requests
tail -f logs/mcp.log

# Errors only
tail -f logs/error.log

# All logs
tail -f logs/*.log
```

### Search Logs

```bash
# Find OAuth attempts for a user
grep "user_id" logs/oauth.log

# Find failed authentications
grep "❌" logs/oauth.log

# Find specific request
grep "[abc123]" logs/mcp.log  # Use request_id
```

### Log Levels

- **DEBUG**: Detailed OAuth/MCP/DB operations
- **INFO**: High-level flow (✅ success, ⚠️ warnings)
- **ERROR**: Failures with stack traces (❌)

All logs include:
- Timestamps
- Function names and line numbers
- Colored console output (errors in red, success in green)
- Request IDs for tracing

## Database

### SQLite (Development)

Default configuration - zero setup required. Database file created automatically.

```bash
DATABASE_URL=sqlite:///./gradient_mcp.db
```

### PostgreSQL (Production)

```bash
# Create database
createdb gradient_mcp

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/gradient_mcp

# Tables created automatically on first run
python main.py
```

### Database Schema

```sql
CREATE TABLE profiles (
    stytch_user_id VARCHAR PRIMARY KEY,
    twitter_id VARCHAR,
    twitter_handle VARCHAR,
    display_name VARCHAR,
    avatar_url VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## OAuth Flow

```
User in ChatGPT: "Create a gradient tweet"
  ↓
ChatGPT: Fetches /.well-known/oauth-authorization-server
  ↓
ChatGPT: Redirects to Stytch authorization URL
  ↓
Stytch: Shows "Sign in with Twitter"
  ↓
User: Authenticates with Twitter
  ↓
Stytch: Returns authorization code to ChatGPT
  ↓
ChatGPT: Exchanges code for access token
  ↓
ChatGPT: Calls MCP tool with Bearer token
  ↓
MCP Server: Verifies token with Stytch
  ↓
MCP Server: Extracts Twitter profile
  ↓
MCP Server: Saves/updates profile in database
  ↓
MCP Server: Returns widget data
```

## Available Tools

### `create-gradient-tweet`

Generate a beautiful tweet mockup with gradient background.

**Input:**
```json
{
  "tweetContent": "Hello World!",
  "gradientIndex": 0  // Optional, 0-24
}
```

**Output:**
```json
{
  "tweetContent": "Hello World!",
  "gradientIndex": 0,
  "gradientName": "Sunset Blaze",
  "profile": {
    "handle": "your_twitter",
    "name": "Your Name",
    "avatar": "https://..."
  }
}
```

## Gradients

25 curated gradient presets:

0. Sunset Blaze
1. Ocean Deep
2. Forest Dawn
3. Purple Haze
4. Fire Burst
5. Candy Floss
6. Northern Lights
7. Peachy Keen
8. Neon Nights
9. Emerald Sea
10. Lavender Dream
11. Cosmic Dust
12. Mango Tango
13. Sky Blue
14. Rose Gold
15. Mint Fresh
16. Electric Violet
17. Citrus Burst
18. Cherry Blossom
19. Aqua Marine
20. Golden Hour
21. Berry Smoothie
22. Ice Blue
23. Sunset Purple
24. Coral Reef

## Troubleshooting

### "STYTCH_PROJECT_ID not configured"

Make sure `.env` file exists and contains your Stytch credentials.

### "Database connection failed"

For PostgreSQL:
```bash
# Check if PostgreSQL is running
pg_isready

# Create database
createdb gradient_mcp
```

For SQLite - should work out of the box.

### "Token verification failed"

Check logs:
```bash
tail -f logs/oauth.log
```

Common issues:
- Invalid Stytch credentials
- Token expired
- Wrong token format

### ChatGPT can't reach server

- Make sure ngrok is running
- Check ngrok URL is correct
- Verify server is running (`curl http://localhost:8000/.well-known/oauth-authorization-server`)

## Development

### Run with auto-reload

```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

### Test without OAuth

The server works without authentication (returns default profile). Great for testing:

```bash
curl -X POST http://localhost:8000/mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create-gradient-tweet",
      "arguments": {
        "tweetContent": "Test tweet!"
      }
    },
    "id": 1
  }'
```

## Deployment

### Railway

1. Connect GitHub repo
2. Add PostgreSQL addon
3. Set environment variables:
   ```
   STYTCH_PROJECT_ID=...
   STYTCH_PUBLIC_TOKEN=...
   DATABASE_URL=<auto-configured>
   ```
4. Deploy!

### Environment Variables (Production)

```bash
STYTCH_PROJECT_ID=project-test-...
STYTCH_PUBLIC_TOKEN=public-token-test-...
STYTCH_CLIENT_ID=connected-app-test-...
DATABASE_URL=postgresql://...
LOG_LEVEL=INFO
```

## License

MIT

## Support

Check logs first:
```bash
tail -f logs/*.log
```

Look for ❌ error markers and stack traces.
