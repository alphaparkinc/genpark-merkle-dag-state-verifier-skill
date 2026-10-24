"""Example usage for GenPark Merkle DAG State Verifier.
100% Python Standard Library.
"""

from client import MerkleDAGStateVerifier

def main():
    verifier = MerkleDAGStateVerifier()
    events = [
        "step_1:init_session",
        "step_2:retrieve_user_context",
        "step_3:invoke_llm_tool",
        "step_4:write_audit_log"
    ]
    
    tree = verifier.build_tree(events)
    print("Merkle Root:", tree["root"])
    
    proof = verifier.generate_proof(tree, 2)
    print("Proof for leaf 2 (invoke_llm_tool):", proof)
    
    valid = verifier.verify_proof("step_3:invoke_llm_tool", proof, tree["root"])
    print("Proof Valid:", valid)
    
    tampered_valid = verifier.verify_proof("step_3:invoke_tampered_tool", proof, tree["root"])
    print("Tampered Proof Valid:", tampered_valid)

if __name__ == "__main__":
    main()
