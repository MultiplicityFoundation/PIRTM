"""
ADR-007 Day 14 Complete Workflow: MLIR → Bytecode → Inspection

This example demonstrates the full Day 14 workflow:
  1. MLIR emission from examples (Day 7-14)
  2. Bytecode generation with contractivity checks (Day 14)
  3. Bytecode inspection to verify contractivity (Day 14)

Run with: python3 pirtm/tests/demo_day_14_workflow.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.mlir_emitter_canonical import PIRTMMLIREmitter, MLIREmitterConfig
from pirtm.transpiler.pirtm_bytecode import create_bytecode_from_mlir
from pirtm.tools.pirtm_inspect import PIRTMInspector


def demo_workflow():
    """Demonstrate the complete Day 14 workflow."""
    
    print("\n" + "=" * 80)
    print("PIRTM DAY 14 COMPLETE WORKFLOW: MLIR → BYTECODE → INSPECTION")
    print("=" * 80)
    print()
    
    # Step 1: Load example from examples/
    print("STEP 1: Load Example Programs")
    print("-" * 80)
    
    examples_dir = Path('/workspaces/Tooling/pirtm/examples')
    example_files = [
        'basic_contractive_system.json',
        'multimodule_network.json',
    ]
    
    examples = {}
    for example_name in example_files:
        example_path = examples_dir / example_name
        with open(example_path, 'r') as f:
            examples[example_name] = json.load(f)
        
        example_data = examples[example_name]
        print(f"✅ Loaded: {example_name}")
        print(f"   Description: {example_data.get('description', 'N/A')[:60]}...")
        print(f"   Components: {len(example_data['components'])}")
        print()
    
    # Step 2: MLIR Emission (Day 7-14 gate)
    print("\nSTEP 2: Emit MLIR from Examples (Day 7-14 Gate)")
    print("-" * 80)
    
    mlir_outputs = {}
    
    for example_name, example_data in examples.items():
        components = example_data['components']
        print(f"Example: {example_name}")
        
        mlir_parts = []
        for comp in components:
            comp_name = comp.get('name', f"component_{comp['prime_index']}")
            
            emitter = PIRTMMLIREmitter(
                MLIREmitterConfig(
                    prime_index=comp['prime_index'],
                    epsilon=comp['epsilon'],
                    op_norm_T=comp['op_norm_T'],
                )
            )
            mlir = emitter.emit_module(module_name=comp_name)
            mlir_parts.append(mlir)
            
            print(f"  ✅ Emitted MLIR for {comp_name} (mod={comp['prime_index']})")
        
        mlir_outputs[example_name] = '\n\n'.join(mlir_parts)
        print()
    
    # Step 3: Bytecode Generation with Contractivity Checks (Day 14 Gate)
    print("\nSTEP 3: Generate Bytecode with Contractivity Checks (Day 14 Gate)")
    print("-" * 80)
    
    bytecodes = {}
    
    for example_name, mlir_text in mlir_outputs.items():
        example_data = examples[example_name]
        components = example_data['components']
        
        print(f"Example: {example_name}")
        
        bytecode = create_bytecode_from_mlir(mlir_text, components)
        bytecodes[example_name] = bytecode
        
        # Check contractivity for each module
        for metadata in bytecode.modules:
            margin = 1.0 - metadata.epsilon - metadata.op_norm_T
            status_symbol = "✅" if metadata.contractivity_check == "PASS" else "❌"
            print(f"  {status_symbol} {metadata.name:25s} mod={metadata.prime_index:6d} "
                  f"margin={margin:7.4f} → {metadata.contractivity_check}")
        
        print()
    
    # Step 4: Write Bytecode to Files
    print("\nSTEP 4: Write Bytecode to Files")
    print("-" * 80)
    
    bytecode_files = {}
    
    with tempfile.TemporaryDirectory(suffix=".pirtm_bytecode") as tmpdir:
        tmpdir = Path(tmpdir)
        
        for example_name, bytecode in bytecodes.items():
            # Convert example name to bytecode filename
            # E.g., "basic_contractive_system.json" → "basic_contractive_system.pirtm.bc"
            bc_filename = example_name.replace('.json', '.pirtm.bc')
            bc_path = tmpdir / bc_filename
            
            bytecode.write_to_file(bc_path)
            bytecode_files[example_name] = bc_path
            
            print(f"✅ Wrote: {bc_path.name}")
        
        # Step 5: Inspect Bytecode Files (Day 14 Gate Final Check)
        print("\nSTEP 5: Inspect Bytecode Files (Day 14 Gate Verification)")
        print("-" * 80)
        
        all_pass = True
        
        for example_name, bc_path in bytecode_files.items():
            print(f"\nInspecting: {bc_path.name}")
            print("─" * 80)
            
            # Use subprocess to capture output (simulating CLI tool)
            import subprocess
            result = subprocess.run(
                ['python3', 'pirtm/tools/pirtm_inspect.py', str(bc_path)],
                capture_output=True,
                text=True,
                cwd='/workspaces/Tooling'
            )
            
            output = result.stdout
            
            # Check for "contractivity_check: PASS"
            if "contractivity_check: PASS" in output:
                print(output)
                print(f"✅ PASS: Bytecode inspection confirms contractivity_check: PASS")
            else:
                print(output)
                print(f"❌ FAIL: Bytecode inspection did not confirm contractivity_check: PASS")
                all_pass = False
        
        print("\n" + "=" * 80)
        if all_pass:
            print("✅ DAY 14 WORKFLOW COMPLETE: All examples emit contractive bytecode")
        else:
            print("❌ DAY 14 WORKFLOW INCOMPLETE: Some examples failed verification")
        print("=" * 80)
        
        return 0 if all_pass else 1


def main():
    """Main entry point."""
    return demo_workflow()


if __name__ == '__main__':
    sys.exit(main())
