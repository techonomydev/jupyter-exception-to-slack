import re
from typing import List, Optional, Type

import requests
from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell, traceback
from IPython.core.ultratb import AutoFormattedTB
from IPython.display import display


def register_to_slack_exception_handler(
    slack_webhook_url: str,
    slack_message_title: str,
    notebook_url: Optional[str],
) -> None:
    get_ipython().set_custom_exc(
        (BaseException,),
        ToSlackExceptionHandler(slack_webhook_url, slack_message_title, notebook_url),
    )


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
        shell: InteractiveShell,
        etype: Type[BaseException],
        value: BaseException,
        tb: traceback,
        tb_offset: Optional[int] = None,
    ) -> Optional[List[str]]:
        notebook_formatter = AutoFormattedTB(tb_offset=tb_offset)
        slack_formatter = AutoFormattedTB(
            mode="Verbose", color_scheme="NoColor", tb_offset=tb_offset
        )

        stb = slack_formatter.structured_traceback(etype, value, tb)

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

        display(notebook_formatter(etype, value, tb))

        return notebook_formatter.structured_traceback(etype, value, tb)
