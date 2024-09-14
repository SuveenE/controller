from typing import Optional

from pydantic import BaseModel


class Gmail(BaseModel):
    id: str
    labelIds: list[str]
    sender: str
    subject: str
    body: str


class GmailEditableFields(BaseModel):
    labelIds: Optional[list[str]]


class GmailFilterEmailsRequest(BaseModel):
    query: str


class GmailGetEmailsRequest(GmailFilterEmailsRequest):
    pass


class GmailDeleteEmailsRequest(GmailFilterEmailsRequest):
    pass


class MarkAsReadRequest(GmailFilterEmailsRequest):
    pass
    

class GmailReadEmailsRequest(BaseModel):
    query: str


class GmailSendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
