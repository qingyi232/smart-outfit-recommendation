# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client
import time

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False

doc_path = r'F:\26毕设2\基于环境信息感知的智能出行穿衣服务系统\通信工程（专转本）Z2024130143陈鎏-基于环境信.docx'
doc = word.Documents.Open(doc_path, ReadOnly=True)
time.sleep(3)

WD_PAGE = 3

print('=== 修改后文档中图标题的实际页码 ===')
for i, para in enumerate(doc.Paragraphs):
    text = para.Range.Text.strip()
    if not text:
        continue
    style_name = para.Style.NameLocal
    if style_name == '图目录' or (style_name == '正文' and text.startswith('图5.') and '  ' in text[:12] and len(text) < 30):
        page = para.Range.Information(WD_PAGE)
        print(f'  page={page} | {text}')

print()
print('=== 修改后文档中表标题的实际页码 ===')
for i, para in enumerate(doc.Paragraphs):
    text = para.Range.Text.strip()
    if not text:
        continue
    style_name = para.Style.NameLocal
    if text.startswith('表') and ('.' in text[:8]) and '  ' in text[:12]:
        page = para.Range.Information(WD_PAGE)
        if style_name in ('样式2', '正文') and len(text) < 40:
            print(f'  page={page} style={style_name} | {text}')

doc.Close(False)
try:
    word.Quit()
except:
    pass
print('\nDone')
