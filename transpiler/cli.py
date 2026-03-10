"""
PIRTM Transpiler CLI: Compile descriptors to various backends.

Usage:
    pirtm transpile --input descriptor.yaml --output mlir
    pirtm transpile --input descriptor.yaml --output numpy
    pirtm inspect recurrence.pirtm.bc
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Internal imports
from pirtm.transpiler.mlir_lowering import MLIREmitter, MLIRConfig


class PirtmCLI:
    """PIRTM command-line interface."""
    
    def __init__(self):
        self.parser = self._build_parser()
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser."""
        parser = argparse.ArgumentParser(
            prog="pirtm",
            description="PIRTM Transpiler: Compile recurrence descriptors to verified code.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Transpile YAML descriptor to MLIR
  pirtm transpile --input policy.yaml --output mlir --epsilon 0.05

  # Transpile with witness hash from ACE
  pirtm transpile \\
    --input policy.yaml \\
    --output mlir \\
    --trace-id "session_abc123" \\
    --witness-hash poseidon

  # Inspect compiled binary
  pirtm inspect compiled.pirtm.bc

  # Show contractivity metadata
  pirtm inspect --meta compiled.pirtm.bc
            """,
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # === transpile command ===
        transpile = subparsers.add_parser(
            "transpile",
            help="Transpile recurrence descriptor to target backend",
        )
        
        transpile.add_argument(
            "--input", "-i",
            type=str,
            required=True,
            help="Input descriptor file (YAML or JSON)",
        )
        
        transpile.add_argument(
            "--output", "-o",
            type=str,
            choices=["mlir", "numpy", "llvm", "circom"],
            default="mlir",
            help="Target compilation backend (default: mlir)",
        )
        
        transpile.add_argument(
            "--epsilon", "-e",
            type=float,
            default=0.05,
            help="Contractivity margin (default: 0.05)",
        )
        
        transpile.add_argument(
            "--confidence", "-c",
            type=float,
            default=0.9999,
            help="Confidence level (default: 0.9999)",
        )
        
        transpile.add_argument(
            "--op-norm-T",
            type=float,
            default=1.0,
            help="Operator norm of transformation T (default: 1.0)",
        )
        
        transpile.add_argument(
            "--prime-index",
            type=int,
            default=17,
            help="Prime modulus index (default: 17)",
        )
        
        transpile.add_argument(
            "--trace-id",
            type=str,
            help="ACE witness trace ID (optional)",
        )
        
        transpile.add_argument(
            "--witness-hash",
            type=str,
            choices=["poseidon", "sha256"],
            default="poseidon",
            help="Witness hash algorithm (default: poseidon)",
        )
        
        transpile.add_argument(
            "--outfile",
            type=str,
            help="Output file path (default: based on input + format)",
        )
        
        transpile.add_argument(
            "--emit-diag",
            action="store_true",
            help="Emit mlir-opt diagnostic header (for verification)",
        )
        
        transpile.set_defaults(func=self.cmd_transpile)
        
        # === inspect command ===
        inspect = subparsers.add_parser(
            "inspect",
            help="Inspect compiled PIRTM binary or MLIR file",
        )
        
        inspect.add_argument(
            "file",
            type=str,
            help="PIRTM binary (.pirtm.bc) or MLIR file (.mlir)",
        )
        
        inspect.add_argument(
            "--meta",
            action="store_true",
            help="Show contractivity metadata only",
        )
        
        inspect.add_argument(
            "--verify",
            action="store_true",
            help="Verify contractivity bounds",
        )
        
        inspect.set_defaults(func=self.cmd_inspect)
        
        return parser
    
    def cmd_transpile(self, args: argparse.Namespace) -> int:
        """Execute transpile command."""
        try:
            # Load descriptor
            descriptor = self._load_descriptor(args.input)
            
            # Route to appropriate backend
            if args.output == "mlir":
                return self._transpile_to_mlir(descriptor, args)
            elif args.output == "numpy":
                return self._transpile_to_numpy(descriptor, args)
            else:
                print(f"Error: Backend '{args.output}' not yet implemented", file=sys.stderr)
                return 1
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _transpile_to_mlir(self, descriptor: Dict[str, Any], args: argparse.Namespace) -> int:
        """Transpile descriptor to MLIR."""
        # Extract metadata
        config = MLIRConfig(
            epsilon=args.epsilon,
            confidence=args.confidence,
            op_norm_T=args.op_norm_T,
            prime_index=args.prime_index,
            emit_witness_hash=bool(args.trace_id),
            witness_hash_type=args.witness_hash,
        )
        
        emitter = MLIREmitter(config=config)
        
        # Emit MLIR
        mlir_code = emitter.emit_module(
            policy_name=descriptor.get("policy", "CarryForward"),
            kernel_name=descriptor.get("kernel", "FullAsymmetricAttribution"),
            trace_id=args.trace_id,
            dimension=descriptor.get("dimension", 512),
        )
        
        # Optional diagnostic header
        if args.emit_diag:
            diag = emitter.emit_diagnostics_header()
            mlir_code = diag + "\n\n" + mlir_code
        
        # Determine output file
        outfile = args.outfile or self._default_output_path(args.input, "mlir")
        
        # Write to file
        with open(outfile, "w") as f:
            f.write(mlir_code)
        
        print(f"✅ Transpiled to MLIR: {outfile}")
        print(f"   Epsilon: {args.epsilon}")
        print(f"   Confidence: {args.confidence}")
        
        if args.trace_id:
            print(f"   Witness ID: {args.trace_id}")
        
        return 0
    
    def _transpile_to_numpy(self, descriptor: Dict[str, Any], args: argparse.Namespace) -> int:
        """Transpile descriptor to NumPy (symbolic IR)."""
        # For now, just output descriptor as annotated JSON
        outfile = args.outfile or self._default_output_path(args.input, "numpy.json")
        
        output: Dict[str, Any] = {
            "format": "numpy-symbolic-ir",
            "descriptor": descriptor,
            "config": {
                "epsilon": args.epsilon,
                "confidence": args.confidence,
                "op_norm_T": args.op_norm_T,
                "prime_index": args.prime_index,
            },
        }
        
        with open(outfile, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Transpiled to NumPy IR: {outfile}")
        return 0
    
    def cmd_inspect(self, args: argparse.Namespace) -> int:
        """Execute inspect command."""
        try:
            filepath = Path(args.file)
            
            if not filepath.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                return 1
            
            if filepath.suffix == ".mlir":
                return self._inspect_mlir(filepath, args)
            elif filepath.suffix == ".bc":
                return self._inspect_bytecode(filepath, args)
            else:
                print(f"Error: Unknown file format: {filepath.suffix}", file=sys.stderr)
                return 1
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _inspect_mlir(self, filepath: Path, args: argparse.Namespace) -> int:
        """Inspect MLIR file."""
        with open(filepath, "r") as f:
            mlir_code = f.read()
        
        if args.meta:
            # Extract metadata only
            self._print_mlir_metadata(mlir_code)
        else:
            # Print full file
            print(mlir_code)
        
        return 0
    
    def _inspect_bytecode(self, filepath: Path, args: argparse.Namespace) -> int:
        """Inspect PIRTM bytecode."""
        # Placeholder: in production, decode .pirtm.bc binary format
        print(f"File: {filepath}")
        print(f"Format: PIRTM Bytecode (.pirtm.bc)")
        print(f"Size: {filepath.stat().st_size} bytes")
        
        if args.verify:
            print("Audit Chain: NOT EMBEDDED — retrieve via pirtm audit <trace.log>")
        
        return 0
    
    def _print_mlir_metadata(self, mlir_code: str) -> None:
        """Print contractivity metadata from MLIR."""
        import re
        
        print("=== MLIR Module Metadata ===")
        print()
        
        # Extract module comments
        comments = re.findall(r'// (.*)', mlir_code)
        for comment in comments[:5]:  # First 5 comments
            print(f"  {comment}")
        
        print()
        
        # Extract pirtm.module metadata
        if "pirtm.module {" in mlir_code:
            print("Contractivity Bounds:")
            for key in ["epsilon", "confidence", "op_norm_T", "prime_index"]:
                match = re.search(fr'@{key} = ([\d.]+|\'?\d+\'?)', mlir_code)
                if match:
                    print(f"  {key}: {match.group(1)}")
        
        print()
    
    # ========== Helper Methods ==========
    
    def _load_descriptor(self, filepath: str) -> Dict[str, Any]:
        """Load descriptor from YAML or JSON."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Descriptor file not found: {filepath}")
        
        with open(path, "r") as f:
            if path.suffix == ".yaml" or path.suffix == ".yml":
                import yaml
                return yaml.safe_load(f)
            elif path.suffix == ".json":
                return json.load(f)
            else:
                raise ValueError(f"Unknown descriptor format: {path.suffix}")
    
    def _default_output_path(self, input_path: str, format: str) -> str:
        """Generate default output path from input."""
        input_p = Path(input_path)
        stem = input_p.stem.replace(".pirtm", "")
        return str(input_p.parent / f"{stem}.{format}")
    
    def run(self, argv: list[str] | None = None) -> int:
        """Run CLI."""
        args = self.parser.parse_args(argv)
        
        if not hasattr(args, "func"):
            self.parser.print_help()
            return 0
        
        return args.func(args)


def main():
    """Entry point for pirtm CLI."""
    cli = PirtmCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
