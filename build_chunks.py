"""按正文标题和行首条款切分，保留真实 PDF 页码。"""
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
PDF_FILE = ROOT / '南京邮电大学学生手册（2025版）.pdf'
FALLBACK = PDF_FILE.stem
ARTICLE = re.compile(r'^第[一二三四五六七八九十百千万零〇两\d]+条')

def compact(text):
    return re.sub(r'\s+', '', text)

def build_chunks():
    reader = PdfReader(PDF_FILE)
    titles = set()
    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
            elif len(compact(item.get('/Title', ''))) >= 6:
                titles.add(compact(item['/Title']))
    walk(reader.outline)
    chunks, current = [], None
    document, fresh = FALLBACK, False
    def flush():
        nonlocal current
        if current and current['text'].strip():
            chunks.append(current)
        current = None
    for page_number, page in enumerate(reader.pages, 1):
        # 该版本前 15 页为封面、简介和目录。
        if page_number <= 15:
            continue
        lines = [re.sub(r'·\s*[\dIVX]+\s*·', '', x).strip()
                 for x in (page.extract_text() or '').splitlines()]
        lines = [x for x in lines if x]
        i = 0
        while i < len(lines):
            title, count = None, 0
            for n in range(1, min(4, len(lines)-i)+1):
                candidate = compact(''.join(lines[i:i+n]))
                if candidate in titles:
                    title, count = candidate, n
            if title:
                flush()
                document, fresh = title, True
                i += count
                continue
            line = lines[i]
            match = ARTICLE.match(line)
            if match:
                article = match.group()
                if article == '第一条' and not fresh:
                    document = FALLBACK
                flush()
                fresh = False
                current = dict(document=document, article=article,
                               start_page=page_number, end_page=page_number, text=line)
            else:
                if current is None:
                    current = dict(document=document, article='相关段落',
                                   start_page=page_number, end_page=page_number, text='')
                current['text'] += line
                current['end_page'] = page_number
            if len(current['text']) >= 360:
                metadata = {k:v for k,v in current.items() if k != 'text'}
                flush()
                current = dict(metadata, start_page=page_number, text='')
            i += 1
    flush()
    (ROOT/'chunks.json').write_text(json.dumps(chunks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'生成 {len(chunks)} 条；请继续运行 build_index.py。')
    return chunks

if __name__ == '__main__':
    build_chunks()

