# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from langfuse.langchain import CallbackHandler

import asyncio

from langfuse import get_client
import bentoml
from dotenv import load_dotenv

load_dotenv()
langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            print("Tools loaded")

            def call_model(state: MessagesState):
                response = model.invoke(state["messages"])
                return {"messages": [*state["messages"], response]}

            model = ChatOpenAI(
                api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
                base_url="https://genai-gateway.azure-api.net/",
                model="gpt-4"
            )
            model = model.bind_tools(tools)
            
            print("Creating Graph")

            builder = StateGraph(MessagesState)
            builder.add_node(call_model)
            builder.add_node(ToolNode(tools))
            builder.add_edge(START, "call_model")
            builder.add_conditional_edges(
                "call_model",
                tools_condition,
            )
            builder.add_edge("tools", "call_model")

            print("Compiling Graph")
            graph = builder.compile()

            print("Invoking message")
            sr_response = await graph.ainvoke({"messages": "list incidents for user remya.panicker@symphonyai.com "},
                                config={"callbacks": [langfuse_handler]})
            print(sr_response["messages"][3].content)

if __name__ == "__main__":
    langfuse_handler = CallbackHandler()
    asyncio.run(main())



svc = bentoml.Service("ITSM Agent")

@svc.api(input=bentoml.io.JSON(), output=bentoml.io.JSON())
def run_agent(data):
    graph.ainvoke({"messages": "list incidents for user remya.panicker@symphonyai.com "},
                                config={"callbacks": [langfuse_handler]})
    return app.invoke(data)