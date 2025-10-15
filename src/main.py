#!/usr/bin/env python3
"""
Kaspa MCP Server - MCP Server
MCP server for Kaspa node RPC integration

Author: Artem Bogomaz <artembogomaz@gmail.com>
Version: 0.1.0
"""
import asyncio
import json
import logging
import sys
import signal
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import config
from core.client import KaspaClient

# MCP imports
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kaspa-mcp-server")

# Initialize the MCP server
server = Server("kaspa-mcp-server")

# Global Kaspa client
kaspa_client: Optional[KaspaClient] = None

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_kaspa_client() -> KaspaClient:
    """Get or create Kaspa client instance"""
    global kaspa_client
    if kaspa_client is None:
        kaspa_client = KaspaClient(config.kaspa_rpc_url)
    return kaspa_client


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_node_info",
            description="Get Kaspa node information and connection status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get_block_by_hash",
            description="Get detailed information about a specific block by its hash",
            inputSchema={
                "type": "object",
                "properties": {
                    "block_hash": {
                        "type": "string",
                        "description": "The hash of the block to retrieve",
                    },
                    "include_transactions": {
                        "type": "boolean",
                        "description": "Whether to include transaction details",
                        "default": False,
                    },
                },
                "required": ["block_hash"],
            },
        ),
        types.Tool(
            name="get_latest_daa",
            description="Get the latest DAA (Difficulty Adjustment Algorithm) score",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get_block_dag_info",
            description="Get comprehensive BlockDAG information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="validate_address",
            description="Validate a Kaspa address format",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Kaspa address to validate (e.g., kaspa:qpauqsvk7yf9unexwmxsnmg547mhyga37csh0kj53q6xxgl24ydxjsgzthw5j)",
                    },
                },
                "required": ["address"],
            },
        ),
        types.Tool(
            name="get_address_balance",
            description="Get balance for a specific Kaspa address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The Kaspa address to check balance for",
                    },
                },
                "required": ["address"],
            },
        ),
        types.Tool(
            name="get_address_utxos",
            description="Get UTXOs (Unspent Transaction Outputs) for specific addresses",
            inputSchema={
                "type": "object",
                "properties": {
                    "addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Kaspa addresses to get UTXOs for",
                    },
                },
                "required": ["addresses"],
            },
        ),
        types.Tool(
            name="get_mempool_transactions",
            description="Get mempool transactions for specific addresses",
            inputSchema={
                "type": "object",
                "properties": {
                    "addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Kaspa addresses to get mempool transactions for",
                    },
                    "include_orphan_pool": {
                        "type": "boolean",
                        "description": "Include transactions from orphan pool",
                        "default": True,
                    },
                },
                "required": ["addresses"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}

    try:
        client = get_kaspa_client()

        if name == "get_node_info":
            result = await client.get_info()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "node_info": result,
                    }, indent=2)
                )
            ]

        elif name == "get_block_by_hash":
            block_hash = arguments.get("block_hash")
            include_transactions = arguments.get("include_transactions", False)
            
            if not block_hash:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "block_hash is required"
                        }, indent=2)
                    )
                ]

            result = await client.get_block(block_hash, include_transactions)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "block_hash": block_hash,
                        "block": result,
                    }, indent=2)
                )
            ]

        elif name == "get_latest_daa":
            result = await client.get_virtual_selected_parent_blue_score()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "blue_score": result.get("blueScore"),
                    }, indent=2)
                )
            ]

        elif name == "get_block_dag_info":
            result = await client.get_block_dag_info()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "dag_info": result,
                    }, indent=2)
                )
            ]

        elif name == "validate_address":
            address = arguments.get("address")
            
            if not address:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "address is required"
                        }, indent=2)
                    )
                ]
            
            validation_result = client.validate_kaspa_address(address)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "validation": validation_result,
                    }, indent=2)
                )
            ]

        elif name == "get_address_balance":
            address = arguments.get("address")
            
            if not address:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "address is required"
                        }, indent=2)
                    )
                ]
            
            # First validate the address
            validation = client.validate_kaspa_address(address)
            if not validation.get("valid"):
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"Invalid address: {validation.get('error')}"
                        }, indent=2)
                    )
                ]
            
            result = await client.get_balance_by_address(address)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "address": address,
                        "balance": result,
                    }, indent=2)
                )
            ]

        elif name == "get_address_utxos":
            addresses = arguments.get("addresses", [])
            
            if not addresses:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "addresses list is required"
                        }, indent=2)
                    )
                ]
            
            # Validate all addresses
            invalid_addresses = []
            for addr in addresses:
                validation = client.validate_kaspa_address(addr)
                if not validation.get("valid"):
                    invalid_addresses.append(f"{addr}: {validation.get('error')}")
            
            if invalid_addresses:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "Invalid addresses found",
                            "invalid_addresses": invalid_addresses
                        }, indent=2)
                    )
                ]
            
            result = await client.get_utxos_by_addresses(addresses)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "addresses": addresses,
                        "utxos": result,
                    }, indent=2)
                )
            ]

        elif name == "get_mempool_transactions":
            addresses = arguments.get("addresses", [])
            include_orphan_pool = arguments.get("include_orphan_pool", True)
            
            if not addresses:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "addresses list is required"
                        }, indent=2)
                    )
                ]
            
            # Validate all addresses
            invalid_addresses = []
            for addr in addresses:
                validation = client.validate_kaspa_address(addr)
                if not validation.get("valid"):
                    invalid_addresses.append(f"{addr}: {validation.get('error')}")
            
            if invalid_addresses:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "Invalid addresses found",
                            "invalid_addresses": invalid_addresses
                        }, indent=2)
                    )
                ]
            
            result = await client.get_mempool_entries_by_addresses(addresses, include_orphan_pool)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "addresses": addresses,
                        "mempool_transactions": result,
                    }, indent=2)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )
        ]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri="kaspa://status",
            name="Server Status",
            description="Current server status and configuration",
            mimeType="text/markdown",
        ),
        types.Resource(
            uri="kaspa://docs/examples",
            name="Usage Examples",
            description="Examples of how to use the Kaspa MCP server",
            mimeType="text/markdown",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource requests"""
    if uri == "kaspa://status":
        return f"""# Kaspa MCP Server Status

**Status**: ✅ Running
**Version**: 0.1.0
**Kaspa RPC**: {config.kaspa_rpc_url}

## Available Tools
- `get_node_info` - Node information and status
- `get_block_by_hash` - Get block details by hash
- `get_latest_daa` - Get latest DAA score
- `get_block_dag_info` - Get BlockDAG information
- `validate_address` - Validate Kaspa address format
- `get_address_balance` - Get balance for specific address
- `get_address_utxos` - Get UTXOs for addresses
- `get_mempool_transactions` - Get mempool transactions by address

## Configuration
- Debug Mode: {'✅' if config.debug else '❌'}
- Kaspa RPC URL: {config.kaspa_rpc_url}
"""

    elif uri == "kaspa://docs/examples":
        return """# Kaspa MCP Server - Usage Examples

## 1. Check Node Status
```
get_node_info()
```

## 2. Get Block by Hash
```
get_block_by_hash(block_hash="0000000000000000000000000000000000000000000000000000000000000000")
```

## 3. Get Latest DAA Score
```
get_latest_daa()
```

## 4. Get BlockDAG Information
```
get_block_dag_info()
```
"""

    else:
        raise ValueError(f"Unknown resource: {uri}")


def main():
    """Entry point for the application"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        sys.exit(1)


async def async_main():
    """Main server entry point"""
    try:
        # Configuration validation
        logger.info("🔧 Validating configuration...")
        
        if not config.kaspa_rpc_url:
            logger.warning("❌ KASPA_RPC_URL not set. Using default: http://localhost:16110")
            config.kaspa_rpc_url = "http://localhost:16110"
        
        logger.info(f"✅ Configuration valid")
        logger.info(f"🔗 Kaspa RPC: {config.kaspa_rpc_url}")
        
        if config.debug:
            logger.info(f"🔍 Debug mode enabled")

        # Test Kaspa connection before starting MCP server
        logger.info("🔍 Testing Kaspa RPC connection...")
        try:
            client = get_kaspa_client()
            await client.get_info()
            logger.info("✅ Kaspa RPC connection successful")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kaspa RPC: {e}")
            logger.error("MCP server will start but Kaspa functionality may be limited")

        logger.info("🚀 Starting MCP server...")

        # Run the server using stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="kaspa-mcp-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"❌ Fatal error during server startup: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()