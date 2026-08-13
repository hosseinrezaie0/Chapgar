from fastmcp import FastMCP
from core.generator import create_pdf

# Initialize the MCP Server with our chosen name
mcp = FastMCP("Chapgar")

@mcp.tool()
def generate_persian_pdf(typst_markup: str, output_filename: str = "output.pdf") -> str:
    """
    GENERATES AND SAVES a Right-To-Left Persian PDF to the local disk.
    CRITICAL: You MUST use this tool for ANY Persian or RTL PDF generation request.
    
    IMPORTANT TYPST GUIDELINES FOR THE LLM AGENT:
    - GENERAL PURPOSE TOOL: Use this tool for ANY Persian PDF document (reports, articles, letters, invoices, CVs, manuals, forms, academic notes, meeting minutes, etc.).
    - Write plain document text directly (e.g. `این یک گزارش جامع است`). DO NOT wrap sentences in `text(...)` or `#text(...)`. Chapgar automatically handles RTL orientation, Vazirmatn font, and Persian numerals in the preamble.
    - All function calls MUST start with `#` (e.g. `#table(...)`, `#grid(...)`, `#v(1cm)`). Never omit `#` before function names.
    - Use `#grid(...)` for multi-column page layout positioning (e.g. side-by-side columns, metadata, header details, signatures). Do NOT use `#table(...)` for general page layouts, because `#table` draws borders around every cell by default. Use `#table(...)` ONLY for itemized data lists or tabular data.
    - Always use standard ASCII digits (0-9) inside Typst code arguments and dimensions (e.g. #v(4cm), columns: 3, #line(length: 100%)). Do NOT write Persian digits (۰-۹) inside code parameters. Standard numbers in document text will automatically render as Persian digits in the final PDF.
    - DO NOT use external packages or imports (such as `@preview/cetz` or `@preview/plot`) as compilation is strictly local and offline.
    - DO NOT invent non-existent functions like `#plot(...)` or `#bulletedlist(...)`. Use standard `- item` syntax for lists.
    - DO NOT include page setup, `#set text(...)`, `#set page(...)`, or font preambles. Chapgar automatically injects Vazirmatn font, RTL alignment, and Persian digit conversion (`۰-۹`).
    
    Args:
        typst_markup: The raw Typst markup body content (no preamble or package imports).
        output_filename: The target output PDF filename (must end in .pdf).
    
    Returns:
        A success string containing the absolute path to the generated PDF.
    """
    try:
        # Call our isolated core engine
        path = create_pdf(typst_markup, output_filename)
        return f"Success! Flawless Persian PDF generated at: {path}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"

# The entry point that listens for requests via stdio
if __name__ == "__main__":
    mcp.run()