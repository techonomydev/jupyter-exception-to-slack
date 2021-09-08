import re
import sys
from typing import Optional

import requests
from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult, traceback
from IPython.core.ultratb import AutoFormattedTB


def register_to_slack_exception_handler(
    slack_webhook_url: str,
    slack_message_title: str,
    notebook_url: Optional[str] = None,
) -> None:
    exception_handler = ToSlackExceptionHandler(
        slack_webhook_url=slack_webhook_url,
        slack_message_title=slack_message_title,
        notebook_url=notebook_url,
    )

    def handle_post_run_cell(result: ExecutionResult) -> None:
        error_in_exec = result.error_in_exec

        if error_in_exec:
            etype, value, tb = sys.exc_info()
            exception_handler(exception=error_in_exec, tb=tb)

    get_ipython().events.register("post_run_cell", handle_post_run_cell)


class ToSlackExceptionHandler:
    def __init__(
        self,
        slack_webhook_url: str,
        slack_message_title: str,
        notebook_url: Optional[str],
    ) -> None:
        super().__init__()
        self.notebook_url = notebook_url
        self.slack_webhook_url = slack_webhook_url
        self.slack_message_title = slack_message_title

    def __call__(
        self,
        exception: BaseException,
        tb: traceback,
    ) -> None:
        slack_formatter = AutoFormattedTB(
            mode="Verbose",
            color_scheme="NoColor",
        )

        stb = slack_formatter.structured_traceback(type(exception), exception, tb)

        text = slack_formatter.stb2text(stb)

        result = requests.post(
            url=self.slack_webhook_url,
            json={
                "attachments": [
                    {
                        "color": "#f2c744",
                        "blocks": [
                            {
                                "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": self.slack_message_title,
                                },
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"```{re.sub('^[-]*', '', text)}```",
                                },
                            },
                            *(
                                [
                                    {
                                        "type": "section",
                                        "text": {"type": "mrkdwn", "text": "👉"},
                                        "accessory": {
                                            "type": "button",
                                            "text": {
                                                "type": "plain_text",
                                                "text": "Go to notebook",
                                            },
                                            "url": self.notebook_url,
                                        },
                                    }
                                ]
                                if self.notebook_url
                                else []
                            ),
                        ],
                    }
                ]
            },
        )
        result.raise_for_status()
