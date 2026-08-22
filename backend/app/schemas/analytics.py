from pydantic import BaseModel


class TopQuery(BaseModel):
    query: str
    count: int


class AnalyticsOut(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_documents: int
    total_users: int
    top_search_queries: list[TopQuery]
