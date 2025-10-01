import aiohttp
import json
import re
from typing import Dict, Any, Optional, List


class KaspaClient:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.headers = {"Content-Type": "application/json"}
    
    async def _rpc_call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make RPC call to Kaspa node"""
        payload = {
            "jsonrpc": "1.0",
            "id": "kaspa-mcp",
            "method": method,
            "params": params or []
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json=payload, headers=self.headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"RPC call failed with status {response.status}: {text}")
                
                result = await response.json()
                
                if "error" in result and result["error"]:
                    raise Exception(f"RPC error: {result['error']}")
                
                return result.get("result", {})
    
    async def get_info(self) -> Dict[str, Any]:
        """Get node information"""
        return await self._rpc_call("getInfoRequest")
    
    async def get_block(self, block_hash: str, include_transactions: bool = False) -> Dict[str, Any]:
        """Get block by hash"""
        params = {
            "hash": block_hash,
            "includeTransactions": include_transactions
        }
        return await self._rpc_call("getBlockRequest", params)
    
    async def get_block_dag_info(self) -> Dict[str, Any]:
        """Get BlockDAG information"""
        return await self._rpc_call("getBlockDagInfoRequest")
    
    async def get_virtual_selected_parent_blue_score(self) -> Dict[str, Any]:
        """Get the blue score of virtual selected parent (DAA score)"""
        return await self._rpc_call("getVirtualSelectedParentBlueScoreRequest")
    
    async def get_balance_by_address(self, address: str) -> Dict[str, Any]:
        """Get balance for a specific address"""
        params = {"address": address}
        return await self._rpc_call("getBalanceByAddressRequest", params)
    
    async def get_balances_by_addresses(self, addresses: list[str]) -> Dict[str, Any]:
        """Get balances for multiple addresses"""
        params = {"addresses": addresses}
        return await self._rpc_call("getBalancesByAddressesRequest", params)
    
    async def get_utxos_by_addresses(self, addresses: list[str]) -> Dict[str, Any]:
        """Get UTXOs for specific addresses"""
        params = {"addresses": addresses}
        return await self._rpc_call("getUtxosByAddressesRequest", params)
    
    async def get_mempool_entries_by_addresses(self, addresses: list[str], include_orphan_pool: bool = True, filter_transaction_pool: bool = True) -> Dict[str, Any]:
        """Get mempool entries for specific addresses"""
        params = {
            "addresses": addresses,
            "includeOrphanPool": include_orphan_pool,
            "filterTransactionPool": filter_transaction_pool
        }
        return await self._rpc_call("getMempoolEntriesByAddressesRequest", params)
    
    async def get_mempool_entries(self, include_orphan_pool: bool = True, filter_transaction_pool: bool = True) -> Dict[str, Any]:
        """Get all mempool entries"""
        params = {
            "includeOrphanPool": include_orphan_pool,
            "filterTransactionPool": filter_transaction_pool
        }
        return await self._rpc_call("getMempoolEntriesRequest", params)
    
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