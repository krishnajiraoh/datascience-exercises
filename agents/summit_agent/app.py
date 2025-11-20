from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from langfuse.langchain import CallbackHandler

import asyncio
import logging

from langfuse import get_client
import bentoml
from dotenv import load_dotenv

load_dotenv()
langfuse = get_client()

logging.basicConfig(level=logging.DEBUG)

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

langfuse_handler = CallbackHandler()

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


# ---------------------------------------------------------
# ASYNC GRAPH LOADER
# ---------------------------------------------------------
async def load_graph():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("Tools loaded")

            model = ChatOpenAI(
                api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
                base_url="https://genai-gateway.azure-api.net/",
                model="gpt-4"
            )
            model = model.bind_tools(tools)

            # --- Node function ---
            def call_model(state: MessagesState):
                response = model.invoke(state["messages"])
                return {"messages": [*state["messages"], response]}

            # --- Build Graph ---
            builder = StateGraph(MessagesState)

            builder.add_node("call_model", call_model)
            builder.add_node("tools", ToolNode(tools))

            builder.add_edge(START, "call_model")

            builder.add_conditional_edges(
                "call_model",
                tools_condition,
            )

            builder.add_edge("tools", "call_model")
            graph = builder.compile()

            print("Graph Compiled")
            return graph


# ---------------------------------------------------------
# MUST LOAD GRAPH ASYNC BEFORE BENTOML STARTS
# ---------------------------------------------------------
graph = asyncio.run(load_graph())


# ---------------------------------------------------------
# BENTOML SERVICE
# ---------------------------------------------------------
svc = bentoml.Service("ITSM_Agent")

@bentoml.task
async def chat(data):
    print("Invoking message")

    sr_response = await graph.ainvoke(
        {"messages": [data["prompt"]]},
        config={"callbacks": [langfuse_handler]}
    )

    return {
        "response": sr_response["messages"][-1].content
    }