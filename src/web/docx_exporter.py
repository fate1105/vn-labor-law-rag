"""
Pure-Python OOXML (.docx) Exporter chuẩn thể thức Nghị định 30/2020/NĐ-CP.
Không cần cài đặt thư viện ngoài (chạy mượt trên cả Windows Local lẫn Streamlit Cloud).
- Khổ giấy A4 (210mm x 297mm)
- Lề chuẩn NĐ 30: Trên 2cm, Dưới 2cm, Trái 3cm, Phải 2cm
- Phông chữ: Times New Roman 13pt (tiêu chuẩn hành chính Việt Nam)
"""

import io
import re
import zipfile
from xml.sax.saxutils import escape as xml_escape

_BR_RE = re.compile(r"(?i)(?:<br\s*/?>|&lt;br\s*/?&gt;)")

_CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

_DOC_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

_STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="26"/>
        <w:szCs w:val="26"/>
        <w:lang w:val="vi-VN"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="100" w:line="288" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="26"/>
      <w:szCs w:val="26"/>
    </w:rPr>
  </w:style>
</w:styles>"""

# Token inline hỗ trợ: **bold**, *italic*, <b>, <strong>, <i>, <em>, <u>
_INLINE_TOKEN_RE = re.compile(
    r"(\*\*[^\*]+?\*\*|(?<!\*)\*[^\*\n]+?\*(?!\*)|<(?:b|strong)>.*?</(?:b|strong)>|<(?:i|em)>.*?</(?:i|em)>|<u>.*?</u>)",
    flags=re.IGNORECASE | re.DOTALL,
)


def _make_run_xml(text: str, bold: bool = False, italic: bool = False, underline: bool = False, size_half_pt: int = 26) -> str:
    if not text:
        return ""
    rpr = [
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>',
        f'<w:sz w:val="{size_half_pt}"/>',
        f'<w:szCs w:val="{size_half_pt}"/>',
    ]
    if bold:
        rpr.append("<w:b/>")
    if italic:
        rpr.append("<w:i/>")
    if underline:
        rpr.append('<w:u w:val="single"/>')
    return f'<w:r><w:rPr>{"".join(rpr)}</w:rPr><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'


def _inline_to_runs_xml(raw_text: str, force_bold: bool = False, size_half_pt: int = 26) -> str:
    """Chuyển chuỗi Markdown/HTML nhẹ thành các <w:r> chuẩn OOXML."""
    parts = _BR_RE.split(raw_text)
    xml_chunks = []
    for p_idx, part in enumerate(parts):
        if p_idx > 0:
            xml_chunks.append("<w:r><w:br/></w:r>")
        clean_part = part.replace("&nbsp;", " ")
        pos = 0
        for m in _INLINE_TOKEN_RE.finditer(clean_part):
            if m.start() > pos:
                xml_chunks.append(_make_run_xml(clean_part[pos:m.start()], bold=force_bold, size_half_pt=size_half_pt))
            tok = m.group(0)
            low = tok.lower()
            if tok.startswith("**") and tok.endswith("**"):
                inner = tok[2:-2]
                xml_chunks.append(_make_run_xml(inner, bold=True, size_half_pt=size_half_pt))
            elif tok.startswith("*") and tok.endswith("*"):
                inner = tok[1:-1]
                xml_chunks.append(_make_run_xml(inner, bold=force_bold, italic=True, size_half_pt=size_half_pt))
            elif low.startswith(("<b>", "<strong>")):
                inner = re.sub(r"</?(?:b|strong)>", "", tok, flags=re.IGNORECASE)
                xml_chunks.append(_make_run_xml(inner, bold=True, size_half_pt=size_half_pt))
            elif low.startswith(("<i>", "<em>")):
                inner = re.sub(r"</?(?:i|em)>", "", tok, flags=re.IGNORECASE)
                xml_chunks.append(_make_run_xml(inner, bold=force_bold, italic=True, size_half_pt=size_half_pt))
            elif low.startswith("<u>"):
                inner = re.sub(r"</?u>", "", tok, flags=re.IGNORECASE)
                xml_chunks.append(_make_run_xml(inner, bold=force_bold, underline=True, size_half_pt=size_half_pt))
            pos = m.end()
        if pos < len(clean_part):
            xml_chunks.append(_make_run_xml(clean_part[pos:], bold=force_bold, size_half_pt=size_half_pt))
    return "".join(xml_chunks)


def _make_paragraph_xml(
    raw_text: str,
    align: str = "both",
    force_bold: bool = False,
    size_half_pt: int = 26,
    space_before: int = 0,
    space_after: int = 100,
    left_indent: int = 0,
) -> str:
    ppr = [f'<w:jc w:val="{align}"/>', f'<w:spacing w:before="{space_before}" w:after="{space_after}" w:line="288" w:lineRule="auto"/>']
    if left_indent > 0:
        ppr.append(f'<w:ind w:left="{left_indent}"/>')
    runs = _inline_to_runs_xml(raw_text, force_bold=force_bold, size_half_pt=size_half_pt)
    return f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{runs}</w:p>'


def _make_table_xml(table_lines: list[str]) -> str:
    """Chuyển bảng Markdown sang bảng OOXML (<w:tbl>): 2 cột không viền cho Quốc hiệu/Chữ ký, 3+ cột có viền."""
    rows = []
    aligns = []
    for tl in table_lines:
        cells = [c.strip() for c in tl.strip().strip("|").split("|")]
        if cells and all(re.match(r"^:?-{2,}:?$", c.replace(" ", "")) for c in cells if c != ""):
            aligns = [
                "center" if (c.startswith(":") and c.endswith(":"))
                else "right" if c.endswith(":")
                else "left"
                for c in cells
            ]
            continue
        rows.append(cells)

    if not rows:
        return ""

    num_cols = max(len(r) for r in rows)
    total_w = 9071  # Khổ khả dụng A4 chuẩn NĐ 30 (16cm = 9071 twips)

    if num_cols == 2:
        borders = (
            '<w:tblBorders>'
            '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
            '<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
            '</w:tblBorders>'
        )
        col_widths = [4173, 4898]
        tr_xml = []
        for r in rows:
            while len(r) < 2:
                r.append("")
            c0_up, c1_up = r[0].upper(), r[1].upper()
            al0 = "center" if any(k in c0_up for k in ["ỦY BAN", "CÔNG TY", "SỞ ", "PHÒNG "]) else (aligns[0] if len(aligns) > 0 else "left")
            al1 = "center" if any(k in c1_up for k in ["CỘNG HÒA", "CHỦ TỊCH", "GIÁM ĐỐC", "KT.", "TM.", "NGƯỜI LẬP", "ĐẠI DIỆN"]) else (aligns[1] if len(aligns) > 1 else "center")
            tcs = []
            for idx, (cell, w, al) in enumerate(zip(r[:2], col_widths, [al0, al1])):
                p_xml = _make_paragraph_xml(cell, align=al, size_half_pt=25, space_after=60)
                tcs.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr>{p_xml}</w:tc>')
            tr_xml.append(f'<w:tr>{"".join(tcs)}</w:tr>')
        return (
            f'<w:tbl><w:tblPr><w:tblW w:w="{total_w}" w:type="dxa"/>{borders}</w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{col_widths[0]}"/><w:gridCol w:w="{col_widths[1]}"/></w:tblGrid>'
            f'{"".join(tr_xml)}</w:tbl>'
        )

    # Bảng dữ liệu 3+ cột có viền mảnh
    borders = (
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="475569"/>'
        '<w:left w:val="single" w:sz="4" w:color="475569"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="475569"/>'
        '<w:right w:val="single" w:sz="4" w:color="475569"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="475569"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="475569"/>'
        '</w:tblBorders>'
    )
    col_w = total_w // num_cols
    grid = "".join(f'<w:gridCol w:w="{col_w}"/>' for _ in range(num_cols))
    tr_xml = []
    for r_idx, r in enumerate(rows):
        while len(r) < num_cols:
            r.append("")
        tcs = []
        for c_idx, cell in enumerate(r[:num_cols]):
            al = aligns[c_idx] if c_idx < len(aligns) else "left"
            p_xml = _make_paragraph_xml(cell, align=al, force_bold=(r_idx == 0), size_half_pt=24, space_after=40)
            tcs.append(f'<w:tc><w:tcPr><w:tcW w:w="{col_w}" w:type="dxa"/></w:tcPr>{p_xml}</w:tc>')
        tr_xml.append(f'<w:tr>{"".join(tcs)}</w:tr>')
    return f'<w:tbl><w:tblPr><w:tblW w:w="{total_w}" w:type="dxa"/>{borders}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(tr_xml)}</w:tbl>'


def build_nd30_docx_bytes(markdown_text: str) -> bytes:
    """Chuyển nội dung dự thảo Agent 4 thành file Microsoft Word (.docx) chuẩn A4 Nghị định 30/2020/NĐ-CP."""
    cleaned = (markdown_text or "").strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\s*\n", "", cleaned)
    cleaned = re.sub(r"\n```\s*$", "", cleaned)

    raw_lines = cleaned.split("\n")
    body_parts = []
    idx = 0
    while idx < len(raw_lines):
        line = raw_lines[idx]
        raw_strip = line.strip()

        if raw_strip.startswith("|") and raw_strip.endswith("|") and raw_strip.count("|") >= 2:
            tbl_block = []
            while idx < len(raw_lines):
                cur_s = raw_lines[idx].strip()
                if cur_s.startswith("|") and cur_s.endswith("|") and cur_s.count("|") >= 2:
                    tbl_block.append(cur_s)
                    idx += 1
                else:
                    break
            body_parts.append(_make_table_xml(tbl_block))
            continue

        idx += 1
        sub_lines = _BR_RE.split(line) if _BR_RE.search(line) else [line]
        for sub in sub_lines:
            sub_strip = sub.strip()
            if not sub_strip:
                body_parts.append('<w:p><w:pPr><w:spacing w:after="60"/></w:pPr></w:p>')
                continue
            if sub_strip in ("---", "***", "___"):
                body_parts.append(
                    '<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="94A3B8"/></w:pBdr>'
                    '<w:spacing w:before="80" w:after="120"/></w:pPr></w:p>'
                )
                continue

            if sub_strip.startswith("### "):
                body_parts.append(_make_paragraph_xml(sub_strip[4:], align="center", force_bold=True, size_half_pt=26, space_before=120, space_after=80))
                continue
            elif sub_strip.startswith("## "):
                body_parts.append(_make_paragraph_xml(sub_strip[3:], align="center", force_bold=True, size_half_pt=28, space_before=140, space_after=100))
                continue
            elif sub_strip.startswith("# "):
                body_parts.append(_make_paragraph_xml(sub_strip[2:], align="center", force_bold=True, size_half_pt=30, space_before=160, space_after=120))
                continue

            plain_up = re.sub(r"[\*\_\#\<\/buistrongem>]", "", sub_strip).strip().upper()
            if "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in plain_up:
                body_parts.append(_make_paragraph_xml(sub_strip, align="center", force_bold=True, size_half_pt=26, space_after=40))
            elif "ĐỘC LẬP - TỰ DO - HẠNH PHÚC" in plain_up:
                body_parts.append(_make_paragraph_xml(sub_strip, align="center", force_bold=True, size_half_pt=26, space_after=120))
            elif any(plain_up.startswith(k) for k in ("GIẤY MỜI", "CÔNG VĂN", "BIÊN BẢN", "QUYẾT ĐỊNH", "THÔNG BÁO", "BÁO CÁO", "TỜ TRÌNH")):
                body_parts.append(_make_paragraph_xml(sub_strip, align="center", force_bold=True, size_half_pt=28, space_before=160, space_after=100))
            elif sub_strip.startswith(("- ", "* ", "• ")):
                body_parts.append(_make_paragraph_xml(f"– {sub_strip[2:]}", align="both", size_half_pt=26, space_after=80, left_indent=360))
            else:
                body_parts.append(_make_paragraph_xml(sub_strip, align="both", size_half_pt=26, space_after=100))

    # Khổ giấy A4 chuẩn NĐ 30/2020/NĐ-CP: Rộng 210mm (11906), Cao 297mm (16838), Lề Trái 3cm (1701), Trên/Dưới/Phải 2cm (1134)
    sect_pr = (
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1701" w:header="708" w:footer="708" w:gutter="0"/>'
        '</w:sectPr>'
    )
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{"".join(body_parts)}{sect_pr}</w:body>'
        '</w:document>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", _RELS_XML)
        zf.writestr("word/_rels/document.xml.rels", _DOC_RELS_XML)
        zf.writestr("word/styles.xml", _STYLES_XML)
        zf.writestr("word/document.xml", doc_xml)
    return buf.getvalue()
