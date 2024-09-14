from app.config import OPENAI_GPT4O_MINI
from app.models.agents.base.summary import transfer_to_summary_agent
from app.models.agents.base.triage import TriageAgent
from app.models.integrations.base import Integration

CALENDAR_TRIAGE_AGENT = TriageAgent(
    name="Google Calendar Triage Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at choosing the right agent to perform the task described by the user. When you deem that the task is completed or cannot be completed, pass the task to the summary agent.",
    tools=[
        transfer_to_summary_agent,
    ],
)
