import logging
from typing import Optional

import openai

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.gmail import GmailClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.gmail import (
    Gmail,
    GmailGetEmailsRequest,
    GmailReadEmailsRequest,
    GmailSendEmailRequest,
    GmailUpdateEmailsRequest,
)
from app.models.query import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
##############################################


class GmailGetRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        client = GmailClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        match function_name:
            case GmailGetEmailsRequest.__name__:
                email_lst: list[Gmail] = client.get_emails(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not email_lst:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="No emails found for the given query",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content=f"Here are the retrieved emails",
                        data=[email.model_dump() for email in email_lst],
                    ),
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


GMAIL_GET_REQUEST_AGENT = GmailGetRequestAgent(
    name="Get Emails Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving emails via the Gmail API. Your task is to help a user retrieve a group of emails by supplying the correct query parameters to the gmail API. Each condition should be separated by a space.",
    tools=[openai.pydantic_function_tool(GmailGetEmailsRequest)],
)

##############################################


class GmailUpdateRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        client = GmailClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        match function_name:
            case GmailUpdateEmailsRequest.__name__:
                updated_emails: list[Gmail] = client.update_emails(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not updated_emails:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="No emails found for the given query",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content=f"Here are the updated emails",
                        data=[email.model_dump() for email in updated_emails],
                    ),
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


GMAIL_UPDATE_REQUEST_AGENT = GmailUpdateRequestAgent(
    name="Update Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at managing emails via the Gmail API. Your task is to help a user update the state of emails by supplying the correct query parameters to the gmail API. Follow the following rules:
    
1. Prioritise using the id as the filter condition of the query where possible.
2. If you are updating one particular labelId, make sure to include the other remaining labelIds that are not being updated as well.""",
    tools=[openai.pydantic_function_tool(GmailUpdateEmailsRequest)],
)

##############################################


class GmailPostRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        client = GmailClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        match function_name:
            case GmailSendEmailRequest.__name__:
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content=str(
                            client.send_email(
                                request=response.choices[0]
                                .message.tool_calls[0]
                                .function.parsed_arguments
                            )
                        ),
                    ),
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


GMAIL_POST_REQUEST_AGENT = GmailPostRequestAgent(
    name="Post Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at sending emails via the Gmail API. Your task is to help a user send an email by supplying the correct request parameters to the gmail API.",
    tools=[openai.pydantic_function_tool(GmailSendEmailRequest)],
)

##############################################


def transfer_to_gmail_post_request_agent() -> GmailPostRequestAgent:
    return GMAIL_POST_REQUEST_AGENT


def transfer_to_gmail_get_request_agent() -> GmailGetRequestAgent:
    return GMAIL_GET_REQUEST_AGENT


def transfer_to_gmail_update_request_agent() -> GmailUpdateRequestAgent:
    return GMAIL_UPDATE_REQUEST_AGENT


GMAIL_TRIAGE_AGENT = TriageAgent(
    name="Triage Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at choosing the right agent to perform the task described by the user.",
    tools=[
        transfer_to_gmail_post_request_agent,
        transfer_to_gmail_get_request_agent,
        transfer_to_gmail_update_request_agent,
        transfer_to_summary_agent,
    ],
)