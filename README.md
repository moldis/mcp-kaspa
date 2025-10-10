# Kaspa MCP Server

MCP server for Kaspa blockchain node RPC integration, providing tools to interact with Kaspa nodes via RPC calls.

## 🚀 Quick Setup

### Prerequisites

- **For uvx method**: Install [uv](https://docs.astral.sh/uv/) which includes uvx
- **For Docker method**: Install [Docker](https://docs.docker.com/get-docker/)
- **Kaspa RPC endpoint**: Access to a Kaspa node RPC (local or remote)

### Installation Methods

Choose one of the following methods based on your MCP client:

## 📱 Claude Desktop

Add to your Claude Desktop configuration file:

**Location**: 
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Method 1: Using uvx (Recommended)
```json
{
  "mcpServers": {
    "kaspa": {
      "command": "uvx",
      "args": ["--from", "/path/to/mcp-kaspa", "kaspa-mcp-server"],
      "env": {
        "KASPA_RPC_URL": "http://localhost:16110"
      }
    }
  }
}
```

### Method 2: Using Docker
```json
{
  "mcpServers": {
    "kaspa": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env", "KASPA_RPC_URL=http://host.docker.internal:16110",
        "kaspa-mcp-server:latest"
      ]
    }
  }
}
```

## 🖥️ Cursor IDE

Add to your Cursor settings:

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "MCP" or go to Extensions → MCP
3. Add new server configuration:

### Method 1: Using uvx
```json
{
  "mcp.servers": {
    "kaspa": {
      "command": "uvx",
      "args": ["--from", "/path/to/mcp-kaspa", "kaspa-mcp-server"],
      "env": {
        "KASPA_RPC_URL": "http://localhost:16110"
      }
    }
  }
}
```

### Method 2: Using Docker
```json
{
  "mcp.servers": {
    "kaspa": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env", "KASPA_RPC_URL=http://host.docker.internal:16110",
        "kaspa-mcp-server:latest"
      ]
    }
  }
}
```

## 🎯 Qoder IDE

Add this MCP server in Qoder settings:

1. Open Qoder Settings (⌘⇧, on macOS or Ctrl+Shift+, on Windows)
2. Navigate to MCP section
3. Click "Add Server"

### Method 1: Using uvx (Recommended)
- **Name**: Kaspa MCP Server
- **Command**: uvx
- **Arguments**: 
  - `--from`
  - `/path/to/mcp-kaspa`
  - `kaspa-mcp-server`
- **Environment Variables**:
  - `KASPA_RPC_URL=http://localhost:16110`

### Method 2: Using Docker
- **Name**: Kaspa MCP Server
- **Command**: docker
- **Arguments**:
  - `run`
  - `-i`
  - `--rm`
  - `--env`
  - `KASPA_RPC_URL=http://host.docker.internal:16110`
  - `kaspa-mcp-server:latest`

### Method 3: Direct Python (Fallback)
If uvx doesn't work:
- **Name**: Kaspa MCP Server
- **Command**: python3
- **Arguments**: 
  - `-m`
  - `src.main`
- **Environment Variables**:
  - `KASPA_RPC_URL=http://localhost:16110`

---

**Configuration Notes for All IDEs**:
- Replace `/path/to/mcp-kaspa` with the actual absolute path to your cloned repository
- For Windows paths, use backslashes: `C:\path\to\mcp-kaspa`
- For Docker: use `host.docker.internal` instead of `localhost` to access host services
- Ensure the path points to the directory containing `pyproject.toml` for uvx method

## 🐳 Docker Support

### Build the Docker Image

```bash
cd /path/to/mcp-kaspa
docker build -t kaspa-mcp-server:latest .
```

### Run with Docker

```bash
# Test with a local Kaspa node
docker run -i --rm --env KASPA_RPC_URL=http://host.docker.internal:16110 kaspa-mcp-server:latest

# Test with a remote Kaspa node
docker run -i --rm --env KASPA_RPC_URL=http://your-kaspa-node:16110 kaspa-mcp-server:latest
```

### Docker Notes

- Use `host.docker.internal` instead of `localhost` when connecting to services on your host machine
- The Docker image includes all necessary dependencies
- Perfect for isolated execution environments

## 🌍 Network Configuration

### Kaspa RPC Endpoints

**Local Node**:
- Default: `http://localhost:16110`
- Docker: `http://host.docker.internal:16110`

**Public Endpoints** (examples):
- `http://23.111.147.178:16110`
- `https://kaspa-rpc.example.com`

### Environment Variables

- `KASPA_RPC_URL`: Kaspa node RPC endpoint (required)
- `DEBUG`: Set to `true` for verbose logging (optional)

## 🛠 Available Tools

1. **get_node_info** - Get Kaspa node information and connection status
2. **get_block_by_hash** - Get detailed information about a specific block by its hash
3. **get_latest_daa** - Get the latest DAA (Difficulty Adjustment Algorithm) score
4. **get_block_dag_info** - Get comprehensive BlockDAG information  
5. **validate_address** - Validate a Kaspa address format
6. **get_address_balance** - Get balance for a specific Kaspa address
7. **get_address_utxos** - Get UTXOs (Unspent Transaction Outputs) for specific addresses
8. **get_mempool_transactions** - Get mempool transactions for specific addresses

## 📚 Resources

- `kaspa://status` - Server status and configuration
- `kaspa://docs/examples` - Usage examples

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-kaspa

# Build Docker image (optional)
docker build -t kaspa-mcp-server:latest .
```

## 🔍 Troubleshooting

### Common Issues

**"Broken Pipe" Error**:
- ✅ **Fixed**: The server now includes comprehensive error handling
- ✅ **Fixed**: Graceful startup process with proper stdio communication
- ✅ **Fixed**: Connection timeouts and better RPC error handling

**"uvx not found"**:
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Unix) or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
- Use Docker method as alternative
- Use direct Python method as fallback

**"Cannot connect to Kaspa RPC"**:
- Verify your Kaspa node is running and accessible
- Check firewall settings
- For Docker: use `host.docker.internal` instead of `localhost`
- Server will start but functionality will be limited until RPC is accessible

**MCP Client Can't Find Server**:
- Ensure the path to mcp-kaspa directory is correct
- For uvx: path should point to directory containing `pyproject.toml`
- For Docker: ensure image is built with correct tag
- Check MCP client logs for detailed error messages

### Verification Steps

1. **Test uvx installation**:
   ```bash
   cd /path/to/mcp-kaspa
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | uvx --from . kaspa-mcp-server
   ```

2. **Test Docker setup**:
   ```bash
   docker run -i --rm --env KASPA_RPC_URL=http://localhost:16110 kaspa-mcp-server:latest
   ```

3. **Check server response**:
   Should return a JSON response with `"result":{"protocolVersion":"2025-06-18"...}`

## 📝 Example Usage

Once configured in your MCP client, you can use tools like:

### Basic Node Information
```
get_node_info()
```

### Address Validation
```
validate_address("kaspa:qpauqsvk7yf9unexwmxsnmg547mhyga37csh0kj53q6xxgl24ydxjsgzthw5j")
```

### Get Latest DAA Score
```
get_latest_daa()
```

### Get Block Information
```
get_block_by_hash("block_hash_here")
```

### Check Address Balance
```
get_address_balance("kaspa:your_address_here")
```

### Get UTXOs
```
get_address_utxos(["kaspa:address1", "kaspa:address2"])
```

## 📚 Additional Resources

- [Kaspa Documentation](https://kaspa.org/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/desktop-app#mcp)

## 📝 License

MIT License - see LICENSE file for details.

