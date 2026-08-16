import os
from pathlib import Path
import pytest
from core.generator import resolve_safe_path

@pytest.mark.unit
class TestPathResolution:
    def test_resolve_simple_filename(self, tmp_path):
        resolved = resolve_safe_path("output.pdf", base_dir=str(tmp_path))
        assert resolved == str((tmp_path / "output.pdf").resolve())
        assert Path(resolved).parent.exists()

    def test_creates_nested_parent_directories(self, tmp_path):
        nested_rel = "deeply/nested/reports/document.pdf"
        resolved = resolve_safe_path(nested_rel, base_dir=str(tmp_path))
        
        target_path = Path(resolved)
        assert target_path.parent.exists()
        assert target_path.name == "document.pdf"

    def test_handles_absolute_path_correctly(self, tmp_path):
        abs_target = str(tmp_path / "custom_dir" / "file.pdf")
        resolved = resolve_safe_path(abs_target)
        
        target_path = Path(resolved)
        assert target_path.parent.exists()
        assert str(target_path) == str(Path(abs_target).resolve())
