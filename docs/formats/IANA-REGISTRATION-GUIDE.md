# IANA Media Type Registration Guide for PIRTM

**Owner**: Language Architect  
**Deadline**: Day 30 (before `pirtm vin` release)  
**Reference**: ADR-009: Digital VIN and Glass-Box Identity Protocol

---

## Overview

PIRTM requires two media type registrations with IANA to establish global format identity. This guide provides step-by-step instructions for submitting registrations via the IANA media types form.

## The Two Formats

| Format | Media Type | Spec Section | Purpose |
|---|---|---|---|
| `.pirtm.bc` sealed binary | `application/vnd.pirtm.bc` | MLIR bitcode with `!pirtm_proof` and `!pirtm_governance` sections | Sealed PIRTM module with embedded proofs |
| PGIF JSON document | `application/vnd.pirtm.governance+json` | ADR-009 §1-2, `digital_vin` hash tree | VIN hash tree serialization |

Both are registered in the **vendor tree** (`application/vnd.`), not the standards tree, as they are publicly available but not yet IETF/ISO standards.

---

## Registration Process (RFC 6838)

### Step 1: Prepare the Media Type Template

IANA requires completion of RFC 6838 Section 4.2 templates for each media type. Below are templates customized for PIRTM:

#### Template 1: `application/vnd.pirtm.bc`

```
Type name: application

Subtype name: vnd.pirtm.bc

Required parameters: None

Optional parameters: None
  (Future: arch parameter for architecture-specific variants,
   e.g., application/vnd.pirtm.bc; arch=x86-64)

Encoding considerations: binary

Security considerations:
  PIRTM sealed binaries carry cryptographic proofs of correctness
  tied to specific module parameters (prime_index, epsilon, op_norm_T).
  These proofs are deterministic hashes of the module content.
  
  Threats:
  1. Binary modification → proof hash mismatch (detected by `pirtm vin`)
  2. Replay: PGIF includes sealed_at timestamp for freshness
  3. Privacy: Module parameters and spectral bounds are visible in PGIF
  
  Mitigations:
  - Always validate proof_hash via `pirtm vin --verify <binary> <vin>`
  - Check sealed_at timestamp contextually
  - Treat spectral bounds as public knowledge (they're system identifiers)

Interoperability considerations:
  PIRTM bitcode is portable across architectures (LLVM IR representation).
  However, the executable compiled from bitcode will be architecture-specific.
  The media type identifies only the bitcode artifact, not the target arch.

Published specification:
  MultiplicityFoundation/PIRTM ADR-004: MLIR Dialect Specification
  https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md
  
  Tooling ADR-009: Digital VIN and Glass-Box Identity Protocol
  https://github.com/MultiplicityFoundation/Tooling/docs/adr/ADR-009-digital-vin-and-glass-box-identity.md

Applications that use this media type:
  - pirtm CLI: `pirtm vin`, `pirtm inspect`, `pirtm verify`
  - Supply chain tools: PIRTM binary repos, mirroring services
  - Content delivery: HTTP caches, package registries
  - Deployment: orchestration platforms consuming sealed binaries

Fragment identifier considerations: None

Restrictions on usage: None

Provisional registration? No

Additional information:
  Magic number(s): None (MLIR binary format, identified by header)
  File extension(s): .pirtm.bc
  Macintosh file type code(s): None
  Person & email address to contact for further information:
    Language Architect <contact@multiplicityf.org>

Intended usage: COMMON

Change controller:
  MultiplicityFoundation
  https://github.com/MultiplicityFoundation/
```

#### Template 2: `application/vnd.pirtm.governance+json`

