#!/usr/bin/env python3
"""
Kaspa MCP Server - MCP Server
MCP server for Kaspa node RPC integration

Author: Artem Bogomaz <artem@example.com>
Version: 0.1.0
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime
from typing import Any, Dict, Optional

# Import our modules
from core.config import config
from core.client import KaspaClient

# FastMCP import
from mcp.server.fastmcp import FastMCP

# Data directory for storing API responses
DATA_DIR = "kaspa_mcp_data"

# Get port from environment
PORT = int(os.environ.get("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(name="kaspa-mcp-server", host="0.0.0.0", port=PORT)

# Initialize Kaspa client
kaspa_client = None


def save_api_data(data_type: str, data: Dict[str, Any]) -> None:
    """Save API data to file for debugging and monitoring"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)

        # Add metadata
        data["saved_at"] = datetime.now().isoformat()
        data["server_name"] = "kaspa-mcp-server"
        data["server_version"] = "0.1.0"

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if config.debug:
            print(f"💾 Data saved to: {filepath}")

    except Exception as e:
        print(f"❌ Error saving data: {str(e)}")


def run_async_tool(async_func, *args, **kwargs):
    """
    Synchronous wrapper for async tools - Required for FastMCP compatibility
    """
    try:
        import asyncio
        import concurrent.futures

        try:
            # Try to get the existing event loop
            loop = asyncio.get_running_loop()

            # If we have a running loop, we need to run in a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                def run_and_close_loop():
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        # Run the async function
                        return loop.run_until_complete(async_func(*args, **kwargs))
                    finally:
                        # Ensure the loop is closed properly
                        loop.close()
                
                future = executor.submit(run_and_close_loop)
                result = future.result(timeout=60)  # 60 second timeout
                return result

        except RuntimeError:
            # No running loop, safe to create new one
            result = asyncio.run(async_func(*args, **kwargs))
            return result

    except concurrent.futures.TimeoutError:
        return {
            "status": "error",
            "message": "Tool execution timed out after 60 seconds",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


# API Implementation Functions
async def get_node_info_async() -> Dict[str, Any]:
    """Get Kaspa node information and status"""
    try:
        print(f"🔍 Getting Kaspa node info...")
        
        info = await kaspa_client.get_info()
        
        return {
            "status": "success",
            "node_info": info,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get node info: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def get_block_by_hash_async(block_hash: str, include_transactions: bool = False) -> Dict[str, Any]:
    """Get block by hash from Kaspa node"""
    try:
        print(f"🔍 Getting block by hash: {block_hash}")
        
        block = await kaspa_client.get_block(block_hash, include_transactions)
        
        return {
            "status": "success",
            "block_hash": block_hash,
            "block": block,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get block {block_hash}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def get_block_dag_info_async() -> Dict[str, Any]:
    """Get BlockDAG information including latest DAA score"""
    try:
        print(f"🔍 Getting BlockDAG info...")
        
        dag_info = await kaspa_client.get_block_dag_info()
        
        return {
            "status": "success",
            "dag_info": dag_info,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get BlockDAG info: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def get_virtual_selected_parent_blue_score_async() -> Dict[str, Any]:
    """Get the current DAA score (blue score of virtual selected parent)"""
    try:
        print(f"🔍 Getting current DAA score...")
        
        result = await kaspa_client.get_virtual_selected_parent_blue_score()
        
        return {
            "status": "success",
            "blue_score": result.get("blueScore"),
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get DAA score: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


# MCP Tool Registration
@mcp.tool()
def get_node_info() -> str:
    """
    Get Kaspa node information and connection status.
    
    Returns comprehensive status including:
    - Node version
    - Network ID
    - Block count
    - Connection status
    
    Returns:
        JSON string with complete node information
    """
    global kaspa_client
    if not kaspa_client:
        kaspa_client = KaspaClient(config.kaspa_rpc_url)
    
    result = run_async_tool(get_node_info_async)
    save_api_data("node_info", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_block_by_hash(block_hash: str, include_transactions: bool = False) -> str:
    """
    Get detailed information about a specific block by its hash.
    
    Args:
        block_hash: The hash of the block to retrieve
        include_transactions: Whether to include transaction details (default: False)
    
    Returns:
        JSON string with complete block details including:
        - Block header (version, parents, timestamp, etc.)
        - Difficulty information
        - Blue score (DAA score)
        - Transactions (if requested)
    """
    global kaspa_client
    if not kaspa_client:
        kaspa_client = KaspaClient(config.kaspa_rpc_url)
    
    if not block_hash:
        error_result = {
            "status": "error",
            "message": "block_hash is required",
        }
        return json.dumps(error_result, indent=2)
    
    result = run_async_tool(get_block_by_hash_async, block_hash, include_transactions)
    save_api_data(f"block_{block_hash[:8]}", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_latest_daa() -> str:
    """
    Get the latest DAA (Difficulty Adjustment Algorithm) score.
    
    The DAA score is represented by the blue score of the virtual selected parent block.
    This value indicates the current position in the BlockDAG.
    
    Returns:
        JSON string with:
        - Current blue score (DAA score)
        - Timestamp
    """
    global kaspa_client
    if not kaspa_client:
        kaspa_client = KaspaClient(config.kaspa_rpc_url)
    
    result = run_async_tool(get_virtual_selected_parent_blue_score_async)
    save_api_data("latest_daa", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_block_dag_info() -> str:
    """
    Get comprehensive BlockDAG information.
    
    Returns information about the current state of the BlockDAG including:
    - Network name
    - Block count
    - Header count
    - Tip hashes
    - Difficulty
    - Past median time
    - Virtual parent hashes
    - Pruning point
    - Virtual DAA score
    
    Returns:
        JSON string with complete BlockDAG information
    """
    global kaspa_client
    if not kaspa_client:
        kaspa_client = KaspaClient(config.kaspa_rpc_url)
    
    result = run_async_tool(get_block_dag_info_async)
    save_api_data("block_dag_info", result)
    return json.dumps(result, indent=2)


# Resources
@mcp.resource("kaspa://status")
def get_server_status() -> str:
    """Get current server status and configuration"""
    try:
        status_info = {
            "server_name": "kaspa-mcp-server",
            "server_version": "0.1.0",
            "debug_mode": config.debug,
            "kaspa_rpc_url": config.kaspa_rpc_url,
            "available_tools": [
                "get_node_info",
                "get_block_by_hash",
                "get_latest_daa",
                "get_block_dag_info",
            ],
            "last_updated": datetime.now().isoformat(),
        }

        content = f"# Kaspa MCP Server Status\n\n"
        content += f"**Status**: ✅ Running\n"
        content += f"**Version**: {status_info['server_version']}\n"
        content += f"**Kaspa RPC**: {status_info['kaspa_rpc_url']}\n\n"

        content += f"## Available Tools ({len(status_info['available_tools'])})\n"
        for tool in status_info["available_tools"]:
            content += f"- `{tool}`\n"

        content += f"\n## Configuration\n"
        content += f"- Debug Mode: {'✅' if status_info['debug_mode'] else '❌'}\n"
        content += f"- Server Name: {status_info['server_name']}\n"

        content += f"\n## Kaspa Integration\n"
        content += f"- RPC URL: {status_info['kaspa_rpc_url']}\n"

        content += f"\n---\n"
        content += f"Last updated: {status_info['last_updated']}\n"

        return content

    except Exception as e:
        return f"# Server Status Error\n\nError retrieving server status: {str(e)}"


@mcp.resource("kaspa://docs/examples")
def get_examples() -> str:
    """Get examples of how to use this API"""
    content = f"""# Kaspa MCP Server - Usage Examples

Below are examples of how to use the available tools with this MCP Server.

## 1. Check Node Status

```python
status = get_node_info()
```

This will return the current status of the Kaspa node, including version and network information.

## 2. Get Block by Hash

```python
# Get block header only
block = get_block_by_hash("0000000000000000000000000000000000000000000000000000000000000000")

# Get block with transactions
block_with_tx = get_block_by_hash("0000000000000000000000000000000000000000000000000000000000000000", True)
```

## 3. Get Latest DAA Score

```python
# Get the current DAA (Difficulty Adjustment Algorithm) score
daa = get_latest_daa()
```

## 4. Get BlockDAG Information

```python
# Get comprehensive BlockDAG state information
dag_info = get_block_dag_info()
```

## API Response Format

All API responses follow this general format:

```json
{{
  "status": "success",
  "data": {{...}},
  "timestamp": "2023-06-15T12:34:56.789Z"
}}
```

For more information, check the server status page at kaspa://status
"""
    return content


def main():
    """Main server entry point"""

    # Configuration validation
    print("🔧 Validating configuration...")
    try:
        if not config.kaspa_rpc_url:
            print("❌ KASPA_RPC_URL not set. Using default: http://localhost:16110")
            config.kaspa_rpc_url = "http://localhost:16110"
        
        print(f"✅ Configuration valid")

        if config.debug:
            print(f"🔍 Debug mode enabled")

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)

    # Data directory setup
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"📁 Data directory: {DATA_DIR}")

    # Server startup
    print(f"\n🚀 Starting Kaspa MCP Server")
    print(f"📊 Server: kaspa-mcp-server")
    print(f"🌍 Host: 0.0.0.0:{PORT}")
    print(f"🔗 Kaspa RPC: {config.kaspa_rpc_url}")

    print(f"🎯 Transport: SSE (Server-Sent Events)")

    print(
        f"🔧 4 tools registered: get_node_info, get_block_by_hash, get_latest_daa, get_block_dag_info"
    )
    print(f"✅ Kaspa MCP Server is ready!")
    print(f"💡 Use with Claude Desktop or MCP-compatible clients")

    # Start the MCP server
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()