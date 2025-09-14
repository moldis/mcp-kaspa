#!/usr/bin/env python3
"""Test script to verify Kaspa RPC connection"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.client import KaspaClient
from core.config import config


async def test_connection():
    print(f"Testing connection to Kaspa node at: {config.kaspa_rpc_url}")
    
    client = KaspaClient(config.kaspa_rpc_url)
    
    try:
        # Test get_info
        print("\n1. Testing get_info...")
        info = await client.get_info()
        print(f"✅ Node info retrieved: {info}")
        
        # Test get_block_dag_info
        print("\n2. Testing get_block_dag_info...")
        dag_info = await client.get_block_dag_info()
        print(f"✅ DAG info retrieved: Virtual DAA Score = {dag_info.get('virtualDaaScore', 'N/A')}")
        
        # Test get_virtual_selected_parent_blue_score
        print("\n3. Testing get_virtual_selected_parent_blue_score...")
        blue_score_result = await client.get_virtual_selected_parent_blue_score()
        print(f"✅ Blue score (DAA) retrieved: {blue_score_result.get('blueScore', 'N/A')}")
        
        print("\n✅ All tests passed! Kaspa node is accessible.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Kaspa node is running")
        print("2. RPC is enabled")
        print("3. Correct RPC URL is set in KASPA_RPC_URL environment variable")


if __name__ == "__main__":
    asyncio.run(test_connection())