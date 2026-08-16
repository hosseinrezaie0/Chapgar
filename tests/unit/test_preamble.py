import pytest
from core.generator import build_preamble, AVAILABLE_FONTS, VALID_PAPER_SIZES

@pytest.mark.unit
class TestBuildPreamble:
    def test_default_vazirmatn_a4(self):
        preamble, line_count = build_preamble()
        assert 'font: "Vazirmatn"' in preamble
        assert 'lang: "fa"' in preamble
        assert 'dir: rtl' in preamble
        assert 'paper: "a4"' in preamble
        assert line_count > 0
        assert line_count == preamble.count("\n")

    def test_estedad_font_case_insensitive(self):
        preamble_lower, _ = build_preamble(font_family="estedad")
        assert 'font: "Estedad"' in preamble_lower

        preamble_upper, _ = build_preamble(font_family="  ESTEDAD  ")
        assert 'font: "Estedad"' in preamble_upper

    def test_unknown_font_falls_back_to_vazirmatn(self):
        preamble, _ = build_preamble(font_family="NonExistentFont")
        assert 'font: "Vazirmatn"' in preamble

    def test_paper_size_normalization(self):
        # Letter alias
        p_letter, _ = build_preamble(paper_size="letter")
        assert 'paper: "us-letter"' in p_letter

        # Legal alias
        p_legal, _ = build_preamble(paper_size="legal")
        assert 'paper: "us-legal"' in p_legal

        # Valid A3
        p_a3, _ = build_preamble(paper_size="a3")
        assert 'paper: "a3"' in p_a3

        # Invalid paper size falls back to A4
        p_invalid, _ = build_preamble(paper_size="invalid_size_xxx")
        assert 'paper: "a4"' in p_invalid

    def test_includes_persian_numeral_conversion(self):
        preamble, _ = build_preamble()
        assert '#let en-to-fa' in preamble
        assert '#show regex("[0-9]"):' in preamble
