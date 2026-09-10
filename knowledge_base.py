"""缓存模型和数据，并检查索引一致性。"""
import hashlib
import json
from pathlib import Path
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_NAME = 'BAAI/bge-small-zh-v1.5'
DOCUMENT = '南京邮电大学学生手册（2025版）'

@st.cache_resource
def load_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)

@st.cache_data
def _load(stamp):
    raw = (ROOT/'chunks.json').read_bytes()
    chunks = json.loads(raw)
    vectors = np.load(ROOT/'vectors.npy',allow_pickle=False)
    if not chunks or vectors.ndim != 2 or len(chunks) != len(vectors):
        raise ValueError('条款与向量数量不一致，请重新构建知识库。')
    if vectors.shape[1] != 512 or not np.isfinite(vectors).all():
        raise ValueError('向量格式不正确，请重新构建。')
    for c in chunks:
        if not all(k in c for k in ('document','article','start_page','end_page','text')):
            raise ValueError('知识库缺少来源信息。')
    manifest = ROOT/'index_meta.json'
    if manifest.exists():
        meta = json.loads(manifest.read_text(encoding='utf-8'))
        if meta['chunks_sha256'] != hashlib.sha256(raw).hexdigest() or meta['model'] != MODEL_NAME:
            raise ValueError('条款已更新，请运行 build_index.py 同步向量。')
    norms = np.linalg.norm(vectors,axis=1,keepdims=True)
    if (norms == 0).any():
        raise ValueError('索引含空向量。')
    return chunks, vectors/norms

def load_knowledge_base():
    try:
        names = ['chunks.json','vectors.npy']
        if (ROOT/'index_meta.json').exists():
            names.append('index_meta.json')
        stamp = tuple((ROOT/name).stat().st_mtime_ns for name in names)
        return _load(stamp)
    except FileNotFoundError:
        raise ValueError('缺少知识库，请运行 build_chunks.py 和 build_index.py。') from None

