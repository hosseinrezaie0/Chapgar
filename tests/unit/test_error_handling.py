import pytest
from core.generator import create_pdf

@pytest.mark.unit
class TestErrorHandling:
    def test_persian_digits_in_code_error(self, tmp_path):
        bad_markup = "#v(۴cm)\nمتن تست"
        out_file = str(tmp_path / "err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf(bad_markup, output_filename=out_file)
        
        err = str(excinfo.value)
        assert "Typst Syntax Error" in err
        assert "Do NOT use Persian digits" in err

    def test_missing_length_unit_error(self, tmp_path):
        bad_markup = "#v(10)\nمتن تست"
        out_file = str(tmp_path / "err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf(bad_markup, output_filename=out_file)
        
        err = str(excinfo.value)
        assert "Typst Syntax Error" in err
        assert "Ensure length values have units attached" in err

    def test_array_in_table_error(self, tmp_path):
        bad_markup = "#table(columns: 2, ([خانه ۱], [خانه ۲]))"
        out_file = str(tmp_path / "err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf(bad_markup, output_filename=out_file)
        
        err = str(excinfo.value)
        assert "In #table(...), pass cells as separate positional content blocks" in err

    def test_unknown_variable_function_error(self, tmp_path):
        bad_markup = "#custom_nonexistent_function(123)\nمتن تست"
        out_file = str(tmp_path / "err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf(bad_markup, output_filename=out_file)
        
        err = str(excinfo.value)
        assert "Please do not use unknown/custom functions" in err

    def test_offline_package_error(self, monkeypatch, tmp_path):
        import typst
        
        def fake_compile(*args, **kwargs):
            raise Exception("failed to download package @preview/cetz:0.2.0 (network is unreachable)")
            
        monkeypatch.setattr(typst, "compile", fake_compile)
        
        out_file = str(tmp_path / "err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf("متن تست", output_filename=out_file)
        
        err = str(excinfo.value)
        assert "Typst Offline Error" in err
        assert "Do not use external @preview packages" in err

    def test_line_number_offset_calculation(self, monkeypatch, tmp_path):
        import typst
        from core.generator import build_preamble
        
        _, preamble_lines = build_preamble()
        simulated_raw_line = preamble_lines + 5
        
        def fake_compile(*args, **kwargs):
            raise Exception(f"document.typ:{simulated_raw_line}:12: unknown variable: my_var")
            
        monkeypatch.setattr(typst, "compile", fake_compile)
        
        out_file = str(tmp_path / "mock_err.pdf")
        with pytest.raises(ValueError) as excinfo:
            create_pdf("متن تستی", output_filename=out_file)
            
        err = str(excinfo.value)
        assert "(line 5, column 12)" in err
        assert "Please do not use unknown/custom functions" in err
