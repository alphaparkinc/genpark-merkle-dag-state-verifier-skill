"""MCP Server for GenPark Merkle DAG State Verifier.
100% Python Standard Library.
"""

import json
import sys
from client import MerkleDAGStateVerifier

verifier = MerkleDAGStateVerifier()

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "build_merkle_tree",
                        "description": "Construct a Merkle tree from an ordered list of agent event strings",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "leaves": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["leaves"]
                        }
                    },
                    {
                        "name": "generate_merkle_proof",
                        "description": "Generate an inclusion proof for a leaf at a specified index",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "leaves": {"type": "array", "items": {"type": "string"}},
                                "leaf_index": {"type": "integer"}
                            },
                            "required": ["leaves", "leaf_index"]
                        }
                    },
                    {
                        "name": "verify_merkle_proof",
                        "description": "Verify that a leaf data matches the root hash given an inclusion proof",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "leaf_data": {"type": "string"},
                                "proof": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "position": {"type": "string"},
                                            "hash": {"type": "string"}
                                        }
                                    }
                                },
                                "expected_root": {"type": "string"}
                            },
                            "required": ["leaf_data", "proof", "expected_root"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "build_merkle_tree":
            leaves = args.get("leaves", [])
            tree = verifier.build_tree(leaves)
            # Exclude full internal levels from direct JSON output for brevity
            summary = {
                "root": tree["root"],
                "depth": tree["depth"],
                "leaf_count": tree["leaf_count"]
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(summary, indent=2)}]}
            }
        elif name == "generate_merkle_proof":
            leaves = args.get("leaves", [])
            idx = args.get("leaf_index", 0)
            tree = verifier.build_tree(leaves)
            proof = verifier.generate_proof(tree, idx)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"root": tree["root"], "proof": proof}, indent=2)}]}
            }
        elif name == "verify_merkle_proof":
            data = args.get("leaf_data", "")
            proof = args.get("proof", [])
            root = args.get("expected_root", "")
            is_valid = verifier.verify_proof(data, proof, root)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"verified": is_valid})}]}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
