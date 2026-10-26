#!/usr/bin/env python3
"""
Produces a synthetic AER-1 receipt (per draft-zambo-aer1-26, Table 1 / Section
5) and anchors its own `output_hash` directly into AnchorRegistry — no
wrapping, no action_ref preimage, no translation. AER-1 already defines
output_hash as SHA-256(canonical_bytes); AnchorRegistry.anchor(bytes32)
takes exactly that shape.

PROVENANCE: this is NOT captured from a running AER-1 client/SDK. The
receipt shape (id, receipt_schema_version, created_at, tool, provenance_class,
canonical_bytes, output_hash, metadata_hash, verification_status) is taken
directly from draft-zambo-aer1-26 Table 1, read from the published I-D at
https://datatracker.ietf.org/doc/draft-zambo-aer1/ . No claim that AER-1 or
Brennan Zambo has integrated, endorsed, or adopted AnchorRegistry.
"""
import base64
import hashlib
import json
import os
import sys
import uuid

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "artifacts"
os.makedirs(OUT_DIR, exist_ok=True)


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# --- Synthetic AER-1 receipt body, per spec Table 1 -------------------------
canonical_payload = {
    "tool_name": "worked-example.lookup",
    "tool_version": "1.0.0",
    "caller_scope": "aer1-anchor-witness",
    "result": "ok",
}
canonical_bytes = json.dumps(canonical_payload, separators=(",", ":"), sort_keys=True).encode()
canonical_bytes_b64 = base64.b64encode(canonical_bytes).decode()

# output_hash: SHA-256 of canonical_bytes, exactly as draft-zambo-aer1-26
# Section 5 / Table 1 defines it. This is the value this repo anchors.
output_hash = sha256_hex(canonical_bytes)

metadata = {"receipt_schema_version": "0.4"}
metadata_bytes = json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode()
metadata_hash = sha256_hex(metadata_bytes)

receipt = {
    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, "aer1-anchor-witness/worked-example/1")),
    "receipt_schema_version": "0.4",
    "created_at": "2026-10-26T15:30:00Z",
    "tool": {
        "name": canonical_payload["tool_name"],
        "version": canonical_payload["tool_version"],
        "caller_scope": canonical_payload["caller_scope"],
    },
    "provenance_class": "executed-by-recording-system",
    "canonical_bytes": canonical_bytes_b64,
    "output_hash": output_hash,
    "metadata_hash": metadata_hash,
    "verification_status": "unverified",
}

manifest = {
    "fixture_id": "aer1-anchor-witness-worked-example",
    "spec": "draft-zambo-aer1-26 (AER-1: A Portable Execution Receipt for AI Agent Tool Calls)",
    "receipt": receipt,
    "anchored_ref": output_hash,
    "anchor_ref_bytes32": "0x" + output_hash,
    "anchor_registry": "0x49fEcA52bC634a9Ab773226D16619deC547794aa",
    "anchor_chain": "Base mainnet (chainId 8453)",
    "provenance": (
        "Synthetic AER-1 receipt. canonical_bytes/output_hash/metadata_hash "
        "computed exactly per draft-zambo-aer1-26 Table 1/Section 5 "
        "(SHA-256 over canonical_bytes). NOT produced by a running AER-1 "
        "client or SDK. The anchored value is AER-1's own output_hash, "
        "unwrapped — no action_ref/JCS preimage involved, since the point "
        "is that AnchorRegistry.anchor(bytes32) can anchor AER-1's own "
        "digest directly. No claim that AER-1 or Brennan Zambo has "
        "integrated, endorsed, or adopted AnchorRegistry."
    ),
}

with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)
    f.write("\n")

print("=== aer1-anchor-witness : producer ===")
print(f"canonical_bytes (b64) = {canonical_bytes_b64}")
print(f"output_hash (AER-1)   = {output_hash}")
print(f"anchor ref (bytes32)  = 0x{output_hash}")
print(f"wrote {OUT_DIR}/manifest.json")
