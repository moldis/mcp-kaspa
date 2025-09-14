# Kaspa MCP Server

MCP server for Kaspa node RPC integration. This server provides tools to interact with a Kaspa node via the Model Context Protocol (MCP).

## Features

- Get node information and status
- Retrieve blocks by hash
- Get latest DAA (Difficulty Adjustment Algorithm) score
- Access BlockDAG information

## Installation

1. Clone this repository
2. Run the setup script:
   ```bash
   cd /path/to/mcp-kaspa
   ./setup.sh
   ```
   
   This will create a virtual environment and install all dependencies.

## Configuration

Set the following environment variables:

```bash
# Kaspa RPC URL (default: http://localhost:16110)
KASPA_RPC_URL=http://localhost:16110

# Debug mode (default: false)
DEBUG=false
```

## Usage

### Running the server

```bash
python main.py
```

### Connecting to AI Assistants

#### Claude Desktop

1. Open Claude Desktop settings
2. Navigate to Developer → Model Context Protocol
3. Add a new MCP server with the following configuration:

```json
{
  "mcpServers": {
    "kaspa": {
      "command": "python",
      "args": ["main.py"],
      "env": {
        "KASPA_RPC_URL": "kaspa-rpc-node-url",
      }
    }
  }
}
```

4. Restart Claude Desktop
5. The Kaspa tools will be available in your conversations

#### Other MCP-Compatible Clients

For other AI assistants that support MCP:

1. Configure the server endpoint:
   - Command: `python /path/to/mcp-kaspa/main.py`
   - Transport: SSE (Server-Sent Events)
   - Port: 8000 (or custom via PORT env var)

2. Set environment variables:
   ```bash
   export KASPA_RPC_URL=http://localhost:16110
   export PORT=8000
   ```

3. The server exposes the following MCP tools:
   - `get_node_info`
   - `get_block_by_hash`
   - `get_latest_daa`
   - `get_block_dag_info`

### Available Tools

1. **get_node_info** - Get Kaspa node information and connection status
2. **get_block_by_hash** - Get detailed information about a specific block by its hash
3. **get_latest_daa** - Get the latest DAA (Difficulty Adjustment Algorithm) score
4. **get_block_dag_info** - Get comprehensive BlockDAG information

### Example Usage

```python
# Get node information
node_info = get_node_info()

# Get block by hash
block = get_block_by_hash("0000000000000000000000000000000000000000000000000000000000000000")

# Get block with transactions
block_with_tx = get_block_by_hash("0000000000000000000000000000000000000000000000000000000000000000", True)

# Get latest DAA score
daa = get_latest_daa()

# Get BlockDAG info
dag_info = get_block_dag_info()
```

## MCP Resources

- `kaspa://status` - Server status and configuration
- `kaspa://docs/examples` - Usage examples

## Requirements

- Python 3.8+
- Running Kaspa node with RPC enabled
- MCP-compatible client (e.g., Claude Desktop)

## License

MIT