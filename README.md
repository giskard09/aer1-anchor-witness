# aer1-anchor-witness

A worked example that anchors a synthetic **AER-1** receipt's own
`output_hash` — unwrapped, no translation — directly into
**AnchorRegistry**, a permissionless on-chain contract
(`anchor(bytes32)`, no owner/roles, same CREATE2 address across
Base/Arbitrum/Ink).

> **Provenance, up front (read `PROVENANCE.md` for the full statement).**
> `output_hash` is computed exactly per
> [draft-zambo-aer1-26](https://datatracker.ietf.org/doc/draft-zambo-aer1/)
> Table 1/Section 5. It was **NOT produced by a running AER-1 client or
> SDK** — this is a synthetic receipt. Nothing here implies that AER-1 or
> Brennan Zambo has integrated, endorsed, or adopted `AnchorRegistry`.

## Why this exists

[draft-zambo-aer1-26](https://datatracker.ietf.org/doc/draft-zambo-aer1/)
is unusually precise about what its self-contained hash check does and
does not prove. Section 13: *"Issuer authentication is not part of this
specification... verification proves the recorded bytes were not altered
after minting, not who minted them."* And on time: *"The `created_at`
timestamp is asserted by the producer. Absent an anchor, a receipt
carries no trusted time."*

Section 10 already defines what an anchor needs to be to close that gap:
*"A verified anchor proves that the anchored_digest existed no later than
the anchor's publication time,"* but *"a 'witness' anchor controlled by
the publisher gives no independent witnessing."* The spec correctly
leaves the anchor target pluggable — its reference implementation uses
Nostr relays, described explicitly as *"a deployment choice, not a
requirement."*

`AnchorRegistry` is one candidate for that slot: permissionless, no
owner, no roles, the same contract address on three real chains — it
isn't infrastructure anyone (including the receipt issuer) controls.
This repo shows AER-1's own `output_hash` anchored into it directly,
with no new format, no wrapping, no dependency.

## What's here

| Path | What it is |
|------|-----------|
| `scripts/produce.py` | Builds a synthetic AER-1 receipt per Table 1/Section 5 and computes `output_hash` exactly as the spec defines it. |
| `verifier/verify.py` | Independent (stdlib-only): recomputes `output_hash` from the declared `canonical_bytes` and confirms the matching `Anchored` event on Base mainnet. |
| `artifacts/` | `manifest.json` (receipt, digest) and `anchor.json` (tx/block). |
| `scripts/anchor.sh` | The exact `cast` command used to anchor the digest. |
| `PROVENANCE.md` | Exactly what is and isn't real here. Read it. |

## Reproduce

```bash
python3 scripts/produce.py artifacts
# anchor on Base mainnet (see scripts/anchor.sh)
python3 verifier/verify.py
```

## The anchor

- **Registry:** `0x49fEcA52bC634a9Ab773226D16619deC547794aa` (Base 8453,
  Arbitrum One 42161, Ink 57073 — same address).
- **Function:** `anchor(bytes32 ref)` — permissionless, no owner/roles/funds.
- **Event:** `Anchored(bytes32 indexed ref, address indexed anchoredBy, uint256 timestamp)`.
- Tx/block for this instance: `artifacts/anchor.json`.

## License

MIT.
