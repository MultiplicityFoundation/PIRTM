# ADR-009: Digital VIN and Glass-Box Identity Protocol

> **Status**: Proposed  
> **Date**: 2026-03-10  
> **Authors**: Phase Mirror Team  
> **Spec Reference**: [PIRTM ADR-004: Compositional Hash Identity](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

## Context

The PIRTM system produces verifiable hash identities at every layer: component (proof_hash in `!pirtm_proof`), subsystem (session_graph commitment), engine (link-time governance seal in `!pirtm_governance`), and chassis (deployment envelope). These four levels compose into a single **Digital VIN**—a cryptographic identity that uniquely identifies not just the current state of the system but also makes visible any mutation anywhere in the dependency tree.

Current practice serializes governance data as an audit report (human-readable records of decisions). This ADR proposes inverting that model: treat the governance interchange format (PGIF) as a **hash tree serialization format** whose root is the VIN, making the system legible from any vantage point (with or without access to the full binary).

## Decision

### 1. PGIF as Hash Tree Serialization Format

The PIRTM Governance Interchange Format (PGIF) is not a report of checks completed. It is a **commitment to a specific hash tree**. Its root field is the **Digital VIN**:

```json
{
  "digital_vin": "0xVIN:e7c3...",
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

### 2. Four-Level Hash Composition

The VIN is computed by layering four hash operations:

| Level | Input | Formula | Output | Represents |
| :--- | :--- | :--- | :--- | :--- |
| 1 (Component) | prime_index ∥ ε ∥ op_norm_T ∥ \|\|Ξ\|\| ∥ \|\|Λ\|\| | H₁(...) | proof_hash | Component correctness (transpile-time contractivity check) |
| 2 (Subsystem) | proof_hash₁ ∥ proof_hash₂ ∥ ... ∥ coupling_matrix | H₂(...) | session_graph commitment | Coupling resolved (link-time matrix construction) |
| 3 (Engine) | subsystem_hash ∥ spectral_radius ∥ r(Ψ) ∥ runtime_version | H₃(...) | governance_seal | Network spectral bounds certified (link-time spectral-small-gain) |
| 4 (Chassis) | governance_seal ∥ sealed_at ∥ deployment_context | H₄(...) | digital_vin | Sealed deployment identity |

**Key property**: Each level commits to all lower levels transitively. Changing any component parameter forces recomputation of all ancestor hashes up to the VIN. There is no way to silently mutate the system.

### 3. The `pirtm vin` CLI Command

A new command displays the full hash tree for any sealed binary:

```bash
$ pirtm vin pirtm_runtime.bin

=== DIGITAL VIN: 0xVIN:e7c3... ===

Component Hashes
  [prime_index=7919]  proof_hash:    0x7f3a91...
                      ε:             0.12
                      ‖op_norm_T‖:   4.35

  [prime_index=7907]  proof_hash:    0x4c22b8...
                      ε:             0.08
                      ‖op_norm_T‖:   3.91

Number of components: 2
Composition modulus: 7919 * 7907 = 62,595,733 (squarefree ✓)

Subsystem Hash
  session_graph_commitment:  0x91fe03...
  coupling_matrix:
    [0.30  0.10]
    [0.10  0.40]

Engine Hash
  governance_seal:     0xb34d77...
  spectral_radius r(Ψ): 0.65
  small-gain margin:   0.35 (threshold 0.0, SAFE ✓)
  runtime_version:     pirtm-0.14.1

Chassis Hash
                       0x002af1...
  sealed_at:           2026-03-10T14:32:00Z
  deployment_context:  production-us-east

Verification: VALID
  ✓ All component hashes recomputable from binary sections
  ✓ Subsystem coupling matrix matches session_graph
  ✓ Spectral radius within governance bounds
  ✓ VIN checksum validates all four levels
```

**Properties**:
- Anyone with the binary can run `pirtm vin` (no external dependencies)
- Output includes all parameters needed to audit the composition
- When run without the binary, a user with the VIN can independently verify any component they have access to
- The command exits with non-zero status if any hash verification fails

### 4. Glass-Box Identity

A PIRTM system is **glass-box** when:

1. Its VIN is publicly known (e.g., `0xVIN:e7c3...`)
2. Any component of it can be shared independent of the full system
3. Recipients can independently verify that component's parameters against the published VIN

**Example**: A supplier ships a PIRTM module with `proof_hash = 0x7f3a91...`. A customer receives the module and the system VIN `0xVIN:e7c3...`. The customer:
- Extracts the module's `proof_hash` and compares to the published value ✓
- Computes the component's contractivity bounds from its parameters
- Verifies these bounds are consistent with the known spectral radius in the VIN

This is possible because each hash commits to the full parameter set transitively.

## Consequences

### Positive

- **Legibility**: The VIN makes the system's entire verified state visible without requiring access to the full binary or a trust-based audit report
- **Composability**: Components and subsystems can be verified independently given their commitment hashes
- **Audit trail**: Every binary carries its own proof of correctness (no separate audit document)
- **Supply chain transparency**: Hashes propagate through multi-tier suppliers without a central authority

### Negative

- **New command**: Requires implementation of `pirtm vin` with hex output formatting and verification logic
- **Binary size**: The `!pirtm_proof` and `!pirtm_governance` sections carry additional metadata (parameter provenance)
- **User education**: Glass-box identity is unfamiliar; documentation must explain why recomputing a VIN is verification

## IANA Media Type Registration

PIRTM introduces two novel binary/data formats that must be globally identifiable:

### 1. `.pirtm.bc` Sealed MLIR Bitcode

**Media Type**: `application/vnd.pirtm.bc`

The sealed PIRTM binary: MLIR bitcode with embedded non-allocating sections:
- `!pirtm_proof`: Component identity (prime_index, ε, ‖T‖, proof_hash)
- `!pirtm_governance`: Link-time governance seal (spectral_radius, certification timestamp)

**Specification**: This ADR + [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

**Registration Path**: IANA vendor tree (RFC 6838), expert review

### 2. PGIF (PIRTM Governance Interchange Format)

**Media Type**: `application/vnd.pirtm.governance+json`

JSON serialization of the four-level hash tree (VIN composition):
- digital_vin root commitment
- component_hashes (proof identities)
- subsystem_hash (coupling resolution)
- engine_hash (governance seal)
- chassis_hash (deployment context)

Uses the `+json` structured syntax suffix per RFC 6839.

**Specification**: This ADR (Section 1-2 above)

**Registration Path**: IANA vendor tree (RFC 6838), expert review

### Rationale

Without IANA registration:
- External tools cannot reliably identify PIRTM formats by media type alone
- Each tool must implement format sniffing or assume file extensions
- Supply chain tooling (mirrors, caches, validators) cannot signal format compatibility

With registration:
- `Content-Type: application/vnd.pirtm.bc` immediately signals "this is a sealed PIRTM binary"
- `Content-Type: application/vnd.pirtm.governance+json` signals "this is a VIN hash tree"
- Standard HTTP/REST semantics apply; content negotiation works
- PIRTM formats are globally legible by standard mechanisms

### Acceptance Criteria (Media Type Registration)

- [ ] Register `application/vnd.pirtm.bc` with IANA (owner: Language Architect)
  - Template (RFC 6838 Section 4.2) completed and submitted
  - References this ADR as normative specification
- [ ] Register `application/vnd.pirtm.governance+json` with IANA (owner: Language Architect)
  - Template (RFC 6838 Section 4.2) completed and submitted
  - References this ADR as normative specification
- [ ] Both registrations completed and approved before `pirtm vin` Day 30+ release
- [ ] Documentation: docs/formats/media-types.md explains both types and their usage

**Horizon**: Day 30 (before `pirtm vin` ships) — ensures PIRTM formats have stable IANA identity from first external release.

## Acceptance Criteria (VIN Implementation)

- [ ] `pirtm vin <binary>` command implemented and produces formatted four-level hash tree
- [ ] PGIF serialization includes `digital_vin` root field and all components' `proof_hash` values
- [ ] `pirtm vin --verify <binary> <published_vin>` exits 0 if hashes match, non-zero otherwise
- [ ] Documentation (docs/vin/README.md) explains glass-box identity and VIN composition semantics
- [ ] Integration test: run `pirtm vin` on a sealed binary, parse output, verify all four hash levels
- [ ] Example: display VIN for a real small-gain system (r < 1.0) and a failing system (r > 1.0)

## Open Questions

1. **Hash function**: Use SHA-256 or BLAKE3? (PIRTM ADR-004 must specify)
2. **Hex encoding**: Output format for long hashes (truncate at 12 hex digits with `...` suffix?)
3. **Parameter serialization**: Canonical order for subsystem hash (alphabetical prime_index? coupling matrix row-major?)
4. **Deployment context**: What fields compose `deployment_context` in the chassis hash? (hostname, timestamp, environment tag?)
5. **Media type registration timeline**: Can IANA registration (Section: IANA Media Type Registration) be completed by Day 30? Who owns the registration submission?
6. **Media type specificity**: Should `.pirtm.bc` variants (e.g., architecture-specific) have subtype parameters (e.g., `application/vnd.pirtm.bc; arch=x86-64`) or separate registrations?

## References

- PIRTM ADR-004: Compositional Hash Identity (Spec Amendment)
- Merkle tree identity (canonical reference)
- Glass-box system architecture (cf. observable system theory)
