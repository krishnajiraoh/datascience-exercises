from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

import openai 
import asyncio

async def main():

    client = MultiServerMCPClient(
        {
            "summit": {
                "command": "python",
                "args": ["server.py"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()

    async def call_model(state: MessagesState):
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
        #state["response"] = response.choices[0].message.content
        #return state
        return {"messages": response.choices[0].message.content}

    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")

    graph = builder.compile()
    sr_response = graph.ainvoke({"messages": "list incidents for user remya.panicker@symphonyai.com "})
    print(sr_response)


if __name__ == "__main__":
    asyncio.run(main())