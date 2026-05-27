# -*- coding: utf-8 -*-
"""精确处理参考文献上标：只对[数字]部分设上标，不影响其他文字"""
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from copy import deepcopy
import re

docx_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-毕业论文-.docx'
output_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-毕业论文-修改版.docx'

doc = Document(docx_path)

ref_pattern = re.compile(r'(\[\d+\])')
changes = 0

for para in doc.paragraphs:
    runs_to_process = []
    for run in para.runs:
        if run.text and ref_pattern.search(run.text):
            runs_to_process.append(run)
    
    for run in runs_to_process:
        text = run.text
        parts = ref_pattern.split(text)
        if len(parts) <= 1:
            continue
        
        # 获取原始格式
        original_rPr = run._element.find(qn('w:rPr'))
        
        # 清空当前run
        run.text = parts[0]
        
        # 在当前run之后插入分割的部分
        parent = run._element.getparent()
        insert_after = run._element
        
        for i, part in enumerate(parts[1:], 1):
            if not part:
                continue
            
            new_run = deepcopy(run._element)
            # 设置文本
            for t_elem in new_run.findall(qn('w:t')):
                new_run.remove(t_elem)
            t = new_run.makeelement(qn('w:t'), {})
            t.text = part
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            new_run.append(t)
            
            # 如果是[数字]格式，设为上标
            if ref_pattern.match(part):
                rPr = new_run.find(qn('w:rPr'))
                if rPr is None:
                    rPr = new_run.makeelement(qn('w:rPr'), {})
                    new_run.insert(0, rPr)
                vertAlign = rPr.makeelement(qn('w:vertAlign'), {qn('w:val'): 'superscript'})
                rPr.append(vertAlign)
                changes += 1
            
            insert_after.addnext(new_run)
            insert_after = new_run

doc.save(output_path)
print(f'精确上标处理完成: {changes} 处')
print(f'保存到: {output_path}')
