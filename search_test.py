"""可直接运行的真实向量检索冒烟测试，不消耗 LLM API。"""
from rag import retrieve

def main():
    question = '考试作弊会受到什么处分？'
    sources = retrieve(question)
    assert sources, '没有检索结果'
    assert any('考试纪律' in s['document'] and '作弊' in s['text'] for s in sources), '未命中考试纪律'
    for s in sources:
        print(s['document'],s['article'],s['start_page'],s['end_page'],round(s['score'],3))
        print(s['text'][:180])
    print('检索测试通过')

if __name__ == '__main__':
    main()

