from fastmcp import FastMCP
from core.generator import create_pdf

# Initialize the MCP Server with our chosen name
mcp = FastMCP("Chapgar")

@mcp.tool()
def generate_persian_pdf(
    typst_markup: str,
    output_filename: str = "output.pdf",
    font_family: str = "Vazirmatn",
    paper_size: str = "a4",
    generate_preview: bool = False
) -> str:
    """
    GENERATES AND SAVES a Right-To-Left Persian PDF to the local disk.
    CRITICAL: You MUST use this tool for ANY Persian or RTL PDF generation request.
    
    IMPORTANT TYPST GUIDELINES FOR THE LLM AGENT:
    - GENERAL PURPOSE TOOL: Use this tool for ANY Persian PDF document (reports, articles, letters, invoices, CVs, manuals, forms, academic notes, meeting minutes, etc.).
    - Write plain document text directly (e.g. `این یک گزارش جامع است`). DO NOT wrap sentences in `text(...)` or `#text(...)`. Chapgar automatically handles RTL orientation, embedded fonts, and Persian numerals in the preamble.
    - All function calls MUST start with `#` (e.g. `#table(...)`, `#grid(...)`, `#v(1cm)`). Never omit `#` before function names.
    - Use `#grid(...)` for multi-column page layout positioning (e.g. side-by-side columns, metadata, header details, signatures). Do NOT use `#table(...)` for general page layouts, because `#table` draws borders around every cell by default. Use `#table(...)` ONLY for itemized data lists or tabular data.
    - Always use standard ASCII digits (0-9) inside Typst code arguments and dimensions (e.g. #v(4cm), columns: 3, #line(length: 100%)). Do NOT write Persian digits (۰-۹) inside code parameters. Standard numbers in document text will automatically render as Persian digits in the final PDF.
    - DO NOT use external packages or imports (such as `@preview/cetz` or `@preview/plot`) as compilation is strictly local and offline.
    - DO NOT invent non-existent functions like `#plot(...)` or `#bulletedlist(...)`. Use standard `- item` syntax for lists.
    - DO NOT include page setup, `#set text(...)`, `#set page(...)`, or font preambles. Chapgar automatically injects selected fonts, RTL alignment, and Persian digit conversion (`۰-۹`).
    
    Args:
        typst_markup: The raw Typst markup body content (no preamble or package imports).
        output_filename: The target output PDF filename (e.g. "report.pdf").
        font_family: Persian font to use. Options: "Vazirmatn" (default, modern & clean) or "Estedad" (geometric & bold).
        paper_size: Target paper dimensions. Options: "a4" (default), "letter", "a5", "a3", "legal".
        generate_preview: Set to True to also generate a PNG image preview alongside the PDF.
    
    Returns:
        A success string containing the absolute path to the generated PDF (and preview image if requested).
    """
    try:
        # Call our isolated core engine
        result = create_pdf(
            typst_markup=typst_markup,
            output_filename=output_filename,
            font_family=font_family,
            paper_size=paper_size,
            generate_preview=generate_preview
        )
        
        pdf_path = result["pdf_path"]
        preview_path = result.get("preview_path")
        
        msg = f"Success! Persian PDF generated at: {pdf_path} (Font: {result['font_family']}, Paper: {result['paper_size']})"
        if preview_path:
            msg += f"\nPreview image generated at: {preview_path}"
        return msg
        
    except Exception as e:
        return f"Error generating PDF: {str(e)}"

def main():
    """Main CLI entrypoint for running the MCP server."""
    mcp.run()

# The entry point that listens for requests via stdio
if __name__ == "__main__":
    main()