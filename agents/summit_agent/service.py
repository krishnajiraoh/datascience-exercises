from __future__ import annotations

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from langfuse.langchain import CallbackHandler
from langfuse import get_client

import asyncio
import logging

import bentoml
from dotenv import load_dotenv

load_dotenv()
langfuse = get_client()

logging.basicConfig(level=logging.DEBUG)


@bentoml.service(
    name="ITSM_Agent",
    workers=2,
    #resources={"cpu": "2000m"},
    #envs=[{"name": "ANTHROPIC_API_KEY"}],
    #traffic={"concurrency": 16, "external_queue": True},
    #labels={"owner": "bentoml-team", "project": "langgraph-anthropic"},
    #image=IMAGE,
)
class ITSM_Agent:

    @bentoml.on_startup
    async def init_graph(self):

        self.langfuse_handler = CallbackHandler()

        client = MultiServerMCPClient(
            {
                "summit": {
                    "transport": "streamable_http",  # Local subprocess communication
                    "url" : "http://127.0.0.1:8000/mcp"
                }
            }
        )

        tools = await client.get_tools()
        model = ChatOpenAI(
            api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
            base_url="https://genai-gateway.azure-api.net/",
            model="gpt-4"
        )
        model = model.bind_tools(tools)

        # --- Node function ---
        def call_model(state: MessagesState):
            print(f"Message: {state['messages']}")
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
        self.graph = builder.compile()

        print("Graph Compiled")

    @bentoml.api
    async def chat(self, query: str):
        print("Invoking message")

        sr_response = await self.graph.ainvoke({"messages": query},
                    config={"callbacks": [self.langfuse_handler]}
        )

        return {
            "response": sr_response["messages"][-1].content
        }
