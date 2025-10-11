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

kaspa_node_url = ""

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
    
    async def test_get_latest_daa(self):
        """Test getting latest DAA (blue score) from Kaspa RPC server"""
        kaspa_client = self.get_client()
        
        # Act
        result = await kaspa_client.get_virtual_selected_parent_blue_score()
        
        # Assert
        assert result is not None, "DAA result should not be None"
        assert isinstance(result, dict), "DAA result should be a dictionary"
        
        # Check for expected fields
        print(f"\n✅ Successfully retrieved latest DAA:")
        print(f"   Response keys: {list(result.keys())}")
        
        # Log the full response
        if result:
            for key, value in result.items():
                print(f"   {key}: {value}")
        
        # Check if blue score exists in response
        if 'getVirtualSelectedParentBlueScoreResponse' in result:
            blue_score_data = result['getVirtualSelectedParentBlueScoreResponse']
            if 'blueScore' in blue_score_data:
                print(f"   Blue Score: {blue_score_data['blueScore']}")
        
        return result
    
    async def test_get_block_dag_info(self):
        """Test getting BlockDAG information from Kaspa RPC server"""
        kaspa_client = self.get_client()
        
        # Act
        result = await kaspa_client.get_block_dag_info()
        
        # Assert
        assert result is not None, "BlockDAG info should not be None"
        assert isinstance(result, dict), "BlockDAG info should be a dictionary"
        
        # Check for expected fields
        print(f"\n✅ Successfully retrieved BlockDAG info:")
        print(f"   Response keys: {list(result.keys())}")
        
        # Log the full response
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
    # Run the tests directly for quick testing
    async def main():
        test = TestKaspaClient()
        tests_passed = 0
        tests_failed = 0
        
        print("\n" + "=" * 60)
        print("Running Kaspa Client Tests")
        print(f"Server: {kaspa_node_url}")
        print("=" * 60)
        
        # Test 1: get_node_info
        try:
            print("\n🔍 Test 1: Getting node info...")
            result = await test.test_get_node_info()
            print("✅ Test 1 PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 1 FAILED: {e}")
            tests_failed += 1
        
        # Test 2: get_latest_daa
        try:
            print("\n🔍 Test 2: Getting latest DAA (blue score)...")
            result = await test.test_get_latest_daa()
            print("✅ Test 2 PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 2 FAILED: {e}")
            tests_failed += 1
        
        # Test 3: get_block_dag_info
        try:
            print("\n🔍 Test 3: Getting BlockDAG info...")
            result = await test.test_get_block_dag_info()
            print("✅ Test 3 PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 3 FAILED: {e}")
            tests_failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"✅ Passed: {tests_passed}")
        print(f"❌ Failed: {tests_failed}")
        print(f"Total: {tests_passed + tests_failed}")
        print("=" * 60)
        
        if tests_failed > 0:
            sys.exit(1)
        else:
            print("\n✨ All tests passed successfully!")
    
    asyncio.run(main())
