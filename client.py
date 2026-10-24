"""Merkle DAG State Verifier Engine.
100% Python Standard Library.
"""

import hashlib
from typing import Dict, List, Any

class MerkleDAGStateVerifier:
    """Tamper-evident Merkle tree engine for agent execution histories and state proofs."""

    @staticmethod
    def hash_leaf(data: str) -> str:
        return hashlib.sha256(("leaf:" + data).encode("utf-8")).hexdigest()

    @staticmethod
    def hash_pair(left: str, right: str) -> str:
        return hashlib.sha256(("node:" + left + ":" + right).encode("utf-8")).hexdigest()

    def build_tree(self, leaves: List[str]) -> Dict[str, Any]:
        if not leaves:
            return {"root": "", "depth": 0, "leaf_count": 0, "levels": []}
        current_level = [self.hash_leaf(l) for l in leaves]
        levels = [current_level]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else left
                next_level.append(self.hash_pair(left, right))
            levels.append(next_level)
            current_level = next_level
        return {
            "root": levels[-1][0],
            "depth": len(levels),
            "leaf_count": len(leaves),
            "levels": levels
        }

    def generate_proof(self, tree_data: Dict[str, Any], leaf_index: int) -> List[Dict[str, str]]:
        levels = tree_data["levels"]
        if not levels or leaf_index < 0 or leaf_index >= len(levels[0]):
            return []
        proof = []
        idx = leaf_index
        for level in levels[:-1]:
            if idx % 2 == 0:
                sibling_idx = idx + 1 if idx + 1 < len(level) else idx
                proof.append({"position": "right", "hash": level[sibling_idx]})
            else:
                sibling_idx = idx - 1
                proof.append({"position": "left", "hash": level[sibling_idx]})
            idx //= 2
        return proof

    def verify_proof(self, leaf_data: str, proof: List[Dict[str, str]], expected_root: str) -> bool:
        curr_hash = self.hash_leaf(leaf_data)
        for item in proof:
            pos = item["position"]
            sibling = item["hash"]
            if pos == "right":
                curr_hash = self.hash_pair(curr_hash, sibling)
            else:
                curr_hash = self.hash_pair(sibling, curr_hash)
        return curr_hash == expected_root
