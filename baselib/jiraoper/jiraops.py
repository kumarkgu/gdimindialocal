from jira import JIRA
from jira import JIRAError
from baselib.utils.Logger import Logger
import baselib.utils.base_util as bu


class JiraBase:
    _ISSUE_KEY = {
        "IssueKey": {
            "Attribute": "key",
            "Type": "Scalar"
        },
        "Summary": {
            "Attribute": "fields.summary",
            "Type": "Scalar"
        },
        "IssueType": {
            "Attribute": "fields.issuetype.name",
            "Type": "Scalar"
        },
        "IssueStatus": {
            "Attribute": "fields.status",
            "Type": "Scalar"
        },
        "IssueAssignee": {
            "Attribute": "fields.assignee",
            "Type": "Scalar"
        },
        "IssueCreated": {
            "Attribute": "fields.created",
            "Type": "Scalar"
        },
        "IssueUpdated": {
            "Attribute": "fields.updated",
            "Type": "Scalar"
        },
        "Worklog": {
            "Attribute": "fields.worklog.worklogs",
            "Type": "List",
            "Subattribute": {
                "Id": {
                    "Attribute": "id",
                    "Type": "Scalar"
                },
                "Name": {
                    "Attribute": "author.name",
                    "Type": "Scalar"
                },
                "CreateTime": {
                    "Attribute": "created",
                    "Type": "Scalar"
                },
                "TimeSpent": {
                    "Attribute": "timeSpent",
                    "Type": "Scalar"
                },
                "TimeSpentSecond": {
                    "Attribute": "timeSpentSeconds",
                    "Type": "Scalar"
                },
                "UpdateTime": {
                    "Attribute": "updated",
                    "Type": "Scalar"
                }
            }
        }
    }

    def __init__(self, jirapath, username=None, passwd=None, log=None):
        self.jirapath = jirapath
        self.username = username if username else None
        self.passwd = passwd if passwd else None
        self.log = log if log else Logger("JIRA").getlog()
        self.jiraconn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def disconnect(self):
        if self.jiraconn:
            self.jiraconn = None

    def connect(self):
        jiraconnerr = "JIRA Connection Error: {}. Response Code: {}"
        if self.jiraconn is None:
            conn_message = "Connecting to JIRA: {}".format(self.jirapath)
            self.log.info(conn_message)
            try:
                options = {
                    'server': self.jirapath
                }
                if self.username and self.passwd:
                    self.jiraconn = JIRA(self.jirapath,
                                         basic_auth=(
                                             self.username,
                                             self.passwd
                                         ))
                else:
                    self.jiraconn = JIRA(options=options)
            except JIRAError as e:
                self.log.info(jiraconnerr.format(e.text, e.status_code))
        return self.jiraconn

    @staticmethod
    def get_max_issues(jiraconn, query, page_size=10, log=None):
        try:
            issues = jiraconn.search_issues(query, startAt=0,
                                            maxResults=page_size,
                                            json_result=True)
            totalissue = issues["total"]
            return totalissue
        except JIRAError as e:
            message = "Error: {}\nFor query: {}".format(e.text, query)
            if log:
                log.info(message)
            else:
                print(message)
            return -1

    @staticmethod
    def _get_issues(jiraconn, query, startat=0, maxresult=50, log=None,
                    prefix=0):
        message = "{}Getting Issue Details: Starting Index: {}. Max Records: {}"
        pre = bu.repeat_string(".", 2)
        message = message.format(pre, str(startat), str(maxresult))
        if log:
            log.info(message)
        else:
            print(message)
        result = jiraconn.search_issues(query, startAt=startat,
                                        maxResults=maxresult,
                                        json_result=True)
        return result

    def get_all_issues_key(self, query, jiraconn=None):
        self.log.info("Getting All Issue Key")
        oconn = jiraconn if jiraconn else self.connect()
        page_size = 50
        totalissue = self.get_max_issues(oconn, query, log=self.log)
        if totalissue <= 0:
            if self.log:
                self.log.info("ERROR: Exiting")
            else:
                print("ERROR: Exiting")
            return None
        self.log.info("Total Number of Issues: {}".format(str(totalissue)))
        keylists = []
        if totalissue > 0:
            endblock = (totalissue // page_size) + 1
            for counter in range(endblock):
                if counter == 0:
                    startindex = 0
                else:
                    startindex = (counter * page_size) + 1
                json_issues = self._get_issues(oconn, query, startindex,
                                               page_size, self.log)
                for issues in json_issues["issues"]:
                    keylists.append(issues["key"])
        return keylists

    @staticmethod
    def _get_issue_detail(jiraconn, issuekey, log=None, keyval=None):
        message = "{}Getting Issue Detail For: {}".format(
            bu.repeat_string(".", 2),
            issuekey
        )
        if log:
            log.info(message)
        else:
            print(message)
        issuefield = JiraBase._ISSUE_KEY
        if keyval is not None:
            issuefield = {**JiraBase._ISSUE_KEY, **keyval}
        issue = jiraconn.issue(issuekey)
        issuedetail = bu.get_rattr(issue, issuefield)
        return issuedetail

    def get_all_issues(self, query, limit=None):
        oconn = self.connect()
        issuekey = self.get_all_issues_key(query, oconn)
        if issuekey is None:
            return None
        issues = []
        self.log.info("Getting Issue Details")
        if limit is None:
            for keys in issuekey:
                issues.append(self._get_issue_detail(oconn, keys, log=self.log))
        else:
            for keys in issuekey[:limit+1]:
                issues.append(self._get_issue_detail(oconn, keys, log=self.log))
        return issues
