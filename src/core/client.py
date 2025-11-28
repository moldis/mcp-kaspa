import re
import aiohttp
import asyncio
import time
from typing import Dict, Any, Optional, List
from kaspad_client import KaspadClient as PyKaspadClient


class KaspaClient:
    def __init__(self, rpc_url: str, kasfyi_api_key: Optional[str] = None, kasfyi_base_url: str = "https://api.kas.fyi", kasfyi_rate_limit: float = 1.0):
        self.rpc_url = rpc_url
        url_parts = rpc_url.replace('http://', '').replace('https://', '').split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) > 1 else 16110
        
        self.client = PyKaspadClient(self.host, self.port)
        
        self.kasfyi_api_key = kasfyi_api_key
        self.kasfyi_base_url = kasfyi_base_url
        self.kasfyi_rate_limit = kasfyi_rate_limit
        self.kasfyi_last_request_time = 0.0
    
    async def get_info(self) -> Dict[str, Any]:
        """Get node information"""
        response = await self.client.get_info()
        # The kaspad-client already returns dict
        return response if response else {}
    
    async def get_block(self, block_hash: str, include_transactions: bool = False) -> Dict[str, Any]:
        """Get block by hash"""
        response = await self.client.get_block(block_hash, include_transactions)
        return response if response else {}
    
    async def get_block_dag_info(self) -> Dict[str, Any]:
        """Get BlockDAG information"""
        response = await self.client.get_block_dag_info()
        return response if response else {}
    
    async def get_virtual_selected_parent_blue_score(self) -> Dict[str, Any]:
        """Get the blue score of virtual selected parent (DAA score)"""
        # kaspad-client doesn't have this specific method, so we get it from block_dag_info
        dag_info = await self.client.get_block_dag_info()
        if dag_info and 'getBlockDagInfoResponse' in dag_info:
            virtual_daa_score = dag_info['getBlockDagInfoResponse'].get('virtualDaaScore')
            # Format it similar to the expected response
            return {
                'id': dag_info.get('id'),
                'getVirtualSelectedParentBlueScoreResponse': {
                    'blueScore': virtual_daa_score
                }
            }
        return dag_info if dag_info else {}
    
    async def get_balance_by_address(self, address: str) -> Dict[str, Any]:
        """Get balance for a specific address"""
        response = await self.client.get_balance_by_address(address)
        return response if response else {}
    
    async def get_balances_by_addresses(self, addresses: list[str]) -> Dict[str, Any]:
        """Get balances for multiple addresses"""
        response = await self.client.get_balances_by_addresses(addresses)
        return response if response else {}
    
    async def get_utxos_by_addresses(self, addresses: list[str]) -> Dict[str, Any]:
        """Get UTXOs for specific addresses"""
        response = await self.client.get_utxos_by_addresses(addresses)
        return response if response else {}
    
    async def get_mempool_entries_by_addresses(
        self, 
        addresses: list[str], 
        include_orphan_pool: bool = True, 
        filter_transaction_pool: bool = True
    ) -> Dict[str, Any]:
        """Get mempool entries for specific addresses"""
        response = await self.client.get_mempool_entries_by_addresses(
            addresses, 
            include_orphan_pool=include_orphan_pool,
            filter_transaction_pool=filter_transaction_pool
        )
        return response if response else {}
    
    async def get_mempool_entries(
        self,
        include_orphan_pool: bool = True,
        filter_transaction_pool: bool = True
    ) -> Dict[str, Any]:
        """Get all mempool entries"""
        response = await self.client.get_mempool_entries(
            include_orphan_pool=include_orphan_pool,
            filter_transaction_pool=filter_transaction_pool
        )
        return response if response else {}

    async def get_mempool_entry(
        self,
        tx_id: str,
        include_orphan_pool: bool = True,
        filter_transaction_pool: bool = True
    ) -> Dict[str, Any]:
        """Get a specific transaction from mempool by transaction ID"""
        response = await self.client.get_mempool_entry(
            tx_id=tx_id,
            include_orphan_pool=include_orphan_pool,
            filter_transaction_pool=filter_transaction_pool
        )
        return response if response else {}
    
    async def get_blocks_by_blue_score_range(
        self,
        blue_score_start: int,
        blue_score_end: int,
        chain_blocks_only: bool = False,
        include_transactions: bool = False,
        include_payload: bool = False
    ) -> Dict[str, Any]:
        """Get blocks by blue score range from kas.fyi API"""
        if not self.kasfyi_api_key:
            raise ValueError("KASFYI_API_KEY environment variable is required for kas.fyi API access")
        
        if blue_score_end - blue_score_start > 100:
            raise ValueError("Blue score range cannot exceed 100 blocks")
        
        current_time = time.time()
        time_since_last_request = current_time - self.kasfyi_last_request_time
        min_interval = 1.0 / self.kasfyi_rate_limit
        
        if time_since_last_request < min_interval:
            await asyncio.sleep(min_interval - time_since_last_request)
        
        url = f"{self.kasfyi_base_url}/v1/blocks/blue-score/{blue_score_start}/{blue_score_end}"
        
        params = {
            "chain_blocks_only": str(chain_blocks_only).lower(),
            "include_transactions": str(include_transactions).lower(),
            "include_payload": str(include_payload).lower()
        }
        
        headers = {
            "x-api-key": self.kasfyi_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                self.kasfyi_last_request_time = time.time()
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"kas.fyi API error (HTTP {response.status}): {error_text}")
    
    @staticmethod
    def validate_kaspa_address(address: str) -> Dict[str, Any]:
        """
        Validate Kaspa address format
        Returns validation result with details
        """
        # Kaspa address prefixes for different networks
        valid_prefixes = {
            'kaspa': 'mainnet',
            'kaspatest': 'testnet', 
            'kaspasim': 'simnet',
            'kaspadev': 'devnet'
        }
        
        # Check if address has the kaspa: scheme
        if ':' not in address:
            return {
                "valid": False,
                "error": "Missing network prefix (should start with 'kaspa:', 'kaspatest:', etc.)"
            }
        
        try:
            prefix, address_part = address.split(':', 1)
        except ValueError:
            return {
                "valid": False,
                "error": "Invalid address format"
            }
        
        # Validate prefix
        if prefix not in valid_prefixes:
            return {
                "valid": False,
                "error": f"Invalid network prefix '{prefix}'. Valid prefixes: {list(valid_prefixes.keys())}"
            }
        
        # Basic bech32 format validation
        # Kaspa addresses should be around 61-63 characters after the prefix
        if len(address_part) < 50 or len(address_part) > 70:
            return {
                "valid": False,
                "error": "Address length is invalid for Kaspa format"
            }
        
        # Check for valid bech32 characters (a-z, 0-9, no 'b', 'i', 'o', '1')
        valid_bech32_pattern = re.compile(r'^[a-z0-9]+$')
        if not valid_bech32_pattern.match(address_part):
            return {
                "valid": False,
                "error": "Address contains invalid characters for bech32 format"
            }
        
        # Check for forbidden bech32 characters
        forbidden_chars = set('1bio')
        if any(char in address_part for char in forbidden_chars):
            return {
                "valid": False,
                "error": "Address contains forbidden bech32 characters (1, b, i, o)"
            }
        
        return {
            "valid": True,
            "network": valid_prefixes[prefix],
            "prefix": prefix,
            "address": address_part,
            "full_address": address
        }