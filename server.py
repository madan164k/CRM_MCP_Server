from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("crm", stateless_http=True,port=8002, json_response=True)


class Contact(BaseModel):
    id: str
    name: str
    email: str | None = None
    stage: str | None = None


FAKE_DB = [
    Contact(id="1", name="Madan", email="madanlalmegh2@gmail.com", stage="Lead"),
    Contact(id="2", name="Subhash", email="subhashmendh@gmail.com", stage="Negotiation"),
]


class FakeCrmService:
    async def search(self, query: str, limit: int) -> list[Contact]:
        q = query.lower()
        hits = [c for c in FAKE_DB if q in c.name.lower() or q in (c.email or "").lower()]
        return hits[:limit]

    async def move_stage(self, deal_id: str, stage: str, idempotency_key: str) -> dict:
        for c in FAKE_DB:
            if c.id == deal_id:
                c.stage = stage
                return {"ok": True, "deal_id": deal_id, "stage": stage}
        return {"ok": False, "error": "deal not found"}


crm_service = FakeCrmService()


@mcp.tool()
async def search_contacts(
    query: Annotated[str, Field(description="Name, email or company. Use before create_lead to avoid duplicates.")],
    limit: Annotated[int, Field(le=25)] = 10,
) -> list[Contact]:
    """Search CRM contacts. Read-only."""
    return await crm_service.search(query, limit)


@mcp.tool()
async def update_deal_stage(deal_id: str, stage: str, idempotency_key: str) -> dict:
    """WRITE. Moves deal to a new stage. Requires human approval on the agent side."""
    return await crm_service.move_stage(deal_id, stage, idempotency_key)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")