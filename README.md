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

#### Docker (Recommended)
```bash
# Build the image
./docker-build.sh

# The server is ready for Claude Desktop
```

#### Manual Python
```bash
./setup.sh  # Install dependencies
python main.py
```

### Connecting to AI Assistants

#### Claude Desktop with Docker (Recommended)

1. Build the Docker image: `./docker-build.sh`
2. Open Claude Desktop settings
3. Navigate to Developer → Model Context Protocol
4. Add this configuration:

```json
{
  "mcpServers": {
    "kaspa": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env", "KASPA_RPC_URL=http://host.docker.internal:16110",
        "kaspa-mcp-server:latest"
      ]
    }
  }
}
```

5. Restart Claude Desktop
6. The Kaspa tools will be available in your conversations

#### Claude Desktop with Python

```json
{
  "mcpServers": {
    "kaspa": {
      "command": "/Users/artem_bogomaz/Documents/GIT2/mcp-kaspa/venv/bin/python",
      "args": ["/Users/artem_bogomaz/Documents/GIT2/mcp-kaspa/main.py"],
      "env": {
        "KASPA_RPC_URL": "http://localhost:16110"
      }
    }
  }
}
```

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

#### Node Information
1. **get_node_info** - Get Kaspa node information and connection status
2. **get_block_by_hash** - Get detailed information about a specific block by its hash
3. **get_latest_daa** - Get the latest DAA (Difficulty Adjustment Algorithm) score
4. **get_block_dag_info** - Get comprehensive BlockDAG information

#### Address Operations
5. **validate_address** - Validate Kaspa address format and network type
6. **get_address_balance** - Get balance for a specific Kaspa address
7. **get_address_utxos** - Get UTXOs (Unspent Transaction Outputs) for addresses
8. **get_mempool_transactions** - Get pending transactions in mempool for specific addresses

### Example Usage

```python
# Node operations
node_info = get_node_info()
block = get_block_by_hash("block_hash_here")
daa = get_latest_daa()
dag_info = get_block_dag_info()

# Address operations
validation = validate_address("kaspa:qpauqsvk7yf9unexwmxsnmg547mhyga37csh0kj53q6xxgl24ydxjsgzthw5j")
balance = get_address_balance("kaspa:qpauqsvk7yf9unexwmxsnmg547mhyga37csh0kj53q6xxgl24ydxjsgzthw5j")
utxos = get_address_utxos(["kaspa:address1", "kaspa:address2"])
mempool_txs = get_mempool_transactions(["kaspa:address1"])
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