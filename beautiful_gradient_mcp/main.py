"""Beautiful Gradient MCP Server - FastMCP with Stytch OAuth."""

import os
import json
import uuid
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from mcp.server.auth.provider import TokenVerifier, AccessToken
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from logger import oauth_logger, mcp_logger, startup_logger, error_logger
from auth import verify_stytch_token, verify_jwt_token, extract_twitter_profile
from database import init_db, get_db, get_or_create_profile, Profile
from gradients import GRADIENTS, get_gradient_css

# Load environment variables
load_dotenv()

# Configuration
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID", "")
STYTCH_PUBLIC_TOKEN = os.getenv("STYTCH_PUBLIC_TOKEN", "")
STYTCH_CLIENT_ID = os.getenv("STYTCH_CLIENT_ID", "")
STYTCH_AUTHORIZATION_SERVER = os.getenv(
    "STYTCH_AUTHORIZATION_SERVER",
    "https://decorous-scale-5822.customers.stytch.dev"
)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# OAuth endpoints (legacy - kept for reference)
OAUTH_AUTHORIZE_URL = "https://test.stytch.com/v1/public/oauth/authorize"
OAUTH_TOKEN_URL = "https://test.stytch.com/v1/public/oauth/token"
OAUTH_REGISTER_URL = "https://test.stytch.com/v1/public/oauth/register"


# Stytch Token Verifier (Official FastMCP Pattern)
class StytchVerifier(TokenVerifier):
    """Verifies Stytch OAuth tokens according to FastMCP auth pattern."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify JWT access token with Stytch and return AccessToken if valid.

        Args:
            token: The JWT access token from OAuth flow

        Returns:
            AccessToken if valid, None if invalid
        """
        try:
            oauth_logger.info(f"🔐 Verifying JWT token with Stytch (FastMCP pattern)")

            # Use JWT verification for OAuth access tokens
            jwt_claims = await verify_jwt_token(token)

            # Extract required fields from JWT claims
            subject = jwt_claims.get("sub")  # User ID is in 'sub' claim
            client_id = jwt_claims.get("azp", jwt_claims.get("client_id", ""))  # Authorized party

            if not subject:
                oauth_logger.error("❌ No 'sub' claim in JWT")
                return None

            oauth_logger.info(f"✅ JWT verified for subject: {subject}")

            # Extract scopes if present
            scopes = jwt_claims.get("scope", "").split() if "scope" in jwt_claims else []

            return AccessToken(
                token=token,
                client_id=client_id,    # OAuth client ID
                subject=subject,        # User ID from JWT sub claim
                scopes=scopes,          # OAuth scopes if any
                claims=jwt_claims,      # Store full JWT claims for later use
            )

        except Exception as e:
            oauth_logger.error(f"❌ JWT verification failed: {str(e)}")
            error_logger.exception("JWT verification error", exc_info=e)
            return None


# Create FastMCP server with Authentication (Official Pattern)
mcp_server = FastMCP(
    name="beautiful-gradient-mcp",
    stateless_http=True,
    token_verifier=StytchVerifier(),
    auth=AuthSettings(
        issuer_url=STYTCH_AUTHORIZATION_SERVER,
        resource_server_url=MCP_SERVER_URL,  # Reads from MCP_SERVER_URL env var
        required_scopes=[],  # No specific scopes required
    ),
)

# Initialize database
try:
    init_db()
except Exception as e:
    startup_logger.error(f"Failed to initialize database: {str(e)}")
    # Continue anyway for testing

# Tool input schema
TOOL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "tweetContent": {
            "type": "string",
            "description": "The content of the tweet to render"
        },
        "gradientIndex": {
            "type": "integer",
            "description": "Gradient preset index (0-24)",
            "default": 0,
            "minimum": 0,
            "maximum": 24
        }
    },
    "required": ["tweetContent"],
    "additionalProperties": False
}


