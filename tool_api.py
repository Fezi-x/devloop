from issues import create_issue, edit_issue, list_issues


def devloop_create_issue(repo: str, title: str, body: str = None):
    return create_issue(repo, title, body=body)


def devloop_edit_issue(repo: str, number: int, title: str = None, body: str = None, state: str = None):
    return edit_issue(repo, number, title=title, body=body, state=state)


def devloop_list_issues(repo: str):
    return list_issues(repo)
