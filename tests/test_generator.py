import os
import pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from core.generator import (
    create_pdf,
    sanitize_markup,
    build_preamble,
    resolve_safe_path,
    AVAILABLE_FONTS,
    VALID_PAPER_SIZES
)
from server import generate_persian_pdf

def test_sanitize_markup_removes_redundant_wrappers():
    raw = 'text(dir: rtl, lang: "fa", "این یک متن ساده است")'
    assert sanitize_markup(raw) == "این یک متن ساده است"

    raw_hash = '#text(lang: "fa", dir: rtl)[متن داخل براکت]'
    assert sanitize_markup(raw_hash) == "متن داخل براکت"

    raw_conflicts = '#set text(font: "Arial")\n#set page(dir: ltr)\n= عنوان اصلی'
    cleaned = sanitize_markup(raw_conflicts)
    assert 'font: "Arial"' not in cleaned
    assert 'dir: ltr' not in cleaned
    assert "عنوان اصلی" in cleaned

def test_resolve_safe_path(tmp_path):
    safe_path = resolve_safe_path("subdir/test.pdf", base_dir=str(tmp_path))
    assert Path(safe_path).parent.exists()
    assert safe_path.endswith("test.pdf")

def test_build_preamble_defaults_and_options():
    preamble_vazir, lines_vazir = build_preamble("Vazirmatn", "a4")
    assert 'font: "Vazirmatn"' in preamble_vazir
    assert 'paper: "a4"' in preamble_vazir
    assert lines_vazir > 0

    preamble_estedad, _ = build_preamble("Estedad", "letter")
    assert 'font: "Estedad"' in preamble_estedad
    assert 'paper: "us-letter"' in preamble_estedad

def test_create_pdf_default_vazirmatn(tmp_path):
    output_file = str(tmp_path / "test_vazir.pdf")
    markup = "= تست با فونت وزیر\nاین یک تست ساده است."
    result = create_pdf(markup, output_filename=output_file)
    
    assert os.path.exists(result["pdf_path"])
    assert os.path.getsize(result["pdf_path"]) > 0
    assert result["font_family"] == "Vazirmatn"

def test_create_pdf_estedad_font(tmp_path):
    output_file = str(tmp_path / "test_estedad.pdf")
    markup = "= تست با فونت استعداد\nاین یک سند رسمی با فونت استعداد است."
    result = create_pdf(markup, output_filename=output_file, font_family="Estedad", paper_size="a5")
    
    assert os.path.exists(result["pdf_path"])
    assert os.path.getsize(result["pdf_path"]) > 0
    assert result["font_family"] == "Estedad"
    assert result["paper_size"] == "a5"

def test_create_pdf_with_preview(tmp_path):
    output_file = str(tmp_path / "test_preview.pdf")
    markup = "= سند همراه با پیش‌نمایش تصویر\nتست تولید فایل PNG."
    result = create_pdf(markup, output_filename=output_file, generate_preview=True)
    
    assert os.path.exists(result["pdf_path"])
    assert result["preview_path"] is not None
    assert os.path.exists(result["preview_path"])
    assert result["preview_path"].endswith(".png")
    assert os.path.getsize(result["preview_path"]) > 0

def test_thread_safe_concurrent_compilations(tmp_path):
    """Verifies that multiple concurrent threads do not conflict with temporary files."""
    num_threads = 5
    
    def compile_worker(i):
        file_path = str(tmp_path / f"concurrent_{i}.pdf")
        content = f"= سند همزمان شماره {i}\nمتن مربوط به ریسمان {i}."
        font = "Estedad" if i % 2 == 0 else "Vazirmatn"
        return create_pdf(content, output_filename=file_path, font_family=font)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(compile_worker, i) for i in range(num_threads)]
        results = [f.result() for f in futures]
        
    for res in results:
        assert os.path.exists(res["pdf_path"])
        assert os.path.getsize(res["pdf_path"]) > 0

def test_error_translation_persian_digits_in_code():
    bad_markup = "#v(۴cm)\nمتن تستی"
    with pytest.raises(ValueError) as excinfo:
        create_pdf(bad_markup, "error_test.pdf")
    
    err_msg = str(excinfo.value)
    assert "Do NOT use Persian digits" in err_msg
    assert "Typst Syntax Error" in err_msg

def test_error_translation_expected_length():
    bad_markup = "#v(4)\nمتن تستی"
    with pytest.raises(ValueError) as excinfo:
        create_pdf(bad_markup, "error_test.pdf")
    
    err_msg = str(excinfo.value)
    assert "Ensure length values have units" in err_msg

def test_server_generate_persian_pdf_tool(tmp_path):
    output_file = str(tmp_path / "server_test.pdf")
    markup = "= تست سرور FastMCP\nارسال درخواست از لایه سرور."
    response = generate_persian_pdf(
        typst_markup=markup,
        output_filename=output_file,
        font_family="Estedad",
        generate_preview=True
    )
    
    assert "Success! Persian PDF generated at:" in response
    assert "Preview image generated at:" in response
    assert os.path.exists(output_file)
    assert os.path.exists(str(Path(output_file).with_suffix(".png")))
