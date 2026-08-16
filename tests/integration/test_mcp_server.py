import asyncio
from pathlib import Path
import pytest
from server import generate_persian_pdf, mcp

@pytest.mark.integration
class TestMcpServer:
    def test_mcp_instance_and_tool_registration(self):
        assert mcp.name == "Chapgar"
        tool = asyncio.run(mcp.get_tool("generate_persian_pdf"))
        assert tool is not None
        assert tool.name == "generate_persian_pdf"

    def test_generate_persian_pdf_tool_success(self, tmp_path, sample_persian_markup):
        out_file = str(tmp_path / "mcp_test_doc.pdf")
        response = generate_persian_pdf(
            typst_markup=sample_persian_markup,
            output_filename=out_file,
            font_family="Vazirmatn",
            paper_size="a4",
            generate_preview=False
        )
        
        assert "Success! Persian PDF generated at:" in response
        assert "Font: Vazirmatn" in response
        assert "Paper: a4" in response
        assert "Preview image generated at:" not in response
        assert Path(out_file).exists()

    def test_generate_persian_pdf_tool_with_preview(self, tmp_path, sample_bidi_markup):
        out_file = str(tmp_path / "mcp_preview_doc.pdf")
        response = generate_persian_pdf(
            typst_markup=sample_bidi_markup,
            output_filename=out_file,
            font_family="Estedad",
            paper_size="a5",
            generate_preview=True
        )
        
        assert "Success! Persian PDF generated at:" in response
        assert "Preview image generated at:" in response
        assert Path(out_file).exists()
        assert Path(out_file).with_suffix(".png").exists()

    def test_generate_persian_pdf_tool_error_handling(self, tmp_path):
        bad_markup = "#v(۴cm)\nمتن نادرست"
        out_file = str(tmp_path / "mcp_err.pdf")
        response = generate_persian_pdf(
            typst_markup=bad_markup,
            output_filename=out_file
        )
        
        assert response.startswith("Error generating PDF:")
        assert "Do NOT use Persian digits" in response
        assert not Path(out_file).exists()
