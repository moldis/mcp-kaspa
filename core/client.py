import aiohttp
import json
from typing import Dict, Any, Optional


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