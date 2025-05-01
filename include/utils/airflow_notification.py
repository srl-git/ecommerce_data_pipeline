import os
import asyncio

import telegram


async def send_telegram_msg(text: str) -> None:
    """
    Send message to Telegram chat.

    Args: 
        text (str): The message to be sent.

    Return:
        None
    """
    token = os.getenv('TELEGRAM_TOKEN','')
    chat_id = os.getenv('TELEGRAM_CHAT_ID','')
    bot = telegram.Bot(token)
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id, parse_mode='Markdown')


def notify_task_state(context: dict) -> None:
    """
    Format message for task notifications and send via Telegram.

    Args:
        context (dict): Airflow context passed from DAG run.

    Returns:
        None
    """
    task = context.get('task_instance')

    if task:
        dag_id = task.dag_id
        run_id = task.run_id
        task_id = task.task_id
        task_state = task.state
        msg = (
            f"*Airflow Task Notification*\n\n"
            f"*DAG:* `{dag_id}`\n"
            f"*Run ID:* `{run_id}`\n"
            f"*Task:* `{task_id}`\n"
            f"*Status:* `{task_state}`"
        )
        asyncio.run(send_telegram_msg(msg))