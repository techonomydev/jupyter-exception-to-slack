# jupyter-exception-to-slack
Contains a handler that automatically sends Jupyter exceptions to slack regardless of the cell in which the issue occurs.

Install with:
`python -m pip install git+https://github.com/techonomydev/jupyter-exception-to-slack`

You can Register the handler with the following code:

```python
from jupyter_exception_to_slack import register_to_slack_exception_handler

register_to_slack_exception_handler(
    slack_webhook_url="<Your slack webhook url>",
    slack_message_title="<Any title you want>",
    notebook_url="<Optional; used for a go-to-notebook button in the message>"
)
```
