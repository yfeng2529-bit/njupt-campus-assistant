"""保留命令行入口，与网页共用 RAG。"""
from api_manager import load_connections
from config import API_KEY, BASE_URL, MODEL
from rag import retrieve, answer_question

def main():
    connections = load_connections()
    connection = next((c for c in connections if c.get('default')),None)
    connection = connection or dict(api_key=API_KEY,base_url=BASE_URL,model=MODEL)
    history = []
    print('校园知识助手（输入 exit 退出）')
    while True:
        question = input('你：').strip()
        if question.lower() in ('exit','quit'):
            break
        if not question:
            continue
        try:
            sources = retrieve(question,history)
            answer = answer_question(question,history,sources,connection)
            print(answer)
            print('参考来源：')
            for s in sources:
                print(s['document'],s['article'],f"PDF {s['start_page']}-{s['end_page']} 页")
            history.extend([dict(role='user',content=question),dict(role='assistant',content=answer)])
            history = history[-6:]
        except Exception:
            print('无法完成问答，请检查知识库、网络及 API 配置。')

if __name__ == '__main__':
    main()

