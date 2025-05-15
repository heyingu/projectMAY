from langchain.chains import RetrievalQA

def create_qa_chain(vectorstore, llm, prompt):
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )