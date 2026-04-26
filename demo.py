"""
AgentOS Demo

Prerequisites:
uv pip install -U fastapi uvicorn sqlalchemy pgvector psycopg openai ollama mcp registry ddgs
"""

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.models.ollama import OllamaResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.tools.websearch import WebSearchTools
from agno.os import AgentOS
from agno.team import Team
from agno.tools.hackernews import HackerNewsTools
from agno.tools.mcp import MCPTools
from agno.vectordb.pgvector import PgVector
from agno.registry import Registry

# Database connection
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

studio_db = PostgresDb(db_url="postgresql+psycopg://ai:ai@localhost:5532/ai")

# Create Postgres-backed memory store
db = PostgresDb(db_url=db_url)

# Create Postgres-backed vector store
vector_db = PgVector(
    db_url=db_url,
    table_name="agno_docs",
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)
knowledge = Knowledge(
    name="Agno Docs",
    contents_db=db,
    vector_db=vector_db,
)

# Create your agents
agno_agent = Agent(
    name="Agno Agent",
    model=OllamaResponses(id="glm-4.7-flash:cloud"),
    tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
    db=db,
    update_memory_on_run=True,
    knowledge=knowledge,
    markdown=True,
)

simple_agent = Agent(
    name="Simple Agent",
    role="Simple agent",
    id="simple_agent",
    model=OllamaResponses(id="glm-4.7-flash:cloud"),
    instructions=["You are a simple agent"],
    db=db,
    update_memory_on_run=True,
)

research_agent = Agent(
    name="Research Agent",
    role="Research agent",
    id="research_agent",
    model=OllamaResponses(id="glm-4.7-flash:cloud"),
    instructions=["You are a research agent"],
    tools=[HackerNewsTools(), HackerNewsTools()],
    db=db,
    update_memory_on_run=True,
)

# Create a team
research_team = Team(
    name="Research Team",
    description="A team of agents that research the web",
    members=[research_agent, simple_agent],
    model=OllamaResponses(id="glm-4.7-flash:cloud"),
    id="research_team",
    instructions=[
        "You are the lead researcher of a research team! 🔍",
    ],
    db=db,
    update_memory_on_run=True,
    add_datetime_to_context=True,
    markdown=True,
)

registry = Registry(
    name="My Registry",
    tools=[WebSearchTools()],
    models=[OllamaResponses(id="glm-4.7-flash:cloud")],
    dbs=[
        studio_db
    ],  # Studio requires the `db` parameter to save and load agents, teams, and workflows.
)

# Create the AgentOS
agent_os = AgentOS(
    id="agentos-demo",
    agents=[agno_agent],
    teams=[research_team],
    registry=registry,
    db=studio_db,
)
app = agent_os.get_app()


if __name__ == "__main__":
    agent_os.serve(app="demo:app", port=8000)
