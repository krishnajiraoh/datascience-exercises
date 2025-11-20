import openai

from langgraph.graph import StateGraph, END
from langfuse.langchain import CallbackHandler


from langfuse import get_client

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

# 2️⃣ Define simple state
class State(dict):
    query: str
    response: str
    summary: str

def retrieve_docs(state: State):
    query = state.get("query", "")
    docs = [f"Document related to '{query}'", "Supporting context text"]
    state["docs"] = docs
    print("📄 Retrieved docs:", docs)
    return state

# 3️⃣ Create a node that calls OpenAI and logs via Langfuse
def call_llm(state: State):
    """llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result = llm.invoke(state["query"], callbacks=[langfuse_handler])
    state["response"] = result.content
    return state
    """
    client = openai.OpenAI(
        api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
        base_url="https://genai-gateway.azure-api.net/"
    )
    response = client.chat.completions.create(
        model= "gpt-4",  # model to send to the proxy
        messages=[
            {
                "role": "user",
                "content": state["query"]
            }
            ]
    )
    state["response"] = response.choices[0].message.content
    return state

def summarize_answer(state: State):
    query_response = state["response"]
    client = openai.OpenAI(
        api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
        base_url="https://genai-gateway.azure-api.net/"
    )
    response = client.chat.completions.create(
        model="gpt-4",  # model to send to the proxy
        messages=[
            {
                "role": "user",
                "content": f"Summarize this answer in one line:\n{query_response}"
            }
        ]
    )
    state["summary"] = response.choices[0].message.content
    return state

# 4️⃣ Build LangGraph
graph = StateGraph(State)
graph.add_node("retrieve_docs", retrieve_docs)
graph.add_node("ask_model", call_llm)
graph.add_node("summarize_answer", summarize_answer)

# Define flow
graph.set_entry_point("retrieve_docs")
graph.add_edge("retrieve_docs", "ask_model")
graph.add_edge("ask_model", "summarize_answer")
graph.add_edge("summarize_answer", END)

app = graph.compile()


# 5️⃣ Run the agent
if __name__ == "__main__":
    # Initialize Langfuse CallbackHandler for Langchain (tracing)
    langfuse_handler = CallbackHandler()

    result = app.invoke({"query": "Explain LangGraph in one line."},
                        config={"callbacks": [langfuse_handler]})

    print("Agent output - Response\n:", result["response"])
    print("Agent output - Summary\n:", result["summary"])

    # Optional: flush logs to Langfuse dashboard
    #langfuse_handler.flush()