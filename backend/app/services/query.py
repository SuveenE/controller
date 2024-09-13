import asyncio
import logging
from typing import Optional

from pydantic import BaseModel

from app.connectors.native.stores.token import Token
from app.exceptions.exception import DatabaseError
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.gmail import GMAIL_TRIAGE_AGENT
from app.models.agents.linear import LINEAR_TRIAGE_AGENT
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.query import Message, QueryResponse, Role
from app.services.message import MessageService
from app.services.token import TokenService
from app.services.user import UserService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class QueryService:

    async def query(
        self,
        message: Message,
        chat_history: list[Message],
        api_key: str,
        integrations: list[Integration],
        instance: Optional[str],
    ) -> QueryResponse:
        tokens: dict[str, Token] = {}
        for integration in integrations:
            token: Optional[Token] = await TokenService().get(
                api_key=api_key, table_name=integration
            )
            if not token:
                raise DatabaseError(
                    f"User has not authenticated with the {integration} table. Please authenticate before trying again."
                )
            tokens[integration] = token
        chat_history.append(message)
        agent_chat_history: list[Message] = []
        for msg in chat_history:
            agent_chat_history.append(
                Message(
                    role=Role.ASSISTANT,
                    content=f"{msg.content}: {str(msg.data)}",
                    data=None,
                )
            )
        response = AgentResponse(agent=MAIN_TRIAGE_AGENT, message=message)
        while response.agent:
            prev_agent: Agent = response.agent
            integration_group: Integration = response.agent.integration_group
            if integration_group == Integration.NONE:
                response = response.agent.query(
                    chat_history=agent_chat_history,
                    access_token="",
                    refresh_token="",
                    client_id="",
                    client_secret="",
                )
            else:
                response = response.agent.query(
                    chat_history=agent_chat_history,
                    access_token=tokens[integration_group].access_token,
                    refresh_token=tokens[integration_group].refresh_token,
                    client_id=tokens[integration_group].client_id,
                    client_secret=tokens[integration_group].client_secret,
                )
            if isinstance(prev_agent, TriageAgent):
                continue
            chat_history.append(
                Message(
                    role=Role.ASSISTANT,
                    content=response.message.content,
                    data=response.message.data,
                    error=response.message.error,
                )
            )
            # Agent seems to just ignore the data field and only bases its judgement on the content field
            agent_chat_history.append(
                Message(
                    role=Role.ASSISTANT,
                    content=f"{response.message.content}: {str(response.message.data)}",
                    data=None,
                    error=response.message.error,
                )
            )
        results = await asyncio.gather(
            UserService().increment_usage(api_key=api_key),
            MessageService().post(
                chat_history=chat_history,
                api_key=api_key,
                integrations=integrations,
                instance=instance,
            ),
        )

        return QueryResponse(
            chat_history=[msg for msg in chat_history if not msg.error],
            instance=results[1],
        )

    async def query_linear(
        self, chat_history: list[Message], api_key: str
    ) -> list[BaseModel]:
        TABLE_NAME = "linear"
        token: Optional[Token] = await TokenService().get(
            api_key=api_key, table_name=TABLE_NAME
        )
        if not token:
            raise DatabaseError(
                f"User has not authenticated with the {TABLE_NAME} table. Please authenticate before trying again."
            )

        curr_agent: Agent = LINEAR_TRIAGE_AGENT.query(
            chat_history=chat_history,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
        )
        response: list[BaseModel] = curr_agent.query(
            chat_history=chat_history,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
        )
        return response

    async def query_gmail(
        self, chat_history: list[Message], api_key: str
    ) -> list[BaseModel]:
        TABLE_NAME = "gmail"
        token: Optional[Token] = await TokenService().get(
            api_key=api_key, table_name=TABLE_NAME
        )
        if not token:
            raise DatabaseError(
                f"User has not authenticated with the {TABLE_NAME} table. Please authenticate before trying again."
            )

        curr_agent: Agent = GMAIL_TRIAGE_AGENT.query(
            messages=chat_history,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            client_id=token.client_id,
            client_secret=token.client_secret,
        )
        response: list[BaseModel] = curr_agent.query(
            chat_history=chat_history,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            client_id=token.client_id,
            client_secret=token.client_secret,
        )
        return response
