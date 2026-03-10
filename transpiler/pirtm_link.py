"""
PIRTM Linker: network-wide contractivity proof (Day 14–16 gate).

Pipeline:
  Pass 1: Name Resolution        — locate .pirtm.bc files, validate format
  Pass 2: Commitment Crosscheck  — detect duplicate identity_commitment (security gate)
  Pass 3: Matrix Construction    — build full session graph, substitute #pirtm.unresolved_coupling
  Then:    Spectral Small-Gain   — verify network-wide stability

Reference: ADR-008-linker-coupling-gates.md
"""

import json
import os
from typing import List, Dict, Tuple
from pirtm.transpiler.pirtm_bytecode import PIRTMBytecode
from pirtm.transpiler.pirtm_perf import OptimizedSpectralRadius


class CommitmentCollisionError(RuntimeError):
    """Raised when a duplicate identity_commitment is detected (security error)."""
    pass


class SpectralMarginWarning:
    """Track spectral margin and emit warnings when approaching threshold."""
    
    # Threshold for warnings (r > WARN_THRESHOLD indicates approaching instability)
    WARN_THRESHOLD = 0.95
    CRITICAL_THRESHOLD = 0.99
    
    # Margin levels for diagnostics
    MARGIN_LEVELS = {
        "excellent": (0.0, 0.50, "Excellent margin (r < 0.50)"),
        "good": (0.50, 0.75, "Good margin (0.50 ≤ r < 0.75)"),
        "acceptable": (0.75, 0.90, "Acceptable margin (0.75 ≤ r < 0.90)"),
        "warning": (0.90, 0.95, "⚠️  WARNING: Approaching threshold (0.90 ≤ r < 0.95)"),
        "critical": (0.95, 1.00, "🚨 CRITICAL: Very close to instability (0.95 ≤ r < 1.0)"),
    }
    
    @staticmethod
    def classify_margin(spectral_radius: float) -> str:
        """Classify spectral radius and return diagnostic message."""
        for level_name, (lower, upper, message) in SpectralMarginWarning.MARGIN_LEVELS.items():
            if lower <= spectral_radius < upper:
                return message
        return "ERROR: r ≥ 1.0 (not contractive)"
    
    @staticmethod
    def emit_warning_if_needed(spectral_radius: float) -> bool:
        """
        Check if spectral radius warrants a warning.
        
        Returns:
            True if warning threshold exceeded, False otherwise
        """
        if spectral_radius >= SpectralMarginWarning.CRITICAL_THRESHOLD:
            print(f"  🚨 CRITICAL WARNING: r={spectral_radius:.6f} (network dangerously close to instability)")
            return True
        elif spectral_radius >= SpectralMarginWarning.WARN_THRESHOLD:
            print(f"  ⚠️  WARNING: r={spectral_radius:.6f} (network approaching instability threshold)")
            return True
        return False


