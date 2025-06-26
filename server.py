import os
import sys
from typing import Annotated
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp.server.auth.provider import AccessToken

# FORCE LOGGING TO SHOW
print("=" * 60, flush=True)
print("🚀 BASIC DEBUG SERVER STARTING", flush=True)
print("=" * 60, flush=True)

TOKEN = "193905b485d6"
MY_NUMBER = "918583949261"

print(f"🔑 TOKEN SET TO: '{TOKEN}'", flush=True)
print(f"📱 PHONE SET TO: '{MY_NUMBER}'", flush=True)

class BasicDebugAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        print(f"🔧 AUTH PROVIDER __init__ called with token: '{token}'", flush=True)
        try:
            k = RSAKeyPair.generate()
            print("✅ RSA key pair generated successfully", flush=True)
            super().__init__(
                public_key=k.public_key, jwks_uri=None, issuer=None, audience=None
            )
            print("✅ BearerAuthProvider parent init successful", flush=True)
            self.token = token
            print(f"✅ Auth provider fully initialized with token: '{token}'", flush=True)
        except Exception as e:
            print(f"❌ AUTH PROVIDER INIT ERROR: {e}", flush=True)
            raise

    async def load_access_token(self, token: str) -> AccessToken | None:
        print("\n" + "="*50, flush=True)
        print("🔍 LOAD_ACCESS_TOKEN CALLED!", flush=True)
        print(f"🔍 Received token: '{token}' (type: {type(token)})", flush=True)
        print(f"🔍 Expected token: '{self.token}' (type: {type(self.token)})", flush=True)
        print(f"🔍 Tokens equal: {token == self.token}", flush=True)
        print(f"🔍 Token length received: {len(token)}", flush=True)
        print(f"🔍 Token length expected: {len(self.token)}", flush=True)
        
        if token == self.token:
            print("✅ TOKEN MATCH! Creating AccessToken...", flush=True)
            try:
                access_token = AccessToken(
                    token=token,
                    client_id="debug-client",
                    scopes=[],
                    expires_at=None,
                )
                print("✅ AccessToken created successfully!", flush=True)
                return access_token
            except Exception as e:
                print(f"❌ AccessToken creation failed: {e}", flush=True)
                return None
        else:
            print("❌ TOKEN MISMATCH! Rejecting...", flush=True)
            return None

print("🔧 Creating auth provider...", flush=True)
try:
    auth_provider = BasicDebugAuthProvider(TOKEN)
    print("✅ Auth provider created successfully", flush=True)
except Exception as e:
    print(f"❌ Auth provider creation failed: {e}", flush=True)
    sys.exit(1)

print("🔧 Creating MCP server...", flush=True)
try:
    mcp = FastMCP(
        "Basic Debug MCP Server",
        auth=auth_provider
    )
    print("✅ MCP server created successfully", flush=True)
except Exception as e:
    print(f"❌ MCP server creation failed: {e}", flush=True)
    sys.exit(1)

@mcp.tool
async def debug_info() -> str:
    """Return debug information"""
    print("🛠️  DEBUG_INFO tool called!", flush=True)
    return f"Debug server working! Token: {TOKEN[:8]}..., Phone: {MY_NUMBER}"

@mcp.tool
async def validate() -> str:
    """Return phone number for validation"""
    print("📞 VALIDATE tool called!", flush=True)
    return MY_NUMBER

@mcp.tool
async def resume() -> str:
    """Return a basic resume"""
    print("📄 RESUME tool called!", flush=True)
    return """# AMRITANSHU LAHIRI

**Phone:** +91 8583949261
**Location:** Kolkata, India

## SUMMARY
Basic resume for MCP server testing and validation.

## SKILLS
- Python Development
- MCP Server Implementation
- Authentication Debugging

## EXPERIENCE
### Software Developer | 2024
- Implemented MCP server with authentication
- Debugged Railway deployment and authentication issues
- Successfully integrated with external AI systems"""

async def main():
    print("\n" + "="*60, flush=True)
    print("🚀 STARTING MCP SERVER", flush=True)
    print("="*60, flush=True)
    
    port = int(os.environ.get("PORT", 8085))
    print(f"🌐 Server will start on port: {port}", flush=True)
    print(f"🔑 Using token: {TOKEN}", flush=True)
    print(f"📱 Phone number: {MY_NUMBER}", flush=True)
    
    try:
        print("🔄 Starting async server...", flush=True)
        await mcp.run_async(
            "streamable-http",
            host="0.0.0.0",
            port=port,
        )
    except Exception as e:
        print(f"❌ SERVER STARTUP FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🏁 Starting main function...", flush=True)
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ MAIN FUNCTION FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
