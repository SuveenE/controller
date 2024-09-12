import logging
from typing import Any, Optional

import openai

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.slack import SlackClient
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.slack import (
    SlackGetChannelIdRequest,
    SlackSendMessageRequest,
)
from app.models.query import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


class SlackPostRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info("SlackPostRequestAgent no tools call error response: %s", response)
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        client = SlackClient(access_token=access_token)
        match function_name:
            case SlackSendMessageRequest.__name__:
                client_response = client.send_message(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not client_response["ok"]:
                    return AgentResponse(
                        agent=SUMMARY_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content=f"Failed to send slack message. Please check the message history and advise the user on what might be the cause of the problem.\nError: {client_response['error']}",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content="Slack message is sent successfully",
                    ),
                )


SLACK_POST_REQUEST_AGENT = SlackPostRequestAgent(
    name="Post Request Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at sending information to slack. Your task is to help a user send information by supplying the correct request to the slack API.",
    tools=[openai.pydantic_function_tool(SlackSendMessageRequest)],
)

##############################################


class SlackGetRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info("SlackGetRequestAgent no tools call error response: %s", response)
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        client = SlackClient(access_token=access_token)
        match function_name:
            case SlackGetChannelIdRequest.__name__:
                client_response: list[dict[str, Any]] = client.get_all_channel_ids(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not client_response:
                    return AgentResponse(
                        agent=SUMMARY_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="No channel IDs were retrieved. Please check the message history to advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content="Here are the channel ids of the requested channel names",
                        data=client_response,
                    ),
                )


SLACK_GET_REQUEST_AGENT = SlackGetRequestAgent(
    name="Get Request Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving information from slack. Your task is to help a user retrieve information by supplying the correct request to the slack API.",
    tools=[openai.pydantic_function_tool(SlackGetChannelIdRequest)],
)

##############################################


def transfer_to_get_request_agent() -> SlackGetRequestAgent:
    return SLACK_GET_REQUEST_AGENT


def transfer_to_post_request_agent() -> SlackPostRequestAgent:
    return SLACK_POST_REQUEST_AGENT


SLACK_TRIAGE_AGENT = TriageAgent(
    name="Triage Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Take note of the following:

1. Always look at the chat history to see if the information you need to proceed with the next stage of the task is available. If it is already available, do not request for it again.
2. To send a message, you need to pass SlackPostRequestAgent the channel_id "CXXXXXXXXXX". If the channel_id is not provided by the user or available in the chat history, you can retrieve the channel_id by transferring the task to the SlackGetRequestAgent.
3. Do not pass any parameters into your tools.
""",
    tools=[
        transfer_to_post_request_agent,
        transfer_to_get_request_agent,
        transfer_to_summary_agent,
    ],
)
