from __future__ import annotations

from typing import Any

from github.GithubObject import Attribute, NotSet
from github.PaginatedList import PaginatedList

# https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28#media-types
mediaType = "application/vnd.github+json"

from github.Issue import Issue


class SubIssue(Issue):
    """
    This class represents a Sub-issue in GitHub's REST API. Sub-issues are issues that are linked to a parent issue.

    See https://docs.github.com/en/rest/issues/sub-issues for more details.

    """

    def _initAttributes(self) -> None:
        super()._initAttributes()
        # Sub-issue specific attributes
        self._parent_issue: Attribute[Issue] = NotSet
        self._priority_position: Attribute[int] = NotSet

    def __repr__(self) -> str:
        return self.get__repr__(
            {"number": self._number.value, "title": self._title.value}
        )

    @property
    def parent_issue(self) -> Issue:
        """
        :type: :class:`github.Issue.Issue`
        """
        self._completeIfNotSet(self._parent_issue)
        return self._parent_issue.value

    @property
    def priority_position(self) -> int:
        """
        :type: int
        """
        self._completeIfNotSet(self._priority_position)
        return self._priority_position.value

    def get_parent_issue(self) -> Issue:
        """
        :calls: `GET /repos/{owner}/{repo}/issues/{number}` :rtype: :class:`github.Issue.Issue`
        """
        # TODO: Need to implement this
        ...

    def _useAttributes(self, attributes: dict[str, Any]) -> None:
        super()._useAttributes(attributes)
        # Process sub-issue specific attributes
        if "parent_issue" in attributes:
            self._parent_issue = self._makeClassAttribute(
                Issue, attributes["parent_issue"]
            )
        if "priority_position" in attributes:
            self._priority_position = self._makeIntAttribute(
                attributes["priority_position"]
            )


class MyIssue:
    def __init__(self, issue: Issue):
        self.issue = issue

    def get_sub_issues(self) -> PaginatedList[SubIssue]:
        """
        :calls: `GET /repos/{owner}/{repo}/issues/{number}/sub_issues <https://docs.github.com/en/rest/issues/sub-issues?apiVersion=2022-11-28>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Issue.Issue`
        """
        return PaginatedList(
            SubIssue,
            self.issue._requester,
            f"{self.issue.url}/sub_issues",
            None,
            headers={"Accept": mediaType},
        )

    def add_sub_issue(self, sub_issue_id: int) -> SubIssue:
        """
        :calls: `POST /repos/{owner}/{repo}/issues/{number}/sub_issues <https://docs.github.com/en/rest/issues/sub-issues>`_
        :param sub_issue_id: int
        :rtype: :class:`github.Issue.SubIssue`
        """
        assert isinstance(self.issue.number, int), self.issue.number
        post_parameters: dict[str, Any] = {
            "sub_issue_id": sub_issue_id,
        }
        print(self.issue.url)
        headers, data = self.issue._requester.requestJsonAndCheck(
            "POST",
            f"{self.issue.url}/sub_issues",
            input=post_parameters,
            headers={"Accept": mediaType},
        )
        return SubIssue(self.issue._requester, headers, data, completed=True)

    def remove_sub_issue(self, sub_issue_id: int) -> SubIssue:
        """
        :calls: `DELETE /repos/{owner}/{repo}/issues/{number}/sub_issue <https://docs.github.com/en/rest/issues/sub-issues>`_
        :param sub_issue_id: int
        :rtype: :class:`github.Issue.SubIssue`
        """
        assert isinstance(sub_issue_id, int), sub_issue_id
        post_parameters: dict[str, Any] = {
            "sub_issue_id": sub_issue_id,
        }
        headers, data = self.issue._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.url}/sub_issue",
            input=post_parameters,
            headers={"Accept": mediaType},
        )
        return SubIssue(self.issue._requester, headers, data, completed=True)

    def reprioritize_sub_issue(self, sub_issue_id: int, after_id: int) -> SubIssue:
        """
        :calls: `PATCH /repos/{owner}/{repo}/issues/{number}/sub_issues/priority <https://docs.github.com/en/rest/issues/sub-issues>`_
        :param sub_issue_id: int
        :param after_id: int
        :rtype: :class:`github.Issue.SubIssue`
        """
        assert isinstance(sub_issue_id, int), sub_issue_id
        assert isinstance(after_id, int), after_id
        patch_parameters = {"sub_issue_id": sub_issue_id, "after_id": after_id}
        headers, data = self.issue._requester.requestJsonAndCheck(
            "PATCH",
            f"{self.url}/sub_issues/priority",
            input=patch_parameters,
            headers={"Accept": mediaType},
        )
        return SubIssue(self.issue._requester, headers, data, completed=True)
