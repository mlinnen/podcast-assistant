import os
from markdown_pdf import MarkdownPdf, Section

def convert_md_to_pdf(md_path, pdf_path=None):
    """
    Converts a Markdown file to a PDF file.
    If pdf_path is not provided, it will use the same name as md_path but with .pdf extension.
    """
    if not os.path.exists(md_path):
        print(f"Error: Markdown file not found at {md_path}")
        return None

    if pdf_path is None:
        pdf_path = os.path.splitext(md_path)[0] + ".pdf"

    try:
        pdf = MarkdownPdf(toc_level=2)
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        pdf.add_section(Section(md_content))
        pdf.save(pdf_path)
        return pdf_path
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return None

if __name__ == "__main__":
    # Simple test if run directly
    import sys
    if len(sys.argv) > 1:
        convert_md_to_pdf(sys.argv[1])
