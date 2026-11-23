import asyncio 
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main() ->None:
    client = MultiServerMCPClient({
        "crm":{"transport":"streamable_http", "url":"http://localhost:8002/mcp"}
    })
    tools = await client.get_tools()
    print([t.name for t in tools])
    search_tool = next(t for t in tools if t.name == "search_contacts")
    result = await search_tool.ainvoke({"query":"acme"})
    print(result)

asyncio.run(main())
