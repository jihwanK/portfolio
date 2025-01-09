import json
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# JSON 파일에서 데이터 가져오기
def load_from_json(filename='pooh_script.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# 벡터화 및 FAISS 인덱스 저장
def save_faiss_index(texts, index_filename='faiss_index.index'):
    # TF-IDF 벡터화
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    
    # FAISS 인덱스 생성
    dim = X.shape[1]
    index = faiss.IndexFlatL2(dim)
    faiss_index = faiss.IndexIDMap(index)
    
    # 벡터 추가
    vectors = X.toarray().astype(np.float32)
    ids = np.arange(len(texts), dtype=np.int64)
    faiss_index.add_with_ids(vectors, ids)
    
    # 인덱스 저장
    faiss.write_index(faiss_index, index_filename)

def main():
    # JSON 파일에서 데이터 읽기
    data = load_from_json()

    # 대사만을 추출
    dialogues = [item['dialogue'] for item in data]

    # 벡터화 및 FAISS 인덱스 저장
    save_faiss_index(dialogues)

if __name__ == "__main__":
    main()