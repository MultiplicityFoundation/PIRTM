# PIRTM Formats and Media Types

This directory documents the serialization formats and media types used in Phase Mirror.

## PIRTM Binary Formats

### `.pirtm.bc` — Sealed MLIR Bitcode

**Media Type**: `application/vnd.pirtm.bc`  
**File Extension**: `.pirtm.bc`  
**Status**: IANA vendor tree (pending registration — see [IANA-REGISTRATION-GUIDE.md](./IANA-REGISTRATION-GUIDE.md))

The sealed PIRTM binary: MLIR bitcode with non-allocating embedded sections:
- `!pirtm_proof`: Component proof hash and parameters
- `!pirtm_governance`: Link-time governance seal

Emitted by the transpiler during Day 0–14 pipeline.  
Verified by `pirtm vin` and `pirtm inspect` commands.

**Spec**: 
- [PIRTM ADR-004](../adr/ADR-004.md) — MLIR Dialect
- [Tooling ADR-009](../adr/ADR-009-digital-vin-and-glass-box-identity.md) — VIN Serialization

---

### `PGIF` — PIRTM Governance Interchange Format

**Media Type**: `application/vnd.pirtm.governance+json`  
**File Extension**: `.pgif.json`  
**Status**: IANA vendor tree (pending registration — see [IANA-REGISTRATION-GUIDE.md](./IANA-REGISTRATION-GUIDE.md))

JSON serialization of the four-level VIN hash tree:
- **Digital VIN**: Root cryptographic identity
- **Component Hashes**: Proof identities for each module
- **Subsystem Hash**: Coupling matrix commitment
- **Engine Hash**: Governance seal with spectral radius
- **Chassis Hash**: Deployment context and sealed timestamp

Emitted by `pirtm vin` command.  
Portable across systems; human-readable.

**Example**:
```json
{
  "digital_vin": "0xVIN:e7c3abc123def456",
  "composition_level": 4,
  "component_hashes": [
    {"prime_index": 7919, "proof_hash": "0x7f3a91..."},
    {"prime_index": 7907, "proof_hash": "0x4c22b8..."}
  ],
  "subsystem_hash": "0x91fe03...",
  "subsystem_coupling_matrix": [[0.3, 0.1], [0.1, 0.4]],
  "engine_hash": "0xb34d77...",
  "engine_spectral_radius": 0.65,
  "chassis_hash": "0x002af1...",
  "sealed_at": "2026-03-10T14:32:00Z",
  "runtime_version": "pirtm-0.14.1"
}
```

**Spec**: [Tooling ADR-009](../adr/ADR-009-digital-vin-and-glass-box-identity.md) — Digital VIN and Glass-Box Identity Protocol

---

## IANA Media Type Registration

**Status**: Day 30 deliverable  
**Owner**: Language Architect  
**Timeline**: Before `pirtm vin` release to establish global format identity

Both formats require registration in the IANA vendor tree (`application/vnd.*`) to be globally identifiable by media type.

**See**: [IANA-REGISTRATION-GUIDE.md](./IANA-REGISTRATION-GUIDE.md) for step-by-step submission instructions, RFC 6838 templates, and verification checklist.

---

## Format Evolution

| Phase | Format | Status | Spec |
|---|---|---|---|
| Day 0–3 | MLIR types with `mod=` | Implemented | ADR-006 + ADR-004 |
| Day 3–7 | Transpiler emits `.pirtm.bc` | In progress (ADR-007 Phase 2) | ADR-007 + ADR-009 |
| Day 30 | `pirtm vin` outputs PGIF JSON | Planned | ADR-009 |
| Day 30 | IANA registration complete | Planned | IANA-REGISTRATION-GUIDE |

---

## Tools and Utilities

- **`pirtm vin <binary>`**: Extract and display VIN hash tree from sealed binary
- **`pirtm inspect <binary>`**: Display all proof sections and metadata
- **`pirtm verify <binary> <vin>`**: Validate binary against published VIN

---

## Integration Points

### Supply Chain

- **Package Registries**: Index PIRTM binaries by media type
- **Content Delivery**: Route `.pirtm.bc` files by media type in HTTP headers
- **Artifact Stores**: SLSA/SCITT integration uses media type for classification

### REST APIs

- Content negotiation: Accept `application/vnd.pirtm.governance+json`
- Webhook notifications: Deliver PGIF with correct media type
- Mirroring: Preserve media type metadata across cache boundaries

### Developer Tools

- IDE support: Syntax highlighting for `.pgif.json` files
- Linters: Validate PGIF JSON schema
- Version control: Diff PGIF trees semantically (not textually)

---

## References

- [RFC 6838](https://tools.ietf.org/html/rfc6838) — IANA Media Types (Vendor Tree)
- [RFC 6839](https://tools.ietf.org/html/rfc6839) — Structured Syntax Suffixes
- [IANA Media Types Registry](https://www.iana.org/assignments/media-types/media-types.xhtml)
- [PIRTM ADR-004](../adr/ADR-004.md) — MLIR Dialect Spec
- [Tooling ADR-009](../adr/ADR-009-digital-vin-and-glass-box-identity.md) — VIN Protocol
