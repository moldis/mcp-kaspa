#!/usr/bin/env python3
"""
Unit tests for Kaspa MCP Server client
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

from src.core.client import KaspaClient

kaspa_node_url = "" # TODO replace with your actual node URL

class TestKaspaClient:
    """Test cases for KaspaClient"""
    
    def get_client(self):
        """Create a KaspaClient instance for testing"""
        return KaspaClient(kaspa_node_url)
    
    async def test_get_node_info(self):
        """Test getting node information from Kaspa RPC server"""
        kaspa_client = self.get_client()
        
        # Act
        result = await kaspa_client.get_info()
        
        # Assert
        assert result is not None, "Node info should not be None"
        assert isinstance(result, dict), "Node info should be a dictionary"
        
        # Check for expected fields in the response
        print(f"\n✅ Successfully retrieved node info:")
        print(f"   Response keys: {list(result.keys())}")
        
        # Log the full response for debugging
        if result:
            for key, value in result.items():
                print(f"   {key}: {value}")
        
        return result


# Pytest fixtures (only used if pytest is available)
if PYTEST_AVAILABLE:
    @pytest.fixture
    def kaspa_client():
        """Create a KaspaClient instance for testing"""
        return KaspaClient("http://23.111.147.178:16110")
    
    @pytest.mark.asyncio
    async def test_get_node_info_pytest(kaspa_client):
        """Test getting node information from Kaspa RPC server (pytest version)"""
        test = TestKaspaClient()
        test.get_client = lambda: kaspa_client
        await test.test_get_node_info()


if __name__ == "__main__":
    # Run the test directly for quick testing
    async def main():
        test = TestKaspaClient()
        try:
            print("🔍 Testing get_node_info with server 23.111.147.178:16110...")
            print("Debug: Creating client...")
            client = test.get_client()
            print(f"Debug: Client created with host={client.host}, port={client.port}")
            print("Debug: Making request...")
            result = await client.get_info()
            print(f"Debug: Raw result type: {type(result)}")
            print(f"Debug: Raw result: {result}")
            
            if result is None:
                print("❌ Error: Result is None")
                sys.exit(1)
            
            print("\n✅ Test passed!")
            print(f"   Response: {result}")
            return result
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(main())
