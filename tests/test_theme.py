import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "gen_theme", pathlib.Path(__file__).parent.parent / "scripts/gen-theme.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)


def test_every_component_uses_the_same_accent():
    p = gt.load()
    out = gt.render(p)
    accent = p["colors"]["accent"]
    assert len(out) == 4
    for path, text in out.items():
        assert accent.lstrip("#") in text.replace("#", ""), path


def test_palette_has_required_keys():
    p = gt.load()
    for k in ("bg", "surface", "text", "muted", "accent", "warn", "urgent"):
        assert k in p["colors"]
