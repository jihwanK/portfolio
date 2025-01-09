
retriever = vector_index.as_retriever(search_type="mmr", search_kwargs={"k": 3})

# test
result = retriever.get_relevant_documents("What is solar system?")

for d in result:
    print(d.page_content)
    print("===")

