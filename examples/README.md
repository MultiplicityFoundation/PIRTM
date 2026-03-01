 # Examples

 ## Quickstart

 Run a minimal one-step + short-run recurrence demo:

 ```bash
 python examples/quickstart.py
 ```

 ## Full Pipeline

 Run Tier 2-style pipeline (CSC budget -> weights -> gains -> run -> certificate -> PETC):

 ```bash
 python examples/full_pipeline.py
 ```

 ## Transpiler Descriptor

 Use this computation descriptor with the Phase 2.1 transpiler CLI examples:

 - `examples/transpile_computation.json`
 - `examples/transpile_two_layer_nn.json`

Note: JSON CLI output is gated; add `--emit-witness` and/or `--emit-lambda-events` to include those fields.

 ## Legacy Notebooks

 The legacy exploratory notebooks remain for reference:

 - `example_multiplicity_flow.ipynb`
 - `example_peoh_proof.ipynb`
 - `example_qai_integration.ipynb`

