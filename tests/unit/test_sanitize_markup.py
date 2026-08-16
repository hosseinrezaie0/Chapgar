import pytest
from core.generator import sanitize_markup

@pytest.mark.unit
class TestSanitizeMarkup:
    def test_strips_double_quoted_text_wrapper_dir_first(self):
        raw = 'text(dir: rtl, lang: "fa", "این یک متن ساده است")'
        assert sanitize_markup(raw) == "این یک متن ساده است"

    def test_strips_double_quoted_text_wrapper_lang_first(self):
        raw = 'text(lang: "fa", dir: rtl, "متن با ترتیب معکوس مشخصه‌ها")'
        assert sanitize_markup(raw) == "متن با ترتیب معکوس مشخصه‌ها"

    def test_strips_single_quoted_text_wrapper(self):
        raw = "text(dir: rtl, lang: 'fa', 'متن با تک کوتیشن')"
        assert sanitize_markup(raw) == "متن با تک کوتیشن"

    def test_strips_hash_text_bracket_syntax(self):
        raw = '#text(lang: "fa", dir: rtl)[متن داخل براکت با علامت هش]'
        assert sanitize_markup(raw) == "متن داخل براکت با علامت هش"

    def test_strips_text_bracket_syntax_without_hash(self):
        raw = 'text(dir: rtl, lang: "fa")[متن داخل براکت بدون علامت هش]'
        assert sanitize_markup(raw) == "متن داخل براکت بدون علامت هش"

    def test_strips_multiline_bracket_content(self):
        raw = """#text(dir: rtl, lang: "fa")[
خط اول متن
خط دوم متن
]"""
        expected = "خط اول متن\nخط دوم متن"
        assert sanitize_markup(raw) == expected

    def test_strips_conflicting_global_preambles(self):
        raw = """#set text(font: "Arial", size: 12pt)
#set page(paper: "a4", dir: ltr)
= عنوان اصلی سند
این متن واقعی است."""
        cleaned = sanitize_markup(raw)
        assert 'font: "Arial"' not in cleaned
        assert 'dir: ltr' not in cleaned
        assert '= عنوان اصلی سند\nاین متن واقعی است.' in cleaned

    def test_leaves_regular_markup_untouched(self):
        raw = """= گزارش ماهانه
- مورد اول
- مورد دوم
#table(columns: 2, [نام], [امتیاز])"""
        assert sanitize_markup(raw) == raw
