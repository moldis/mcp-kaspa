import re
from typing import Dict, Any, Optional, List
from kaspad_client import KaspadClient as PyKaspadClient


class KaspaClient:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        # Extract host and port from URL
        # Format: http://host:port or https://host:port
        url_parts = rpc_url.replace('http://', '').replace('https://', '').split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) > 1 else 16110
        
        # Initialize the py-kaspad-client
        self.client = PyKaspadClient(self.host, self.port)
    
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
        response = await self.client.get_virtual_selected_parent_blue_score()
        return response if response else {}
    
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