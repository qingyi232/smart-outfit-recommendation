import docx
import re

doc = docx.Document(r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-基于环境信.docx')

print("=" * 60)
print("SCANNING DOCUMENT PARAGRAPHS")
print("=" * 60)

table_pattern = re.compile(r'^表\s*[\d\.\-]+\s+')
figure_pattern = re.compile(r'^图\s*[\d\.\-]+\s+')
toc_table_pattern = re.compile(r'表\s*[\d\.\-]+')
toc_figure_pattern = re.compile(r'图\s*[\d\.\-]+')

tables_found = []
figures_found = []
toc_region = False
toc_table_entries = []
toc_figure_entries = []

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if not text:
        continue

    style_name = para.style.name if para.style else ''

    if table_pattern.match(text):
        tables_found.append((i, text[:80], style_name))

    if figure_pattern.match(text):
        figures_found.append((i, text[:80], style_name))

    if '表目录' in text or '图目录' in text:
        print(f"\n>>> FOUND TOC MARKER at para {i}: '{text}' [style: {style_name}]")
        toc_region = text

    if '表目录' in str(toc_region):
        if toc_table_pattern.search(text) and i > 0:
            toc_table_entries.append((i, text[:100], style_name))

    if '图目录' in str(toc_region):
        if toc_figure_pattern.search(text) and i > 0:
            toc_figure_entries.append((i, text[:100], style_name))

    if toc_region and text and not toc_table_pattern.search(text) and not toc_figure_pattern.search(text):
        if '目录' not in text and len(toc_table_entries) + len(toc_figure_entries) > 0:
            toc_region = False

print("\n" + "=" * 60)
print(f"TABLES IN DOCUMENT ({len(tables_found)} found):")
print("=" * 60)
for idx, text, style in tables_found:
    print(f"  para[{idx}] [{style}] {text}")

print(f"\nFIGURES IN DOCUMENT ({len(figures_found)} found):")
print("=" * 60)
for idx, text, style in figures_found:
    print(f"  para[{idx}] [{style}] {text}")

print(f"\nTABLE TOC ENTRIES ({len(toc_table_entries)} found):")
print("=" * 60)
for idx, text, style in toc_table_entries:
    print(f"  para[{idx}] [{style}] {text}")

print(f"\nFIGURE TOC ENTRIES ({len(toc_figure_entries)} found):")
print("=" * 60)
for idx, text, style in toc_figure_entries:
    print(f"  para[{idx}] [{style}] {text}")
