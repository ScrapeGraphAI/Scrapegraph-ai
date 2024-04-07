from langchain_community.llms import Ollama

llm = Ollama(model="llama2")

answer = llm.invoke("Tell me a joke")

print(answer)