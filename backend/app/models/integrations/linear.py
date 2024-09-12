from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class Status(StrEnum):
    BACKLOG = "Backlog"
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"
    CANCELED = "Canceled"
    DUPLICATE = "Duplicate"


class State(BaseModel):
    name: Status


class Label(BaseModel):
    name: str


class Labels(BaseModel):
    nodes: list[Label]


class User(BaseModel):
    name: str


class Comment(BaseModel):
    message: str
    user: str


class Cycle(BaseModel):
    number: int


class Project(BaseModel):
    name: str


class LinearIssue(BaseModel):
    id: Optional[str]
    number: Optional[int]
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    estimate: Optional[
        int
    ]  # Assume T-Shirt sizes for now, which is represented as an integer in the API
    state: Optional[Status]
    assignee: Optional[str]
    creator: Optional[str]
    labels: Optional[list[str]]
    createdAt: Optional[str]  # Timezone but in string format
    updatedAt: Optional[str]  # Timezone but in string format
    dueDate: Optional[str]  # YYYY-MM-DD but in string format
    cycle: Optional[int]
    project: Optional[str]
    comments: Optional[list[Comment]]
    url: Optional[str]


class LinearFilterIssuesRequest(BaseModel):
    use_and_clause: bool = Field(
        description="True if all conditions should be met, False if any condition should be met"
    )
    id: Optional[list[str]]
    title: Optional[list[str]]
    number: Optional[list[int]]
    state: Optional[list[Status]]
    assignee: Optional[list[str]]
    creator: Optional[list[str]]
    project: Optional[list[str]]
    cycle: Optional[list[int]]
    labels: Optional[list[str]]
    estimate: Optional[list[int]]

    @model_validator(mode="after")
    def list_length_match_use_and_clause(self):
        """
        Validate that the length of the other attributes are consistent in the event use_and_clause is True
        """
        if self.use_and_clause == False:
            return self
        if self.id and len(self.id) > 1:
            raise ValueError("id must have a length of 1 when use_and_clause is True")
        if self.title and len(self.title) > 1:
            raise ValueError(
                "title must have a length of 1 when use_and_clause is True"
            )
        if self.number and len(self.number) > 1:
            raise ValueError(
                "number must have a length of 1 when use_and_clause is True"
            )
        if self.state and len(self.state) > 1:
            raise ValueError(
                "state must have a length of 1 when use_and_clause is True"
            )
        if self.assignee and len(self.assignee) > 1:
            raise ValueError(
                "assignee must have a length of 1 when use_and_clause is True"
            )
        if self.creator and len(self.creator) > 1:
            raise ValueError(
                "creator must have a length of 1 when use_and_clause is True"
            )
        if self.project and len(self.project) > 1:
            raise ValueError(
                "project must have a length of 1 when use_and_clause is True"
            )
        if self.estimate and len(self.estimate) > 1:
            raise ValueError(
                "estimate must have a length of 1 when use_and_clause is True"
            )

        # labels can still be a list
        return self


class LinearGetIssuesRequest(LinearFilterIssuesRequest):
    pass


class LinearDeleteIssuesRequest(LinearFilterIssuesRequest):
    pass


class LinearCreateIssueRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    estimate: Optional[int]
    state: Optional[Status]
    assignee: Optional[str]
    creator: Optional[str]
    labels: Optional[Labels]
    dueDate: Optional[str]
    cycle: Optional[int]
    project: Optional[str]


class LinearUpdateIssuesRequest(BaseModel):
    filter_conditions: LinearFilterIssuesRequest
    update_conditions: LinearCreateIssueRequest
