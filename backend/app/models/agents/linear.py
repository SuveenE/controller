import logging
from typing import Optional

import openai
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.linear import LinearClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.linear import (
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearGetIssuesRequest,
    LinearIssue,
    LinearUpdateIssuesRequest,
)
from app.models.query import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
openai_client = OpenAI()


class LinearPostRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "LinearPostRequestAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        linear_client = LinearClient(
            access_token=access_token,
        )
        try:
            match function_name:
                case LinearCreateIssueRequest.__name__:
                    try:
                        created_issue: LinearIssue = linear_client.create_issue(
                            request=response.choices[0]
                            .message.tool_calls[0]
                            .function.parsed_arguments
                        )
                    except Exception as e:
                        log.info(
                            "LinearPostRequestAgent create issue error message: %s", e
                        )
                        return AgentResponse(
                            agent=SUMMARY_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content=f"Failed to create issue. Please check the message history and error log to advise the user on what might be the cause of the problem.\nError: {e}",
                                error=True,
                            ),
                        )
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Issue created successfully",
                            data=[created_issue.model_dump()],
                        ),
                    )

                case _:
                    raise InferenceError(f"Function {function_name} not supported")

        except Exception as e:
            log.error(f"Error in LinearPostRequestAgent: {e}")
            raise e


LINEAR_POST_REQUEST_AGENT = LinearPostRequestAgent(
    name="Post Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at creating issues in Linear via the Linear API. Your task is to help a user create an issue by supplying the correct request parameters to the Linear API.",
    tools=[openai.pydantic_function_tool(LinearCreateIssueRequest)],
)

##############################################


class LinearGetRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info("LinearGetRequestAgent no tools call error response: %s", response)
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        linear_client = LinearClient(
            access_token=access_token,
        )

        try:
            match function_name:
                case LinearGetIssuesRequest.__name__:
                    retrieved_issues: list[LinearIssue] = linear_client.get_issues(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments
                    )
                    if not retrieved_issues:
                        return AgentResponse(
                            agent=SUMMARY_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="No Linear issues were retrieved. Please check the message history to advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                                error=True,
                            ),
                        )
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Here are the retrieved Linear issues",
                            data=[issue.model_dump() for issue in retrieved_issues],
                        ),
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in LinearGetRequestAgent: {e}")
            raise e


# TODO: Add AND/OR logic to the input model
LINEAR_GET_REQUEST_AGENT = LinearGetRequestAgent(
    name="Get Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at retrieving information from linear. Your task is to help a user retrieve information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[openai.pydantic_function_tool(LinearGetIssuesRequest)],
)

##############################################


class LinearUpdateRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> AgentResponse:
        print("CHAT HISTORY")
        print(chat_history)
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "LinearUpdateRequestAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        linear_client = LinearClient(
            access_token=access_token,
        )
        match function_name:
            case LinearUpdateIssuesRequest.__name__:
                updated_issues: list[LinearIssue] = linear_client.update_issues(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not updated_issues:
                    return AgentResponse(
                        agent=SUMMARY_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="No Linear issues were updated. Please check the message history and advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content=f"Here are the updated Linear issues",
                        data=[issue.model_dump() for issue in updated_issues],
                    ),
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


# TODO: Add AND/OR logic to the input model
LINEAR_UPDATE_REQUEST_AGENT = LinearUpdateRequestAgent(
    name="Update Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at updating information in linear. Your task is to help a user update information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible. Look through the chat history carefully to find the correct id.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.     
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[openai.pydantic_function_tool(LinearUpdateIssuesRequest)],
)

##############################################


class LinearDeleteRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "LinearDeleteRequestAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        linear_client = LinearClient(
            access_token=access_token,
        )
        match function_name:
            case LinearDeleteIssuesRequest.__name__:
                deleted_issues: list[LinearIssue] = linear_client.delete_issues(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments
                )
                if not deleted_issues:
                    return AgentResponse(
                        agent=SUMMARY_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="No Linear issues were deleted. Please check the message history and advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                            error=True,
                        ),
                    )
                return AgentResponse(
                    agent=MAIN_TRIAGE_AGENT,
                    message=Message(
                        role=Role.ASSISTANT,
                        content="Here are the deleted Linear issues",
                        data=[issue.model_dump() for issue in deleted_issues],
                    ),
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


LINEAR_DELETE_REQUEST_AGENT = LinearDeleteRequestAgent(
    name="Delete Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at deleting information in linear. Your task is to help a user delete information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[openai.pydantic_function_tool(LinearDeleteIssuesRequest)],
)
##############################################


def transfer_to_linear_get_request_agent() -> LinearGetRequestAgent:
    return LINEAR_GET_REQUEST_AGENT


def transfer_to_linear_post_request_agent() -> LinearPostRequestAgent:
    return LINEAR_POST_REQUEST_AGENT


def transfer_to_linear_update_request_agent() -> LinearUpdateRequestAgent:
    return LINEAR_UPDATE_REQUEST_AGENT


def transfer_to_linear_delete_request_agent() -> LinearDeleteRequestAgent:
    return LINEAR_DELETE_REQUEST_AGENT


LINEAR_TRIAGE_AGENT = TriageAgent(
    name="Triage Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Follow these guidelines:
    
1. None of the tools in this agent require any arguments.
2. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
3. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.""",
    tools=[
        transfer_to_linear_post_request_agent,
        transfer_to_linear_get_request_agent,
        transfer_to_linear_update_request_agent,
        transfer_to_linear_delete_request_agent,
        transfer_to_summary_agent,
    ],
)
