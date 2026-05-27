# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

docx_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-毕业论文-.docx'
output_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-毕业论文-修改版.docx'

doc = Document(docx_path)

ref_pattern = re.compile(r'\[\d+\]')
xia_tu_patterns = ['如下图', '如下所示', '见下图']

changes_ref = 0
changes_xiatu = 0
changes_fig_title = 0

for para in doc.paragraphs:
    full_text = para.text.strip()

    # 批注3: 统一图名格式 - 检测以"图X-"开头的段落
    if re.match(r'^图\s*\d', full_text) and len(full_text) < 80:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.font.name = '宋体'
            run.font.size = Pt(10.5)  # 五号
            run.font.bold = True
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        changes_fig_title += 1

    for run in para.runs:
        if not run.text:
            continue

        # 批注0: 参考文献改上标
        if ref_pattern.search(run.text):
            run.font.superscript = True
            changes_ref += 1

        # 批注4/5: 替换"如下图"等
        for pat in xia_tu_patterns:
            if pat in run.text:
                run.text = run.text.replace(pat, '如相应图示所示')
                changes_xiatu += 1

doc.save(output_path)
print(f'参考文献上标处理: {changes_ref} 处')
print(f'如下图替换处理: {changes_xiatu} 处')
print(f'图名格式统一: {changes_fig_title} 处')
print(f'已保存到: {output_path}')
