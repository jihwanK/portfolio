# 프로젝트 이름

**푸와 친구들의 고민상담**

## 프로젝트 소개
이 프로젝트는 곰돌이 푸우의 긍정적이고 따뜻한 페르소나를 활용한 상담용 챗봇을 개발하는 것을 목표로 합니다. 소설 속 푸와 친구들의 밝은 성격을 통해 사용자에게 긍정적인 에너지를 전달하고, 고민 속에서도 마음의 평화를 찾도록 돕고자 합니다.

### 목표
- LLM을 활용하여 대화의 자연스러움과 깊이를 확보합니다. 
- Langchain을 통해 대화의 흐름을 효과적으로 관리하고 확장합니다. 
- RAG를 사용하여 관련 정보를 정확하게 검색하고 제공합니다. 
- Prompt 기능을 통해 다양한 사용자 요구에 맞는 답변을 생성합니다. 
- Streamlit Front를 사용해 사용자 친화적인 인터페이스를 구현합니다.

<br>

## 팀원 구성

<div align="center">

| **김지환** | **김서현** | **최정은** | **김민수** | **박주연** |
| :------: |  :------: | :------: | :------: | :------: |
|[<img src="https://avatars.githubusercontent.com/u/17960812?v=4" height=150 width=150> <br/> @jihwanK](https://github.com/jihwanK) |[<img src="https://avatars.githubusercontent.com/u/177704202?v=4" height=150 width=150> <br/> @tjgusKim](https://github.com/tjgusKim) |[<img src="https://avatars.githubusercontent.com/u/177805026?v=4" height=150 width=150> <br/> @Insight7321](https://github.com/Insight7321) |[<img src="https://avatars.githubusercontent.com/u/175805884?v=4" height=150 width=150> <br/> @GoldDuck0108](https://github.com/GoldDuck0108) |[<img src="https://avatars.githubusercontent.com/u/40532035?v=4" height=150 width=150> <br/> @pbcs0321](https://github.com/pbcs0321) |
</div>

<br>

## 1. 개발 환경

- 주 언어 : Python
- 버전 및 이슈관리 : Git, [GitHub(@jihwanK/chatbot)](https://github.com/jihwanK/chatbot)
- 협업 툴 : Slack, Notion

<br>

## 2. 채택한 개발 기술과 브랜치 전략

### LangChain

#### LangChain 컴포넌트
* `LLM`: OpenAI 등의 대규모 언어 모델을 래핑하여 사용합니다.
* `VectorStore`: FAISS를 사용하여 벡터 데이터베이스를 구현합니다.
* `Embeddings`: OpenAI의 임베딩 모델을 사용하여 텍스트를 벡터로 변환합니다.
* `ConversationBufferWindowMemory`: 대화 기록을 저장하고 관리합니다.
* `RunnableParallel`, `RunnablePassthrough`, `RunnableLambda`: 복잡한 체인 로직을 구성하는 데 사용됩니다.

#### 체인 구성
* `_chain` 메서드에서 여러 LangChain 컴포넌트를 조합하여 복잡한 대화 처리 파이프라인을 구성합니다.
* 컨텍스트 검색, 쿼리 처리, 대화 기록 관리 등의 작업을 연결합니다.

### RAG (Retrieval-Augmented Generation)

#### 벡터 저장소 구현
* `VectorStore` 클래스에서 FAISS를 사용하여 문서의 벡터 표현을 저장하고 검색합니다.
* 스크립트 파일에서 텍스트를 로드하고, 이를 벡터화하여 저장합니다.

#### 검색 기능
* `get_retriever` 메서드를 통해 MMR(Maximum Marginal Relevance) 검색 방식을 사용하는 검색기를 생성합니다.
* 사용자 쿼리와 관련된 가장 연관성 높은 문서를 검색합니다.

#### 검색 결과 활용
* `_merge_docs` 메서드에서 검색된 문서들을 하나의 컨텍스트로 병합합니다.
* 이 컨텍스트는 LLM에 입력되어 보다 정확하고 관련성 높은 응답을 생성하는 데 사용됩니다.

#### 대화 처리
* `_chat` 메서드에서 사용자 쿼리, 검색된 컨텍스트, 대화 기록을 결합하여 LLM에 전달합니다.
* LLM은 이 정보를 바탕으로 응답을 생성하며, 이는 RAG의 핵심 아이디어를 구현한 것입니다.

### 브랜치전략 
    
- 브랜치 전략
  - Git-flow 전략을 기반으로 main, dev 브랜치와 feature 보조 브랜치를 운용했습니다.
  - main, dev, feauter/X 브랜치로 나누어 개발을 하였습니다.
    - **main** 브랜치는 배포 단계에서만 사용하는 브랜치입니다.
    - **dev** 브랜치는 개발 단계에서 git-flow의 master 역할을 하는 브랜치입니다.
    - **feature/X** 브랜치는 기능 단위로 독립적인 개발 환경을 위하여 사용하고 merge 후 각 브랜치를 삭제해주었습니다.


<br>

## 3. 프로젝트 구조
```
.
├── README.md
├── __init__.py
├── chatbot.log
├── front.py
├── main.py
├── requirements.txt
├── setup.sh
├── archive
│   ├── PracticeChatHistory.py
│   ├── PracticeRetriever.py
│   ├── db_extract.py
│   ├── faiss_index.index
│   ├── faiss_vector_checker.py
│   ├── faiss_vector_store.py
│   └── pooh_script.json
├── artefact
│   ├── pooh_script.txt
│   └── pooh_faiss
│       ├── index.faiss
│       └── index.pkl
├── chatbot
│   ├── __init__.py
│   ├── chatbot.py
│   └── prompt.py
├── dataset
│   ├── pooh.txt
│   └── pooh2.txt
├── llm
│   ├── __init__.py
│   ├── anthropic_wrapper.py
│   ├── gemini_wrapper.py
│   ├── llm.py
│   ├── llm_base.py
│   ├── openai_wrapper.py
│   └── upstage_wrapper.py
├── utils
│   ├── __init__.py
│   └── logger.py
└── vector_store
    ├── __init__.py
    ├── data_extraction.py
    └── vector_store.py
```

<br>

## 4. 역할 분담

### 김지환

- 팀장; 전반적인 프로젝트 관리
- 프로젝트 설계 및 프롬프트 구현
- LangChain을 활용하여 chat memory와 chain 구현
- Vector Store 구현
- 전체 코드 병합 및 리팩토링

### 김서현

- LangChain을 활용하여 chat memory와 chain 구현
- 데모 페이지 구현 (streamlit 활용)
    
### 최정은

- 챗봇 시나리오 구상
- Raw Data 수집
- 데이터 가공
- Vector Store 구현
    
### 김민수

- 주제 선정에 관한 고민

### 박주연

- LLM 모듈 구현
- 발표 시나리오 구상

<br>

## 5. 개발 기간

### 개발 기간
- 전체 개발 기간: 2024-08-12 ~ 2024-08-19
- 기능 구현: 2024-08-14 ~ 2024-08-17
- 수정 및 보완: 2024-08-18 ~ 2024-08-19


<br>


