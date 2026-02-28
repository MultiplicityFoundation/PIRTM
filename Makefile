PYTHON ?= python
DIST_DIR ?= dist
SBOM_FILE ?= $(DIST_DIR)/sbom.spdx.json

.PHONY: help clean lint typecheck test conformance build sbom sign verify reproduce

help:
	@echo "Targets: lint typecheck test conformance build sbom sign verify reproduce clean"

clean:
	rm -rf $(DIST_DIR) build .pytest_cache .mypy_cache .ruff_cache

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	pytest -q

conformance:
	pirtm-conformance --profile all --output text

build:
	$(PYTHON) -m build

sbom: build
	@mkdir -p $(DIST_DIR)
	@if command -v syft >/dev/null 2>&1; then \
		syft packages dir:. -o spdx-json=$(SBOM_FILE); \
	else \
		echo "syft not found; install syft to generate SBOM"; \
		exit 1; \
	fi

sign: build
	@if command -v cosign >/dev/null 2>&1; then \
		for artifact in $(DIST_DIR)/*; do cosign sign-blob --yes $$artifact --output-signature $$artifact.sig; done; \
	else \
		echo "cosign not found; install cosign to sign artifacts"; \
		exit 1; \
	fi

verify:
	@if command -v cosign >/dev/null 2>&1; then \
		for artifact in $(DIST_DIR)/*; do \
			if [ -f $$artifact.sig ]; then cosign verify-blob --signature $$artifact.sig $$artifact; fi; \
		done; \
	else \
		echo "cosign not found; install cosign to verify signatures"; \
		exit 1; \
	fi

reproduce: clean build
	@sha256sum $(DIST_DIR)/* | sort > $(DIST_DIR)/SHA256SUMS
	@echo "Reproducibility manifest written to $(DIST_DIR)/SHA256SUMS"
