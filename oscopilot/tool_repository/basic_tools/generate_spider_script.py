

def generate_spider_javascript(task_description):
    """
    Generate Spider JavaScript code based on the given task description using a language model.

    Args:
    task_description (str): A description of the web scraping or crawling task.

    Returns:
    str: The generated JavaScript code as a string.
    """
    from oscopilot.utils.llms import OpenAI
    from oscopilot.prompts.tool_pt import prompt

    sys_prompt = prompt["generate_spider_javascript"]
    sys_prompt = sys_prompt.format(task_description=task_description)

    llm = OpenAI()
    message = [
        {
            "role": "system",
            "content": sys_prompt,
        },
    ]

    response = llm.chat(message)
    response = prompt["code_prefix"] + response
    return response