class PIRTMLinker:
    """Link PIRTM modules using coupling.json specification."""
    
    def __init__(self, coupling_json_path: str, enable_warnings: bool = True, use_cache: bool = True):
        """
        Initialize linker with coupling configuration.
        
        Args:
            coupling_json_path: Path to coupling.json file
            enable_warnings: If True, emit warnings when r approaches 1.0
            use_cache: If True, cache spectral radius computations (Day 30+ optimization)
        """
        self.coupling_config = self._load_coupling_json(coupling_json_path)
        self.modules = {}
        self.sessions = {}
        self.commitment_map = {}
        self.spectral_radius = None
        self.is_contractive = False
        self.spectral_margin = None
        self.enable_warnings = enable_warnings
        self.warnings = []  # Track all warnings emitted
        self.spectral_solver = OptimizedSpectralRadius(use_cache=use_cache, sparse_threshold=0.05)

    def _load_coupling_json(self, path: str) -> Dict:
        """
        Load and validate coupling.json schema.
        
        Schema:
        {
          "version": "1.0",
          "sessions": [
            {
              "name": "SessionA",
              "identity_commitment": "0xabc123def456",
              "modules": [...],
              "coupling_matrix": [[...]]
            }
          ],
          "cross_session_coupling": [[...]]
        }
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"coupling.json not found: {path}")
        
        with open(path) as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON in coupling.json: {e}")
        
        # Schema validation
        if "version" not in config:
            raise RuntimeError("coupling.json missing 'version'")
        if "sessions" not in config:
            raise RuntimeError("coupling.json missing 'sessions'")
        if not isinstance(config["sessions"], list):
            raise RuntimeError("'sessions' must be a list")
        
        return config

    def pass1_name_resolution(self) -> None:
        """
        Pass 1: Locate and load all .pirtm.bc files.
        
        Validates that each path exists and is a valid .pirtm.bc bytecode file.
        """
        print("[Pass 1] Name Resolution...")
        
        for session_cfg in self.coupling_config["sessions"]:
            session_name = session_cfg["name"]
            
            # Register session with commitment
            self.sessions[session_name] = {
                "commitment": session_cfg["identity_commitment"],
                "modules": [],
                "coupling": session_cfg.get("coupling_matrix", []),
                "module_specs": {}
            }
            
            # Load each module in session
            for module_cfg in session_cfg["modules"]:
                module_name = module_cfg["name"]
                path = module_cfg["path"]
                
                # Verify file exists
                if not os.path.exists(path):
                    raise RuntimeError(
                        f"Module {module_name}: bytecode file not found: {path}"
                    )
                
                # Load bytecode
                try:
                    bytecode = PIRTMBytecode.read_from_file(path)
                except Exception as e:
                    raise RuntimeError(
                        f"Module {module_name}: failed to load bytecode: {e}"
                    )
                
                # Register module
                module_key = f"{session_name}:{module_name}"
                self.modules[module_key] = {
                    "path": path,
                    "bytecode": bytecode,
                    "prime_index": module_cfg["prime_index"],
                    "epsilon": module_cfg["epsilon"],
                    "op_norm_T": module_cfg["op_norm_T"]
                }
                
                self.sessions[session_name]["modules"].append(module_name)
                self.sessions[session_name]["module_specs"][module_name] = {
                    "prime_index": module_cfg["prime_index"],
                    "epsilon": module_cfg["epsilon"],
                    "op_norm_T": module_cfg["op_norm_T"]
                }
                
                print(f"  ✓ {session_name}:{module_name} (prime_index={module_cfg['prime_index']})")

    def pass2_commitment_crosscheck(self) -> None:
        """
        Pass 2: Detect duplicate identity_commitment (L0 invariant #6).
        
        Raises CommitmentCollisionError if duplicate commitments found.
        This is a security gate—violations must cause hard failure.
        """
        print("[Pass 2] Commitment Crosscheck...")
        
        seen_commitments = {}
        
        for session_name, session in self.sessions.items():
            commitment = session["commitment"]
            
            if commitment in seen_commitments:
                prev_session = seen_commitments[commitment]
                raise CommitmentCollisionError(
                    f"error: duplicate identity_commitment: {commitment}\n"
                    f"  Session '{prev_session}' and '{session_name}' both share identity\n"
                    f"  (L0 invariant #6: human names in coupling.json do not survive into IR)"
                )
            
            seen_commitments[commitment] = session_name
            self.commitment_map[session_name] = commitment
            print(f"  ✓ {session_name}: commitment {commitment} (unique)")

    def pass3_matrix_construction(self) -> Dict:
        """
        Pass 3: Build full coupling matrix and resolve #pirtm.unresolved_coupling.
        
        Returns:
            Dict with 'matrix' (full coupling) and 'mapping' (session/module indices)
        """
        print("[Pass 3] Matrix Construction...")
        
        session_names = list(self.sessions.keys())
        session_indices = {name: i for i, name in enumerate(session_names)}
        
        # Count total modules
        total_modules = sum(len(s["modules"]) for s in self.sessions.values())
        
        # Initialize full coupling matrix (zeros)
        full_coupling = [[0.0] * total_modules for _ in range(total_modules)]
        
        # Fill in-session couplings (block-diagonal)
        module_offset = 0
        session_module_map = {}
        
        for session_name, session in self.sessions.items():
            num_modules = len(session["modules"])
            session_coupling = session["coupling"]
            
            # Validate coupling matrix is square and properly sized
            if len(session_coupling) != num_modules:
                raise RuntimeError(
                    f"Session {session_name}: coupling matrix size mismatch "
                    f"(expected {num_modules}x{num_modules}, got {len(session_coupling)})"
                )
            
            # Validate all rows have correct width
            for i, row in enumerate(session_coupling):
                if len(row) != num_modules:
                    raise RuntimeError(
                        f"Session {session_name}: coupling row {i} has wrong width "
                        f"(expected {num_modules}, got {len(row)})"
                    )
            
            # Insert into full matrix
            for i in range(num_modules):
                for j in range(num_modules):
                    full_coupling[module_offset + i][module_offset + j] = session_coupling[i][j]
            
            session_module_map[session_name] = (module_offset, num_modules)
            module_offset += num_modules
            
            print(f"  ✓ {session_name}: (modules: {num_modules}, offset: {session_module_map[session_name][0]})")
        
        # Fill cross-session couplings (if present)
        cross_coupling = self.coupling_config.get("cross_session_coupling", [])
        if cross_coupling:
            if len(cross_coupling) != len(session_names):
                raise RuntimeError(
                    f"Cross-session coupling matrix size mismatch "
                    f"(expected {len(session_names)}x{len(session_names)})"
                )
            
            for i, session_i in enumerate(session_names):
                offset_i, size_i = session_module_map[session_i]
                
                if len(cross_coupling[i]) != len(session_names):
                    raise RuntimeError(
                        f"Cross-session coupling row {i} has wrong width"
                    )
                
                for j, session_j in enumerate(session_names):
                    if i != j:
                        offset_j, size_j = session_module_map[session_j]
                        # Place cross-session coupling in first block position
                        value = cross_coupling[i][j]
                        if value != 0.0:
                            full_coupling[offset_i][offset_j] = value
                            print(f"  ✓ Cross-session: {session_i}[{offset_i}] ↔ {session_j}[{offset_j}] = {value}")
        
        return {
            "matrix": full_coupling,
            "mapping": session_module_map,
            "total_modules": total_modules
        }

    def spectral_small_gain(self, coupling_matrix: List[List[float]]) -> Tuple[float, bool]:
        """
        Run spectral-small-gain pass.
        
        Computes spectral radius of coupling matrix. Networks with r < 1 are contractive.
        L0 invariant #2: All modules individually contractive, AND network-wide r < 1.
        
        Returns:
            (spectral_radius, is_contractive)
        """
        print("[Spectral Pass] Small-Gain Test...")
        
        # Compute spectral radius
        spectral_radius = self._compute_spectral_radius(coupling_matrix)
        self.spectral_radius = spectral_radius
        
        # Compute margin (how much headroom we have until r=1.0)
        self.spectral_margin = 1.0 - spectral_radius
        
        print(f"  Spectral radius: r = {spectral_radius:.6f}")
        print(f"  Spectral margin: 1 - r = {self.spectral_margin:.6f}")
        
        # Classify and report margin level
        margin_report = SpectralMarginWarning.classify_margin(spectral_radius)
        print(f"  Margin level: {margin_report}")
        
        # Emit warning if margin is too small
        if self.enable_warnings:
            if SpectralMarginWarning.emit_warning_if_needed(spectral_radius):
                self.warnings.append(f"Spectral margin warning: r={spectral_radius:.6f}")
        
        # L0 invariant #2: must be < 1 for contractivity
        is_contractive = spectral_radius < 1.0
        self.is_contractive = is_contractive
        
        if is_contractive:
            print(f"  ✅ PASS: r < 1.0 (contractive network)")
        else:
            print(f"  ❌ FAIL: r ≥ 1.0 (divergent network)")
        
        return spectral_radius, is_contractive

    def _compute_spectral_radius(self, matrix: List[List[float]]) -> float:
        """
        Compute spectral radius (largest absolute eigenvalue).
        
        Uses optimized solver with caching and sparse matrix support (Day 30+).
        Falls back to power iteration if NumPy unavailable.
        """
        return self.spectral_solver.compute(matrix)

    def link(self) -> bool:
        """
        Execute full linking pipeline.
        
        Returns:
            True if linking succeeds (network is contractive)
            False if linking fails (network is divergent or other error)
        
        Raises:
            CommitmentCollisionError if duplicate identity_commitment detected (security gate)
        """
        print("=" * 50)
        print("PIRTM Linker: Day 14–16 Gate (with margin tracking)")
        print("=" * 50 + "\n")
        
        try:
            self.pass1_name_resolution()
            print()
            
            self.pass2_commitment_crosscheck()  # Can raise CommitmentCollisionError
            print()
            
            coupling_info = self.pass3_matrix_construction()
            print()
            
            spectral_radius, is_contractive = self.spectral_small_gain(coupling_info["matrix"])
            print()
            
            # Print audit and margin report
            self._print_audit_report()
            
            if is_contractive:
                print(f"✅ LINKING SUCCESSFUL (r={spectral_radius:.6f} < 1.0)")
                if self.warnings:
                    print(f"\n⚠️  Linking succeeded but with {len(self.warnings)} warning(s):")
                    for w in self.warnings:
                        print(f"   - {w}")
                return True
            else:
                print(f"❌ LINKING FAILED (r={spectral_radius:.6f} ≥ 1.0)")
                print(f"  Network is divergent. Spectral radius exceeds threshold.")
                return False
        
        except CommitmentCollisionError:
            # Security gate: re-raise so caller must handle explicitly
            raise
        except RuntimeError as e:
            print(f"❌ LINKING FAILED: {e}")
            return False
        except Exception as e:
            print(f"❌ LINKING FAILED (internal error): {e}")
            return False
    
    def _print_audit_report(self) -> None:
        """Print audit trail and margin tracking report."""
        print("[Audit Report]")
        if self.spectral_radius is not None:
            print(f"  Spectral radius: r = {self.spectral_radius:.6f}")
            print(f"  Spectral margin: 1 - r = {self.spectral_margin:.6f}")
            
            # Calculate percentage of available margin
            margin_pct = (self.spectral_margin / 1.0) * 100
            print(f"  Margin utilization: {100 - margin_pct:.1f}%")
            
            # Sessions and modules summary
            num_sessions = len(self.sessions)
            total_modules = sum(len(s["modules"]) for s in self.sessions.values())
            print(f"  Sessions linked: {num_sessions}")
            print(f"  Total modules: {total_modules}")
            
            # Spectral margin classification
            margin_class = SpectralMarginWarning.classify_margin(self.spectral_radius)
            print(f"  Margin classification: {margin_class}")
    
    def get_margin_report(self) -> Dict:
        """
        Get detailed margin report as dictionary.
        
        Returns:
            Dict with spectral_radius, margin, margin_pct, warnings, status
        """
        return {
            "spectral_radius": self.spectral_radius,
            "spectral_margin": self.spectral_margin,
            "margin_percent": (self.spectral_margin / 1.0 * 100) if self.spectral_margin else None,
            "is_contractive": self.is_contractive,
            "warnings": self.warnings,
            "num_sessions": len(self.sessions),
            "num_modules": sum(len(s["modules"]) for s in self.sessions.values()),
        }
