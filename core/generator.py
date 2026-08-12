import os
import typst

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(CORE_DIR, "assets", "fonts")

import re

def sanitize_markup(typst_markup: str) -> str:
    """Strips redundant text(...) or #text(...) wrappers that LLMs sometimes generate without hashes."""
    # Match text(dir: rtl, lang: "fa", "...") or text(lang: "fa", dir: rtl, "...")
    pattern1 = r'text\s*\(\s*(?:dir:\s*rtl\s*,\s*lang:\s*"fa"|lang:\s*"fa"\s*,\s*dir:\s*rtl)\s*,\s*"(.*?)"\s*\)'
    cleaned = re.sub(pattern1, r'\1', typst_markup)
    
    pattern2 = r'text\s*\(\s*(?:dir:\s*rtl\s*,\s*lang:\s*"fa"|lang:\s*"fa"\s*,\s*dir:\s*rtl)\s*,\s*\'(.*?)\'\s*\)'
    cleaned = re.sub(pattern2, r'\1', cleaned)
    
    # Match #text(...)[...] or text(...)[...]
    pattern3 = r'#?text\s*\(\s*(?:dir:\s*rtl\s*,\s*lang:\s*"fa"|lang:\s*"fa"\s*,\s*dir:\s*rtl)\s*\)\s*\[(.*?)\]'
    cleaned = re.sub(pattern3, r'\1', cleaned, flags=re.DOTALL)
    
    return cleaned

def create_pdf(typst_markup: str, output_filename: str = "output.pdf") -> str:
    """
    Compiles Typst markup into a Right-to-Left Persian PDF.
    Returns the absolute path to the generated PDF.
    """
    typst_markup = sanitize_markup(typst_markup)
    
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
    except Exception as e:
        err = str(e)
        if "is not valid in code" in err:
            raise ValueError(
                f"Typst Syntax Error: {err}. Do NOT use Persian digits (۰-۹) inside Typst code parameters or dimensions (e.g. use #v(4cm) or columns: 3, NOT Persian digits in code). Standard numbers (0-9) in text will automatically render as Persian digits in the PDF."
            )
        elif "expected length" in err:
            raise ValueError(
                f"Typst Syntax Error: {err}. Ensure length values have units attached (e.g. 4cm, 12pt, 100%). Example: #v(1cm) or #line(length: 100%)."
            )
        elif "expected content, found array" in err:
            raise ValueError(
                f"Typst Syntax Error: {err}. In #table(...), pass cells as separate positional content blocks like #table([Cell 1], [Cell 2]), not wrapped in an array."
            )
        elif "unknown variable" in err:
            raise ValueError(
                f"Typst Syntax Error: {err}. Please do not use unknown/custom functions (like #plot or #bulletedlist). Use standard Typst syntax (- for lists, #table for tables, #grid for layouts)."
            )
        elif "package" in err or "download" in err:
            raise ValueError(
                f"Typst Offline Error: {err}. Do not use external @preview packages. Use only standard offline Typst primitives."
            )
        else:
            raise Exception(f"Typst Compilation Error: {err}")
    finally:
        # Clean up the temporary text file
        if os.path.exists(temp_typst_file):
            os.remove(temp_typst_file)
            
    return output_path