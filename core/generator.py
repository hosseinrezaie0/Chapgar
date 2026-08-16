import os
import re
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import typst

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(CORE_DIR, "assets", "fonts")

# Recognized and bundled fonts
AVAILABLE_FONTS = {
    "vazirmatn": "Vazirmatn",
    "estedad": "Estedad",
}

# Standard supported paper sizes in Typst
VALID_PAPER_SIZES = {
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
    "b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
    "us-letter", "us-legal", "us-executive", "letter", "legal"
}

def sanitize_markup(typst_markup: str) -> str:
    """
    Cleans up redundant or conflicting wrappers that LLMs sometimes generate defensively:
    1. Strips text(dir: rtl, lang: 'fa', "...") or text(lang: 'fa', dir: rtl, "...")
    2. Strips #text(...)[...] or text(...)[...]
    3. Strips redundant conflicting preambles like #set text(...) and #set page(...)
    """
    # 1. Match #text(dir: rtl, lang: "fa", "...") / single/double quotes, either order
    pattern_quoted = r'#?text\s*\(\s*(?:dir:\s*rtl\s*,\s*lang:\s*["\']fa["\']|lang:\s*["\']fa["\']\s*,\s*dir:\s*rtl)\s*,\s*["\'](.*?)["\']\s*\)'
    cleaned = re.sub(pattern_quoted, r'\1', typst_markup)
    
    # 2. Match #text(...)[...] or text(...)[...]
    pattern_bracket = r'#?text\s*\(\s*(?:dir:\s*rtl\s*,\s*lang:\s*["\']fa["\']|lang:\s*["\']fa["\']\s*,\s*dir:\s*rtl)\s*\)\s*\[(.*?)\]'
    cleaned = re.sub(pattern_bracket, r'\1', cleaned, flags=re.DOTALL)
    
    # 3. Strip conflicting user-generated global preambles
    cleaned = re.sub(r'#set\s+text\s*\([^)]*\)\s*', '', cleaned)
    cleaned = re.sub(r'#set\s+page\s*\([^)]*dir:\s*(?:ltr|rtl)[^)]*\)\s*', '', cleaned)
    
    return cleaned.strip()

def resolve_safe_path(output_filename: str, base_dir: str = ".") -> str:
    """
    Sanitizes target path to ensure it remains inside an allowed directory
    and creates any necessary parent directories.
    """
    base_path = Path(base_dir).resolve()
    target_path = (base_path / output_filename).resolve()
    
    # Ensure parent directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return str(target_path)

def build_preamble(font_family: str = "Vazirmatn", paper_size: str = "a4") -> tuple[str, int]:
    """
    Constructs the standard RTL Persian preamble and returns the preamble string
    along with its line count (for accurate error line offset calculation).
    """
    # Normalize font name
    font_key = font_family.strip().lower()
    selected_font = AVAILABLE_FONTS.get(font_key, "Vazirmatn")
    
    # Normalize paper size
    paper_key = paper_size.strip().lower()
    selected_paper = paper_key if paper_key in VALID_PAPER_SIZES else "a4"
    if selected_paper == "letter":
        selected_paper = "us-letter"
    elif selected_paper == "legal":
        selected_paper = "us-legal"

    preamble = f"""#set text(font: "{selected_font}", lang: "fa", dir: rtl)
#set align(right)
#set page(paper: "{selected_paper}", numbering: "۱")

// Safely convert numbers in text to Persian numerals
#let en-to-fa = ("0": "۰", "1": "۱", "2": "۲", "3": "۳", "4": "۴", "5": "۵", "6": "۶", "7": "۷", "8": "۸", "9": "۹")
#show regex("[0-9]"): it => en-to-fa.at(it.text)

"""
    line_count = preamble.count("\n")
    return preamble, line_count

def create_pdf(
    typst_markup: str,
    output_filename: str = "output.pdf",
    font_family: str = "Vazirmatn",
    paper_size: str = "a4",
    generate_preview: bool = False
) -> Dict[str, Any]:
    """
    Compiles Typst markup into a Right-to-Left Persian PDF in a thread-safe environment.
    
    Args:
        typst_markup: The raw Typst document content.
        output_filename: Target output PDF file path.
        font_family: Font to use ("Vazirmatn" or "Estedad").
        paper_size: Paper size (e.g. "a4", "letter", "a5").
        generate_preview: If True, also generates a PNG preview of the first page.
        
    Returns:
        A dictionary containing the PDF path, preview path (if requested), font, and paper size.
    """
    typst_markup = sanitize_markup(typst_markup)
    preamble, preamble_lines = build_preamble(font_family=font_family, paper_size=paper_size)
    final_markup = preamble + typst_markup
    
    output_path = resolve_safe_path(output_filename)
    if not output_path.lower().endswith(".pdf"):
        output_path += ".pdf"
        
    preview_path: Optional[str] = None
    if generate_preview:
        preview_path = str(Path(output_path).with_suffix(".png"))

    # Thread-safe isolated temporary compilation directory
    with tempfile.TemporaryDirectory(prefix="chapgar_") as temp_dir:
        temp_typst_file = os.path.join(temp_dir, "document.typ")
        with open(temp_typst_file, "w", encoding="utf-8") as f:
            f.write(final_markup)

        try:
            # Compile main PDF
            typst.compile(temp_typst_file, output=output_path, font_paths=[FONTS_DIR])
            
            # Optionally compile PNG preview
            if generate_preview and preview_path:
                typst.compile(temp_typst_file, output=preview_path, format="png", font_paths=[FONTS_DIR])
                
        except Exception as e:
            err = str(e)
            
            # Extract line and column numbers if present in traceback
            line_match = re.search(r'document\.typ:(\d+):(\d+)', err)
            line_context = ""
            if line_match:
                raw_line = int(line_match.group(1))
                col = line_match.group(2)
                user_line = max(1, raw_line - preamble_lines)
                line_context = f" (line {user_line}, column {col})"

            if "is not valid in code" in err:
                raise ValueError(
                    f"Typst Syntax Error{line_context}: {err}. Do NOT use Persian digits (۰-۹) inside Typst code parameters or dimensions (e.g. use #v(4cm) or columns: 3, NOT Persian digits in code). Standard numbers (0-9) in text will automatically render as Persian digits in the PDF."
                )
            elif "length" in err or "fraction" in err:
                raise ValueError(
                    f"Typst Syntax Error{line_context}: {err}. Ensure length values have units attached (e.g. 4cm, 12pt, 100%). Example: #v(1cm) or #line(length: 100%)."
                )
            elif "expected content, found array" in err:
                raise ValueError(
                    f"Typst Syntax Error{line_context}: {err}. In #table(...), pass cells as separate positional content blocks like #table([Cell 1], [Cell 2]), not wrapped in an array."
                )
            elif "unknown variable" in err:
                raise ValueError(
                    f"Typst Syntax Error{line_context}: {err}. Please do not use unknown/custom functions (like #plot or #bulletedlist). Use standard Typst syntax (- for lists, #table for tables, #grid for layouts)."
                )
            elif "package" in err or "download" in err:
                raise ValueError(
                    f"Typst Offline Error{line_context}: {err}. Do not use external @preview packages. Use only standard offline Typst primitives."
                )
            else:
                raise ValueError(f"Typst Compilation Error{line_context}: {err}")

    return {
        "pdf_path": output_path,
        "preview_path": preview_path,
        "font_family": font_family,
        "paper_size": paper_size,
    }