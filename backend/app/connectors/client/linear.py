import json
import logging

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from app.models.integrations.linear import (
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearGetIssuesRequest,
    LinearIssue,
    LinearUpdateIssuesRequest,
)

logging.getLogger("gql").setLevel(logging.WARNING)
logging.getLogger("gql.transport.requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

LINEAR_API_URL = "https://api.linear.app/graphql"


class LinearClient:
    def __init__(self, access_token: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        transport = RequestsHTTPTransport(
            url=LINEAR_API_URL,
            headers=headers,
            use_json=True,
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def query_grapql(self, query):
        r = requests.post(
            self.graphql_url,
            json={"query": query},
            headers={
                "Authorization": self.api_key
                # "Authorization" : self.access_token
            },
        )

        response = json.loads(r.content)

        if "errors" in response:
            raise Exception(response["errors"])

        return response

    def query_basic_resource(self, resource=""):
        resource_response = self.query_grapql(
            """
                query Resource {"""
            + resource
            + """{nodes{id,name}}}
            """
        )

        return resource_response["data"][resource]["nodes"]

    def teams(self):
        return self.query_basic_resource("teams")

    def states(self):
        return self.query_basic_resource("workflowStates")

    def projects(self):
        return self.query_basic_resource("projects")

    def create_issue(self, request: LinearCreateIssueRequest) -> LinearIssue:
        MUTATION_NAME = "issueCreate"

        mutation = gql(
            f"""
            mutation CreateIssue($input: IssueCreateInput!) {{
                {MUTATION_NAME}(input: $input) {{
                    success
                    issue {{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            }}
            """
        )

        variables = {
            "input": {
                "title": request.title,
                "description": request.description,
                "stateId": (
                    self.get_state_id_by_name(name=request.state.value)
                    if request.state
                    else None
                ),
                "priority": request.priority,
                "assigneeId": (
                    self.get_id_by_name(name=request.assignee, target="users")
                    if request.assignee
                    else None
                ),
                "estimate": request.estimate,
                "cycleId": (
                    self.get_id_by_number(number=request.cycle, target="cycles")
                    if request.cycle
                    else None
                ),
                "labels": request.labels.nodes if request.labels else None,
                "projectId": (
                    self.get_id_by_name(name=request.project, target="projects")
                    if request.project
                    else None
                ),
                "teamId": (
                    self.get_id_by_name(name="Linear-whale", target="teams")
                    if request.assignee
                    else None
                ),
            }
        }

        variables["input"] = {
            k: v for k, v in variables["input"].items() if v is not None
        }

        result = self.client.execute(mutation, variable_values=variables)
        return LinearIssue.model_validate(
            _flatten_linear_response_issue(result[MUTATION_NAME]["issue"])
        )

    def get_issues(self, request: LinearGetIssuesRequest) -> list[LinearIssue]:
        match request.use_and_clause:
            case True:
                return self._get_issues_with_and_clause(request=request)
            case False:
                return self._get_issues_with_or_clause(request=request)
            case _:
                raise ValueError(
                    "use_and_clause of LinearGetIssuesRequest must be a boolean"
                )

    def _get_issues_with_or_clause(
        self, request: LinearGetIssuesRequest
    ) -> list[LinearIssue]:
        variables = {}
        validated_results: list[LinearIssue] = []
        QUERY_OBJ_GROUP: str = "issues"
        QUERY_OBJ_LIST: str = "nodes"
        query = gql(
            f"""
            query GetIssues($filter: IssueFilter) {{
                {QUERY_OBJ_GROUP}(filter: $filter) {{
                    {QUERY_OBJ_LIST}{{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            }}
        """
        )
        variables["filter"] = {"or": []}
        if request.id:
            variables["filter"]["or"].extend(
                [{"id": {"eq": _id}} for _id in request.id]
            )
        if request.state:
            variables["filter"]["or"].extend(
                [{"state": {"name": {"eq": _state}}} for _state in request.state]
            )
        if request.number:
            variables["filter"]["or"].extend(
                [{"number": {"eq": _number}} for _number in request.number]
            )
        if request.title:
            variables["filter"]["or"].extend(
                [{"title": {"contains": _title}} for _title in request.title]
            )
        if request.assignee:
            variables["filter"]["or"].extend(
                [
                    {"assignee": {"name": {"eq": _assignee}}}
                    for _assignee in request.assignee
                ]
            )
        if request.creator:
            variables["filter"]["or"].extend(
                [
                    {"creator": {"name": {"eq": _creator}}}
                    for _creator in request.creator
                ]
            )
        if request.project:
            variables["filter"]["or"].extend(
                [
                    {"project": {"name": {"eq": _project}}}
                    for _project in request.project
                ]
            )
        if request.cycle:
            variables["filter"]["or"].extend(
                [{"cycle": {"number": {"eq": _cycle}}} for _cycle in request.cycle]
            )
        if request.labels:
            variables["filter"]["or"].extend(
                [
                    {"labels": {"some": {"name": {"in": _labels}}}}
                    for _labels in request.labels
                ]
            )
        if request.estimate:
            variables["filter"]["or"].extend(
                [{"estimate": {"eq": _estimate}} for _estimate in request.estimate]
            )
        result = self.client.execute(query, variable_values=variables)

        for issue in result[QUERY_OBJ_GROUP][QUERY_OBJ_LIST]:
            validated_results.append(_flatten_linear_response_issue(issue))
        return validated_results

    def _get_issues_with_and_clause(
        self, request: LinearGetIssuesRequest
    ) -> list[LinearIssue]:
        variables = {}
        validated_results: list[LinearIssue] = []

        if request.id:
            QUERY_OBJ_NAME: str = "issue"
            query = gql(
                f"""
                query GetIssue($id: String!) {{
                    {QUERY_OBJ_NAME}(id: $id) {{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            """
            )
            variables["id"] = request.id[0]
            result = self.client.execute(query, variable_values=variables)
            validated_results.append(
                _flatten_linear_response_issue(result[QUERY_OBJ_NAME])
            )
        else:
            QUERY_OBJ_GROUP: str = "issues"
            QUERY_OBJ_LIST: str = "nodes"
            query = gql(
                f"""
                query GetIssues($filter: IssueFilter) {{
                    {QUERY_OBJ_GROUP}(filter: $filter) {{
                        {QUERY_OBJ_LIST}{{
                            id
                            number
                            title
                            description
                            priority
                            estimate
                            state {{ name }}
                            assignee {{ name }}
                            creator {{ name }}
                            labels {{ nodes {{ name }} }}
                            createdAt
                            updatedAt
                            dueDate
                            cycle {{ number }}
                            project {{ name }}
                            comments {{ nodes {{ body user {{ name }} }} }}
                            url
                        }}
                    }}
                }}
            """
            )
            variables["filter"] = {"and": []}
            if request.state:
                variables["filter"]["and"].append(
                    {"state": {"name": {"eq": request.state[0]}}}
                )
            if request.number:
                variables["filter"]["and"].append({"number": {"eq": request.number[0]}})
            if request.title:
                variables["filter"]["and"].append(
                    {"title": {"contains": request.title[0]}}
                )
            if request.assignee:
                variables["filter"]["and"].append(
                    {"assignee": {"name": {"eq": request.assignee[0]}}}
                )
            if request.creator:
                variables["filter"]["and"].append(
                    {"creator": {"name": {"eq": request.creator[0]}}}
                )
            if request.project:
                variables["filter"]["and"].append(
                    {"project": {"name": {"eq": request.project[0]}}}
                )
            if request.cycle:
                variables["filter"]["and"].append(
                    {"cycle": {"number": {"eq": request.cycle[0]}}}
                )
            if request.labels:
                variables["filter"]["and"].append(
                    {"labels": {"some": {"name": {"in": request.labels}}}}
                )
            if request.estimate:
                variables["filter"]["and"].append(
                    {"estimate": {"eq": request.estimate[0]}}
                )
            result = self.client.execute(query, variable_values=variables)
            for issue in result[QUERY_OBJ_GROUP][QUERY_OBJ_LIST]:
                validated_results.append(_flatten_linear_response_issue(issue))

        return validated_results

    def update_issues(self, request: LinearUpdateIssuesRequest) -> list[LinearIssue]:
        variables = {}
        validated_results: list[LinearIssue] = []

        # First, get the issues based on filter_conditions
        filter_conditions = request.filter_conditions
        issues_to_update = self.get_issues(filter_conditions)

        # Prepare the update mutation
        MUTATION_NAME: str = "issueUpdate"
        mutation = gql(
            f"""
            mutation UpdateIssue($id: String!, $update: IssueUpdateInput!) {{
                {MUTATION_NAME}(id: $id, input: $update) {{
                    success
                    issue {{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            }}
            """
        )

        # Iterate over each issue and apply the updates
        for issue in issues_to_update:
            variables["id"] = issue.id
            variables["update"] = {}

            update_conditions = request.update_conditions

            if update_conditions.state:
                variables["update"]["stateId"] = self.get_state_id_by_name(
                    update_conditions.state.value
                )
            if update_conditions.assignee:
                variables["update"]["assigneeId"] = self.get_id_by_name(
                    update_conditions.assignee, "users"
                )
            if update_conditions.project:
                variables["update"]["projectId"] = self.get_id_by_name(
                    update_conditions.project, "projects"
                )
            if update_conditions.cycle:
                variables["update"]["cycleId"] = self.get_id_by_number(
                    update_conditions.cycle, "cycles"
                )
            if update_conditions.labels:
                label_names = [label.name for label in update_conditions.labels.nodes]
                variables["update"]["labelIds"] = [
                    self.get_label_id_by_name(label) for label in label_names
                ]
            if update_conditions.estimate:
                variables["update"]["estimate"] = update_conditions.estimate

            result = self.client.execute(mutation, variable_values=variables)

            validated_results.append(
                _flatten_linear_response_issue(result[MUTATION_NAME]["issue"])
            )

        return validated_results

    def delete_issues(self, request: LinearDeleteIssuesRequest) -> list[LinearIssue]:
        variables = {}
        issues_to_delete = self.get_issues(request=request)

        MUTATION_NAME: str = "issueDelete"
        mutation = gql(
            f"""
            mutation DeleteIssue($id: String!) {{
                {MUTATION_NAME}(id: $id) {{
                    success
                }}
            }}
            """
        )

        for issue in issues_to_delete:
            variables["id"] = issue.id
            self.client.execute(mutation, variable_values=variables)

        return issues_to_delete

    ###
    ### Helper
    ###
    def get_id_by_name(self, name: str, target: str) -> str:
        query = gql(
            f"""
            query GetIdByName($name: String!) {{
                {target}(filter: {{ name: {{ eq: $name }} }}) {{
                    nodes {{
                        id
                    }}
                }}
            }}
            """
        )

        variables = {"name": name}

        result = self.client.execute(query, variable_values=variables)
        users = result.get(target, {}).get("nodes", [])

        if users:
            return users[0]["id"]
        else:
            raise ValueError(f"{target} with name '{name}' not found.")

    def get_id_by_number(self, number: int, target: str) -> str:
        query = gql(
            f"""
            query GetIdByNumber($number: Float!) {{
                {target}(filter: {{ number: {{ eq: $number }} }}) {{
                    nodes {{
                        id
                    }}
                }}
            }}
            """
        )

        variables = {"number": number}

        result = self.client.execute(query, variable_values=variables)
        cycles = result.get(target, {}).get("nodes", [])

        if cycles:
            return cycles[0]["id"]
        else:
            raise ValueError(f"Cycle with number '{number}' not found.")

    def get_state_id_by_name(self, name: str) -> str:
        query = gql(
            """
            query GetStateIdByName {
                workflowStates {
                    nodes {
                        id
                        name
                    }
                }
            }
            """
        )

        result = self.client.execute(query)
        states = result.get("workflowStates", {}).get("nodes", [])

        # Filter the states by name in the application code
        for state in states:
            if state["name"] == name:
                return state["id"]

        raise ValueError(f"State with name '{name}' not found.")

    def get_label_id_by_name(self, name: str) -> str:
        query = gql(
            """
            query GetLabelIdByName {
                issueLabels {
                    nodes {
                        id
                        name
                    }
                }
            }
            """
        )

        result = self.client.execute(query)
        labels = result.get("issueLabels", {}).get("nodes", [])

        # Filter the labels by name in the application code
        for label in labels:
            if label["name"] == name:
                return label["id"]

        raise ValueError(f"Label with name '{name}' not found.")


def _flatten_linear_response_issue(issue: dict) -> LinearIssue:
    if "labels" in issue and "nodes" in issue["labels"]:
        issue["labels"] = [label["name"] for label in issue["labels"]["nodes"]]
    if "comments" in issue and "nodes" in issue["comments"]:
        issue["comments"] = [
            {"message": comment["body"], "user": comment["user"]["name"]}
            for comment in issue["comments"]["nodes"]
        ]
    if "project" in issue and issue["project"]:
        issue["project"] = issue["project"]["name"]
    if "cycle" in issue and issue["cycle"]:
        issue["cycle"] = issue["cycle"]["number"]
    if "state" in issue and issue["state"]:
        issue["state"] = issue["state"]["name"]
    if "assignee" in issue and issue["assignee"]:
        issue["assignee"] = issue["assignee"]["name"]
    if "creator" in issue and issue["creator"]:
        issue["creator"] = issue["creator"]["name"]

    return LinearIssue.model_validate(issue)
