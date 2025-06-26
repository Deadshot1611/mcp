import os
from typing import Annotated
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp.server.auth.provider import AccessToken
from pathlib import Path

# PUT YOUR EXACT APPLICATION KEY HERE
TOKEN = "193905b485d6"  # REPLACE WITH YOUR EXACT TOKEN FROM /apply
MY_NUMBER = "918583949261"

class DebugBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(
            public_key=k.public_key, jwks_uri=None, issuer=None, audience=None
        )
        self.token = token
        print(f"🔧 [AUTH INIT] Expected token: '{token}' (length: {len(token)})")

    async def load_access_token(self, token: str) -> AccessToken | None:
        print(f"🔍 [AUTH CHECK] Received token: '{token}' (length: {len(token)})")
        print(f"🔍 [AUTH CHECK] Expected token: '{self.token}' (length: {len(self.token)})")
        print(f"🔍 [AUTH CHECK] Tokens match: {token == self.token}")
        print(f"🔍 [AUTH CHECK] Token type: {type(token)}")
        print(f"🔍 [AUTH CHECK] Expected type: {type(self.token)}")
        
        # Additional debugging
        if token != self.token:
            print(f"🔍 [AUTH DEBUG] Token bytes comparison:")
            print(f"    Received: {[ord(c) for c in token[:20]]}")
            print(f"    Expected: {[ord(c) for c in self.token[:20]]}")
        
        if token == self.token:
            print("✅ [AUTH SUCCESS] Token validated successfully!")
            return AccessToken(
                token=token,
                client_id="debug-client",
                scopes=[],
                expires_at=None,
            )
        else:
            print("❌ [AUTH FAILED] Token validation failed!")
            return None

# Create MCP server with debug auth
mcp = FastMCP(
    "Debug MCP Server with Detailed Logging",
    auth=DebugBearerAuthProvider(TOKEN),
)

@mcp.tool
async def debug_info() -> str:
    """Return debug information about the server"""
    return f"Debug server is working! Expected token: {TOKEN[:8]}... (length: {len(TOKEN)})"

@mcp.tool
async def validate() -> str:
    """Return phone number for validation."""
    print(f"📞 [VALIDATE] Returning phone number: {MY_NUMBER}")
    return MY_NUMBER

@mcp.tool
async def resume() -> str:
    """Return a simple resume placeholder"""
    return "# Debug Resume\n\nThis is a debug resume response to test the server functionality."

async def main():
    print("=" * 60)
    print("🚀 STARTING DEBUG MCP SERVER")
    print(f"🔑 Expected token: {TOKEN}")
    print(f"📏 Token length: {len(TOKEN)}")
    print(f"📞 Phone number: {MY_NUMBER}")
    print("=" * 60)
    
    port = int(os.environ.get("PORT", 8085))
    print(f"🌐 Server will run on port: {port}")
    
    await mcp.run_async(
        "streamable-http",
        host="0.0.0.0",
        port=port,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