@mcp_server._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    mcp_logger.info("📋 Tools list requested")

    tools = [
        types.Tool(
            name="get-my-profile",
            title="Get My Profile",
            description="Get the authenticated user's profile information from OAuth",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
            securitySchemes=[
                {
                    "type": "oauth2",
                    "scopes": ["openid", "profile"]
                }
            ],
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True
            }
        ),
        types.Tool(
            name="create-gradient-tweet",
            title="Create Gradient Tweet",
            description="Generate a beautiful tweet mockup with a vibrant gradient background",
            inputSchema=TOOL_INPUT_SCHEMA,
            securitySchemes=[
                {
                    "type": "oauth2",
                    "scopes": ["openid", "profile"]
                }
            ],
            _meta={
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True
            }
        )
    ]

    mcp_logger.info(f"✅ Returned {len(tools)} tools")
    return tools


async def _call_tool(request: types.CallToolRequest) -> types.ServerResult:
    """Handle MCP tool calls."""
    request_id = uuid.uuid4().hex[:8]

    mcp_logger.error(f"🚨 _call_tool() ENTERED!")
    mcp_logger.error(f"Request.params.meta: {request.params.meta if hasattr(request.params, 'meta') else 'NO META'}")
    if hasattr(request.params, 'meta') and request.params.meta:
        meta_dict = request.params.meta.__dict__ if hasattr(request.params.meta, '__dict__') else {}
        mcp_logger.error(f"Meta dict: {meta_dict}")
        openai_subject = getattr(request.params.meta, 'openai/subject', None)
        mcp_logger.error(f"openai/subject: {openai_subject}")

    mcp_logger.info("=" * 80)
    mcp_logger.info(f"📥 MCP Tool Call [{request_id}]")
    mcp_logger.info(f"Tool: {request.params.name}")
    mcp_logger.info(f"Arguments: {json.dumps(request.params.arguments, indent=2)}")

    # Extract authorization token from request metadata
    # The exact location of the token depends on how MCP sends it
    auth_token = None
    if hasattr(request.params, "_meta"):
        auth_token = request.params._meta.get("authorization_token")

    mcp_logger.info(f"Authorization present: {bool(auth_token)}")

    # For now, let's make auth optional for testing
    # In production, you'd require it
    profile = None
    if auth_token:
        mcp_logger.debug(f"Token (first 20): {auth_token[:20]}...")

        try:
            # Verify with Stytch
            user_data = await verify_stytch_token(auth_token)
            mcp_logger.info(f"✅ Token verified")

            # Extract Twitter profile
            twitter_profile = extract_twitter_profile(user_data)

            if twitter_profile:
                # Get or create profile in database
                db = get_db()
                try:
                    profile = get_or_create_profile(db, twitter_profile)
                    if profile:
                        mcp_logger.info(f"✅ Profile loaded: @{profile.twitter_handle}")
                finally:
                    db.close()

        except Exception as e:
            mcp_logger.error(f"❌ Auth failed: {str(e)}")
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Authentication failed: {str(e)}"
                        )
                    ],
                    isError=True
                )
            )

    # Execute tool
    if request.params.name == "get-my-profile":
        return await handle_get_my_profile(auth_token, request_id)
    elif request.params.name == "create-gradient-tweet":
        return await handle_create_gradient_tweet(request.params.arguments, profile, request_id)
    else:
        mcp_logger.error(f"❌ Unknown tool: {request.params.name}")
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {request.params.name}"
                    )
                ],
                isError=True
            )
        )


async def handle_get_my_profile(
    auth_token: Optional[str],
    request_id: str
) -> types.ServerResult:
    """Handle the get-my-profile tool to test OAuth authentication."""
    mcp_logger.info(f"🔧 Executing get-my-profile [{request_id}]")

    if not auth_token:
        mcp_logger.error(f"❌ No auth token provided [{request_id}]")
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="Authentication required. Please connect your account first."
                    )
                ],
                isError=True
            )
        )

    try:
        # Verify JWT token
        mcp_logger.info(f"🔐 Verifying JWT token [{request_id}]")
        jwt_claims = await verify_jwt_token(auth_token)

        # Extract user information from JWT
        subject = jwt_claims.get("sub", "UNKNOWN")
        client_id = jwt_claims.get("azp", jwt_claims.get("client_id", "UNKNOWN"))
        scopes = jwt_claims.get("scope", "").split() if "scope" in jwt_claims else []

        # Build profile response
        profile_data = {
            "user_id": subject,
            "client_id": client_id,
            "scopes": scopes,
            "jwt_claims": jwt_claims
        }

        mcp_logger.info(f"✅ Profile retrieved for user: {subject} [{request_id}]")
        mcp_logger.info(f"📊 Scopes: {scopes}")

        # Create readable text response
        text_response = f"""Profile Information:
- User ID: {subject}
- Client ID: {client_id}
- Scopes: {', '.join(scopes) if scopes else 'none'}
- JWT Claims: {len(jwt_claims)} claims present"""

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=text_response
                    )
                ],
                structuredContent=profile_data
            )
        )

    except Exception as e:
        mcp_logger.error(f"❌ Failed to get profile: {str(e)} [{request_id}]")
        error_logger.exception("Get profile error", exc_info=e)
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Failed to retrieve profile: {str(e)}"
                    )
                ],
                isError=True
            )
        )


