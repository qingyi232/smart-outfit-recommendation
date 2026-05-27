# -*- coding: utf-8 -*-
import zipfile
import re

docx_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-毕业论文-修改版.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

# 搜索公式标签
for tag in ['oMath', 'oMathPara', 'equation', 'fld']:
    count = doc_xml.count(tag)
    if count > 0:
        print(f'{tag}: {count} 次')

# 搜索包含公式文本的段落
from xml.etree import ElementTree as ET
root = ET.fromstring(doc_xml)
ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

formula_keywords = ['THI', 'sim(', 'cos(', '×', '÷', '∑', '∏']
chapter = 0

for para in root.iter('{%s}p' % ns_w):
    texts = []
    for t in para.iter('{%s}t' % ns_w):
        if t.text:
            texts.append(t.text)
    full = ''.join(texts).strip()
    
    ch_match = re.match(r'^(\d+)\s', full)
    if ch_match and len(full) < 40:
        chapter = int(ch_match.group(1))
    
    for kw in formula_keywords:
        if kw in full:
            print(f'[第{chapter}章] 含公式关键词"{kw}": {full[:80]}')
            break
    
    if '=' in full and len(full) < 100 and not full.startswith('图') and not full.startswith('表'):
        if any(c in full for c in ['×', '+', '-', '/', 'T', 'H', 'I', 'sim', 'cos']):
            if not full.startswith('http') and '。' not in full:
                print(f'[第{chapter}章] 疑似公式: {full}')
