def generate_javascript(task_description):
    """
    Generate JavaScript code based on the given task description using a language model.

    Args:
    task_description (str): A description of the task for which JavaScript code needs to be generated.

    Returns:
    str: The generated JavaScript code as a string.
    """
    from oscopilot.utils.llms import OpenAI
    from oscopilot.prompts.tool_pt import prompt

    sys_prompt = prompt["generate_javascript"]
    sys_prompt = sys_prompt.format(task_description=task_description)

    llm = OpenAI()
    message = [
        {
            "role": "system",
            "content": sys_prompt,
        },
    ]

    response = llm.chat(message)
    return response


# print(
#     generate_javascript(
#         # "delete all occurrence of MapReduce in a html."
#         # "hightlight all occurence of 'MapReduce' in a html."
#         # "change web backgound color to green."
#         "change web font family to 'Arial'."
#     )
# )
