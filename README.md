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

Section 10 says anchoring is optional (*"A receipt MAY be bound to one or
more external anchors after issuance"*) and defines what an anchor needs
to be to supply that trusted time: *"A verified anchor proves that the
anchored_digest existed no later than the anchor's publication time."*
It's also explicit about what disqualifies a witness: *'A "witness"
anchor whose witness record is publisher-controlled provides no
independent witnessing; it binds only the digest to the publisher's own
statement at the anchor time.'*

The spec defines five `anchor_type` values — `nostr`, `ots`, `witness`,
`scitt`, `rfc3161` — each with its own fixed proof shape. None of them is
a permissionless on-chain contract. `AnchorRegistry` doesn't fit any of
the five as specified today: it's closest in spirit to `ots` (public,
no publisher control over the underlying chain) but a different proof
shape entirely (a transaction + event log, not a base64 OpenTimestamps
calendar proof). This repo doesn't claim otherwise — it shows AER-1's
own `output_hash` anchored into `AnchorRegistry` directly, as a concrete
example of what a sixth, permissionless-contract anchor shape could look
like, not a drop-in fit for an existing `anchor_type`.

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
