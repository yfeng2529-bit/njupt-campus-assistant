"""生成向量和数据指纹；修改条款后必须重建。"""
import hashlib
import json
import os
import numpy as np
from knowledge_base import ROOT, MODEL_NAME, load_embedding_model

def build_index():
    raw = (ROOT/'chunks.json').read_bytes()
    chunks = json.loads(raw)
    texts = [f"规章名称：{c['document']}\n条款：{c['article']}\n内容：{c['text']}" for c in chunks]
    vectors = load_embedding_model().encode(texts,normalize_embeddings=True,show_progress_bar=True)
    with (ROOT/'vectors.tmp').open('wb') as f:
        np.save(f,vectors)
    os.replace(ROOT/'vectors.tmp',ROOT/'vectors.npy')
    (ROOT/'index_meta.json').write_text(json.dumps(dict(model=MODEL_NAME,
        chunks_sha256=hashlib.sha256(raw).hexdigest(),count=len(chunks)),indent=2),encoding='utf-8')
    print(f'完成：{len(chunks)} 条，向量形状 {vectors.shape}')

if __name__ == '__main__':
    build_index()

