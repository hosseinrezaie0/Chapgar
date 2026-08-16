import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from core.generator import create_pdf

@pytest.mark.integration
class TestPdfCompilation:
    def test_compile_vazirmatn_pdf(self, tmp_path, sample_persian_markup):
        out_file = str(tmp_path / "vazir_doc.pdf")
        result = create_pdf(
            sample_persian_markup,
            output_filename=out_file,
            font_family="Vazirmatn",
            paper_size="a4"
        )
        
        pdf_path = Path(result["pdf_path"])
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        assert result["font_family"] == "Vazirmatn"
        assert result["paper_size"] == "a4"
        
        # Verify valid PDF header
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"

    def test_compile_estedad_pdf(self, tmp_path, sample_persian_markup):
        out_file = str(tmp_path / "estedad_doc.pdf")
        result = create_pdf(
            sample_persian_markup,
            output_filename=out_file,
            font_family="Estedad",
            paper_size="a5"
        )
        
        pdf_path = Path(result["pdf_path"])
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        assert result["font_family"] == "Estedad"
        assert result["paper_size"] == "a5"

    def test_compile_with_preview_image(self, tmp_path, sample_bidi_markup):
        out_file = str(tmp_path / "preview_doc.pdf")
        result = create_pdf(
            sample_bidi_markup,
            output_filename=out_file,
            generate_preview=True
        )
        
        assert result["preview_path"] is not None
        preview_path = Path(result["preview_path"])
        assert preview_path.exists()
        assert preview_path.suffix == ".png"
        assert preview_path.stat().st_size > 0
        
        # Verify PNG signature
        with open(preview_path, "rb") as f:
            png_header = f.read(8)
            assert png_header == b"\x89PNG\r\n\x1a\n"

    def test_compile_stress_test_markup(self, tmp_path, sample_stress_markup):
        out_file = str(tmp_path / "stress_doc.pdf")
        result = create_pdf(
            sample_stress_markup,
            output_filename=out_file,
            font_family="Estedad",
            paper_size="a4",
            generate_preview=True
        )
        
        assert Path(result["pdf_path"]).exists()
        assert Path(result["preview_path"]).exists()

    def test_concurrent_compilations_thread_safety(self, tmp_path):
        num_workers = 6
        
        def worker(idx: int):
            out_file = str(tmp_path / f"threaded_{idx}.pdf")
            markup = f"""= سند همزمان شماره {idx}
این سند در نخ پردازشی شماره {idx} تولید شده است.
مقدار تصادفی: {idx * 42}
"""
            font = "Estedad" if idx % 2 == 0 else "Vazirmatn"
            return create_pdf(markup, output_filename=out_file, font_family=font)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            results = [f.result() for f in futures]

        for res in results:
            p = Path(res["pdf_path"])
            assert p.exists()
            assert p.stat().st_size > 0
