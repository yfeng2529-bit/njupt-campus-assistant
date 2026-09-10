from pypdf import PdfReader
from build_chunks import PDF_FILE

if __name__ == '__main__':
    reader = PdfReader(PDF_FILE)
    print('总页数：',len(reader.pages))
    print(reader.pages[50].extract_text())

