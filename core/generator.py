import os
import typst

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(CORE_DIR, "assets", "fonts")

def create_pdf(typst_markup: str, output_filename: str = "output.pdf") -> str:
    """
    Compiles Typst markup into a Right-to-Left Persian PDF.
    Returns the absolute path to the generated PDF.
    """
    
    preamble = """
#set text(font: "Vazirmatn", lang: "fa", dir: rtl)
#set align(right)
#set page(numbering: "۱")

// Safely convert numbers in text to Persian numerals
#let en-to-fa = ("0": "۰", "1": "۱", "2": "۲", "3": "۳", "4": "۴", "5": "۵", "6": "۶", "7": "۷", "8": "۸", "9": "۹")
#show regex("[0-9]"): it => en-to-fa.at(it.text)

"""
    final_markup = preamble + typst_markup
    
    # Write the temporary typst file
    temp_typst_file = "temp_document.typ"
    with open(temp_typst_file, "w", encoding="utf-8") as f:
        f.write(final_markup)
    
    # Compile the PDF using the Typst Python wrapper, linking our local font
    output_path = os.path.abspath(output_filename)
    try:
        typst.compile(temp_typst_file, output=output_path, font_paths=[FONTS_DIR])
    finally:
        # Clean up the temporary text file
        if os.path.exists(temp_typst_file):
            os.remove(temp_typst_file)
            
    return output_path