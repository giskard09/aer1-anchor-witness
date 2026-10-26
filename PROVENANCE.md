# Provenance — read this before drawing any conclusion

## What is real

- The receipt shape (`id`, `receipt_schema_version`, `created_at`, `tool`,
  `provenance_class`, `canonical_bytes`, `output_hash`, `metadata_hash`,
  `verification_status`) is taken directly from **draft-zambo-aer1-26**
  Table 1 / Section 5, read from the published I-D at
  [datatracker.ietf.org/doc/draft-zambo-aer1](https://datatracker.ietf.org/doc/draft-zambo-aer1/).
- `output_hash` is computed exactly as the spec defines it: SHA-256 over
  `canonical_bytes`. The value in `artifacts/manifest.json` is independently
  recomputable by anyone from the declared `canonical_bytes` — see
  `verifier/verify.py`.
- The on-chain anchor is a real transaction on Base mainnet; the tx hash and
  block are independently checkable by anyone.

## What is synthetic — declared

- **No running AER-1 client or SDK was called.** `id`, `created_at`,
  `tool`, and the payload inside `canonical_bytes` are all constructed in
  `scripts/produce.py`, not captured from a real tool call.
- **No wrapping.** This repo does not run AER-1's `output_hash` through
  `action_ref`'s own JCS/four-field preimage scheme — the anchored value is
  AER-1's own digest, unwrapped. The point is narrower than "these two
  specs are compatible": `AnchorRegistry.anchor(bytes32)` takes any
  32-byte value permissionlessly, and AER-1's `output_hash` already is one.

## What this therefore does and does not show

- **Does show:** AER-1's own `output_hash`, computed exactly per its
  published spec, can be anchored directly into a permissionless, no-owner
  on-chain registry — giving it the property draft-zambo-aer1-26 Section 10
  describes anchoring as providing ("a verified anchor proves that the
  anchored_digest existed no later than the anchor's publication time"),
  and Section 13 as absent without one ("absent an anchor, a receipt
  carries no trusted time").
- **Does not show:** that AER-1, Brennan Zambo, or zambo.dev has
  integrated, endorsed, or adopted `AnchorRegistry`. It is a worked example
  applying a public, permissionless contract to AER-1's own published
  digest format. Anchoring itself is already optional in the spec
  ("a receipt MAY be bound to one or more external anchors after
  issuance") — but the spec's five defined `anchor_type` values
  (`nostr`/`ots`/`witness`/`scitt`/`rfc3161`) each have a fixed proof
  shape, and none of them is a permissionless on-chain contract.
  `AnchorRegistry` doesn't fit any of the five as specified today — this
  repo does not claim it does, only that the same digest anchors cleanly
  into it as a sixth, different shape of external witness.
