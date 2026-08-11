import os
import typst
from .preprocessor import convert_to_persian_numerals

# Define paths dynamically so it works anywhere
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(CORE_DIR, "assets", "fonts")

def create_pdf(typst_markup: str, output_filename: str = "output.pdf") -> str:
    """
    Compiles Typst markup into a Right-to-Left Persian PDF.
    Returns the absolute path to the generated PDF.
    """
    # 1. Enforce Persian numerals
    processed_markup = convert_to_persian_numerals(typst_markup)
    
    # 2. Inject the Typst preamble for Persian RTL support if the AI missed it
    # We enforce Vazirmatn, Persian language, RTL direction, and right-aligned text.
    preamble = """
#set text(font: "Vazirmatn", lang: "fa", dir: rtl)
#set align(right)
#set page(numbering: "۱")

"""
    final_markup = preamble + processed_markup
    
    # 3. Write the temporary typst file
    temp_typst_file = "temp_document.typ"
    with open(temp_typst_file, "w", encoding="utf-8") as f:
        f.write(final_markup)
    
    # 4. Compile the PDF using the Typst Python wrapper, linking our local font
    output_path = os.path.abspath(output_filename)
    try:
        typst.compile(temp_typst_file, output=output_path, font_paths=[FONTS_DIR])
    finally:
        # Clean up the temporary text file
        if os.path.exists(temp_typst_file):
            os.remove(temp_typst_file)
            
    return output_path