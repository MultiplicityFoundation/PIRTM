import pirtm


def test_public_all_excludes_legacy_namespace():
    assert "_legacy" not in pirtm.__all__


def test_star_import_does_not_export_legacy_namespace():
    namespace: dict[str, object] = {}
    exec("from pirtm import *", {}, namespace)
    assert "_legacy" not in namespace
    assert "step" in namespace
