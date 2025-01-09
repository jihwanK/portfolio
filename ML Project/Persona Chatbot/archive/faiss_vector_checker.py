import faiss
import numpy as np

def load_faiss_index(index_filename='faiss_index.index'):
    # FAISS 인덱스 읽기
    index = faiss.read_index(index_filename)
    return index

def search(index, query_vector, top_k=5):
    # FAISS 인덱스에서 검색
    D, I = index.search(query_vector, top_k)
    return I, D

def main():
    # FAISS 인덱스 읽기
    index = load_faiss_index()
    
    # 쿼리 벡터 예시
    query_vector = np.random.random((1, index.d)).astype(np.float32)
    
    # 검색
    top_k = 5
    indices, distances = search(index, query_vector, top_k)
    
    print("Indices:", indices)
    print("Distances:", distances)

if __name__ == "__main__":
    main()