from pathlib import Path

from docx import Document


class DocxRenderer:
    def render(self, document_data: dict, output_path: Path) -> None:
        doc = Document()

        title = document_data.get("title")
        if title:
            doc.add_heading(title, level=1)

        for section in document_data.get("sections", []):
            heading = section.get("heading")
            if heading:
                doc.add_heading(heading, level=2)

            for item in section.get("content", []):
                item_type = item.get("type")
                if item_type == "paragraph":
                    doc.add_paragraph(item.get("text", ""))
                elif item_type == "bullet_list":
                    for bullet in item.get("items", []):
                        doc.add_paragraph(bullet, style="List Bullet")
                elif item_type == "table":
                    rows = item.get("rows", [])
                    if rows:
                        table = doc.add_table(rows=0, cols=len(rows[0]))
                        for row in rows:
                            cells = table.add_row().cells
                            for index, cell_text in enumerate(row):
                                cells[index].text = cell_text

        doc.save(output_path)
