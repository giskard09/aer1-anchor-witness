#!/usr/bin/env python3
"""
Independent (stdlib-only) verifier for aer1-anchor-witness. Trusts nothing
in manifest.json's prose fields — only recomputes.

1. Recomputes output_hash = SHA-256(base64-decoded canonical_bytes), exactly
   per draft-zambo-aer1-26 Table 1/Section 5, and checks it matches
   manifest.json.
2. Queries Base mainnet RPC for the Anchored(bytes32,address,uint256) event
   with topics[1] == output_hash, confirming it exists on-chain.

Run: python3 verifier/verify.py [--artifacts DIR] [--rpc URL]
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.request

ANCHOR_REGISTRY = "0x49fEcA52bC634a9Ab773226D16619deC547794aa"
ANCHORED_TOPIC0 = "0xfe2289542f7a0110ac112c3a4d712afdcaaf2900a1326f4e6f340b563a0e8734"
DEFAULT_RPC = "https://mainnet.base.org"


def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "aer1-anchor-witness-verifier/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read())
    if "error" in out:
        raise RuntimeError(f"RPC {method} error: {out['error']}")
    return out["result"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default=os.environ.get("BASE_RPC", DEFAULT_RPC))
    ap.add_argument("--artifacts", default=os.path.join(os.path.dirname(__file__), "..", "artifacts"))
    args = ap.parse_args()

    art = os.path.abspath(args.artifacts)
    m = json.load(open(os.path.join(art, "manifest.json")))
    receipt = m["receipt"]

    ok = True

    canonical_bytes = base64.b64decode(receipt["canonical_bytes"])
    recomputed = hashlib.sha256(canonical_bytes).hexdigest()
    check1 = recomputed == receipt["output_hash"] == m["anchored_ref"]
    print(f"[{'PASS' if check1 else 'FAIL'}] output_hash recompute (AER-1 Table 1): {recomputed}")
    ok &= check1

    ref = "0x" + m["anchored_ref"]
    try:
        with open(os.path.join(art, "anchor.json")) as f:
            anchor = json.load(f)
    except FileNotFoundError:
        print("[SKIP] no anchor.json yet — ref not anchored on-chain")
        anchor = None

    if anchor:
        hint = int(anchor["block"])
        head = int(rpc(args.rpc, "eth_blockNumber", []), 16)
        from_block = hex(max(0, hint - 25))
        to_block = hex(min(hint + 25, head))

        logs = rpc(args.rpc, "eth_getLogs", [{
            "address": ANCHOR_REGISTRY,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [ANCHORED_TOPIC0, ref],
        }])

        check2 = bool(logs)
        if check2:
            log = logs[0]
            ts = int(log["data"], 16)
            anchored_by = "0x" + log["topics"][2][-40:]
            print(f"[PASS] on-chain Anchored event : AnchorRegistry {ANCHOR_REGISTRY} (Base 8453)")
            print(f"         tx               : {log['transactionHash']}")
            print(f"         block            : {int(log['blockNumber'], 16)}")
            print(f"         anchoredBy       : {anchored_by}")
            print(f"         block timestamp  : {ts}")
        else:
            print(f"[FAIL] no Anchored event for {ref} near block {hint}")
        ok &= check2

    print()
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