```
Type name: application

Subtype name: vnd.pirtm.governance+json

Required parameters: None

Optional parameters: None

Encoding considerations: UTF-8 (JSON)

Security considerations:
  PGIF is a serialization of the VIN hash tree—a commitment to all module
  parameters and coupling configuration. PGIF is derived deterministically
  from the sealed binary and cannot be forged without also forging the
  binary's embedded proofs.
  
  Threats:
  1. PGIF substitution: Replace VIN with different one
     → Detected: Any module verifies against its own embedded proof_hash
  2. PGIF tampering: Modify coupling_matrix or spectral_radius
     → Detected: Would require recomputing all ancestor hashes
  3. Stale PGIF: Use old governance after module was updated
     → Mitigated: sealed_at timestamp, module recomputation
  
  Mitigations:
  - Always validate PGIF against binary via `pirtm vin --verify`
  - Check sealed_at against deployment context
  - Every component is independently verifiable (glass-box identity)

Interoperability considerations:
  PGIF is JSON per RFC 8259, human-readable and easily parsed.
  Structured syntax suffix "+json" per RFC 6839 signals JSON schema tools
  to expect JSON inside.

Published specification:
  Tooling ADR-009: Digital VIN and Glass-Box Identity Protocol
  https://github.com/MultiplicityFoundation/Tooling/docs/adr/ADR-009-digital-vin-and-glass-box-identity.md

Applications that use this media type:
  - pirtm CLI: `pirtm vin`, `pirtm inspect`
  - Supply chain tools: VIN registries, governance audits
  - REST APIs: Content negotiation for VIN exchange
  - Webhook systems: Governance change notifications

Fragment identifier considerations: None (standard JSON fragment syntax applies)

Restrictions on usage: None

Provisional registration? No

Additional information:
  File extension(s): .pgif, .pgif.json
  Person & email address:
    Language Architect <contact@multiplicityf.org>

Intended usage: COMMON

Change controller:
  MultiplicityFoundation
  https://github.com/MultiplicityFoundation/
```

---

### Step 2: Submit via IANA Media Types Form

1. Go to **https://www.iana.org/form/media-types**
2. Select **Vendor Tree** (for both forms)
3. Fill in each template as a separate submission
4. Designate owner: Language Architect
5. Submit

**Expected timeline**: IANA expert review typically completes in 1–4 weeks.

---

### Step 3: Confirmation

Upon approval, IANA will:
1. Assign registration IDs (usually sequential within vendor tree)
2. Publish in the official registry at https://www.iana.org/assignments/media-types/media-types.xhtml
3. Send confirmation email to the contact email

---

## Verification Checklist

Before Day 30 release, verify:

- [ ] `application/vnd.pirtm.bc` appears in IANA registry
- [ ] `application/vnd.pirtm.governance+json` appears in IANA registry
- [ ] Both registrations include references to spec ADRs
- [ ] `pirtm vin` can emit PGIF with correct media type in HTTP headers (if REST API)
- [ ] Documentation (docs/formats/media-types.md) is complete and explains both types
- [ ] Test: PIRTM binaries served with `Content-Type: application/vnd.pirtm.bc` are correctly identified by tools

---

## After Registration

### Update Code and Docs

1. **`pirtm inspect` output** (if adding HTTP/REST):
   ```
   Content-Type: application/vnd.pirtm.governance+json (IANA registered)
   ```

2. **`docs/formats/media-types.md`**:
   ```markdown
   # PIRTM Media Types
   
   ## Sealed MLIR Bitcode
   - **Type**: application/vnd.pirtm.bc
   - **File extension**: .pirtm.bc
   - **Spec**: PIRTM ADR-004, ADR-009
   - **IANA Registry**: https://www.iana.org/assignments/media-types/...
   
   ## Governance Interchange Format (PGIF)
   - **Type**: application/vnd.pirtm.governance+json
   - **File extension**: .pgif.json
   - **Spec**: PIRTM ADR-009
   - **IANA Registry**: https://www.iana.org/assignments/media-types/...
   ```

3. **Supply chain tooling**:
   - File validators can now check media type instead of extension
   - HTTP caches can use `Content-Type` header for routing
   - REST APIs can offer content negotiation

### Community Communication

- Add note to PIRTM README about media type registration
- Include IANA URLs in release notes (Day 30+)
- Consider SCITT/SLSA integration: use media types for artifact identification

---

## Reference

- **RFC 6838** (IANA Media Types): https://tools.ietf.org/html/rfc6838
- **RFC 6839** (Structured Syntax Suffixes): https://tools.ietf.org/html/rfc6839
- **IANA Media Types Registry**: https://www.iana.org/assignments/media-types/media-types.xhtml
- **IANA Registration Form**: https://www.iana.org/form/media-types
- **PIRTM ADR-004**: Compositional Hash Identity (spec amendment)
- **PIRTM ADR-009**: Digital VIN and Glass-Box Identity Protocol
