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

class State(dict):
    query: str
    response: str
    summary: str


graph = StateGraph(State)
graph.add_node("retrieve_docs", retrieve_docs)
graph.add_node("ask_model", call_llm)
graph.add_node("summarize_answer", summarize_answer)

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