async def handle_create_gradient_tweet(
    arguments: Dict[str, Any],
    profile: Profile | None,
    request_id: str
) -> types.ServerResult:
    """Handle the create-gradient-tweet tool."""
    mcp_logger.info(f"🔧 Executing create-gradient-tweet [{request_id}]")

    tweet_content = arguments.get("tweetContent", "")
    gradient_index = arguments.get("gradientIndex", 0)

    # Validate gradient index
    if not 0 <= gradient_index < len(GRADIENTS):
        gradient_index = 0

    gradient = GRADIENTS[gradient_index]
    mcp_logger.info(f"🌈 Using gradient: {gradient['name']} (index {gradient_index})")

    # Build response with profile data or defaults
    if profile:
        twitter_data = {
            "handle": profile.twitter_handle,
            "name": profile.display_name,
            "avatar": profile.avatar_url
        }
        mcp_logger.info(f"Using authenticated profile: @{profile.twitter_handle}")
    else:
        # Default profile for testing without auth
        twitter_data = {
            "handle": "twitter_user",
            "name": "Twitter User",
            "avatar": "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
        }
        mcp_logger.warning("⚠️ Using default profile (no auth)")

    # Structured content for the widget
    structured_content = {
        "tweetContent": tweet_content,
        "gradientIndex": gradient_index,
        "gradientName": gradient['name'],
        "profile": twitter_data
    }

    # Text response
    text_response = f"Created gradient tweet with {gradient['name']} gradient!"

    mcp_logger.info(f"✅ Tool executed successfully [{request_id}]")
    mcp_logger.debug(f"Structured content: {json.dumps(structured_content, indent=2)}")
    mcp_logger.info("=" * 80)

    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=text_response
                )
            ],
            structuredContent=structured_content,
            _meta={
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True
            }
        )
    )


# OAuth Protected Resource Metadata endpoint is now handled automatically by FastMCP
# when auth=AuthSettings(...) is configured above.
# FastMCP exposes /.well-known/oauth-protected-resource automatically.


# Register tool handler (following official example pattern)
mcp_server._mcp_server.request_handlers[types.CallToolRequest] = _call_tool

# Create Starlette app from FastMCP
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
import os

app = mcp_server.streamable_http_app()

# OAuth Protected Resource Metadata route is automatically added by FastMCP
# when auth=AuthSettings(...) is configured

# Serve built React app
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# Mount static assets
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# Serve index.html at /login
@app.route("/login")
async def login_page(request):
    """Serve the OAuth login page (built React app with Stytch IdentityProvider)."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False
)


# Startup logging (called when server starts)
def log_startup():
    """Server startup logging."""
    startup_logger.info("=" * 80)
    startup_logger.info("🚀 Beautiful Gradient MCP Server Starting")
    startup_logger.info("=" * 80)
    startup_logger.info(f"Stytch Project ID: {STYTCH_PROJECT_ID[:20] if STYTCH_PROJECT_ID else 'NOT SET'}...")
    startup_logger.info(f"Stytch Authorization Server: {STYTCH_AUTHORIZATION_SERVER}")
    startup_logger.info(f"OAuth Metadata Endpoint: /.well-known/oauth-protected-resource")
    startup_logger.info("=" * 80)


if __name__ == "__main__":
    import uvicorn
    log_startup()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
