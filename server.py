from fastmcp import FastMCP
from core.generator import create_pdf

# Initialize the MCP Server with our chosen name
mcp = FastMCP("Chapgar")

@mcp.tool()
def generate_persian_pdf(typst_markup: str, output_filename: str = "output.pdf") -> str:
    """
    Generates a Right-To-Left Persian PDF from Typst markup.
    Automatically enforces Vazirmatn font, Persian language, RTL direction, and localized numerals.
    
    Args:
        typst_markup: The Typst syntax containing the document content (do not include the preamble).
        output_filename: The name of the resulting PDF (must end in .pdf).
    
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