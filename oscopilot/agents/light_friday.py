from oscopilot.utils import setup_config, setup_pre_run
from oscopilot.modules.base_module import BaseModule
from oscopilot.utils import setup_config
import re
from rich.console import Console
from rich.markdown import Markdown
import sys
import os
import dotenv

project_root="/home/evi0ned/NLP/OS-Copilot"
os.chdir(project_root)
sys.path.append(project_root)

console = Console()

def rich_print(markdown_text):
    try:
        md = Markdown(markdown_text)
        console.print(md)
    except:
        print(markdown_text)
    
def send_chat_prompts(message, llm):
    return llm.chat(message)

def extract_code(text):
    pattern = r"```(\w+)?\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        language, code = matches[0]

        if not language:
            if re.search("python", code.lower()) or re.search(r"import\s+\w+", code):
                language = "Python"
            elif re.search("bash", code.lower()) or re.search(r"echo", code):
                language = "Bash"

        return code.strip(), language
    else:
        return None, None

class LightFriday(BaseModule):
    def __init__(self, args):
        super().__init__()
        self.args = args
    def execute_tool(self, code, lang):
        state = self.environment.step(lang, code)
        return_info = ''
        if state.result != None and state.result.strip() != '':
            return_info = '**Execution Result** :' + state.result.strip()
        if state.error != None and state.error.strip() != '':
            return_info = '\n**Execution Error** :' + state.error.strip()
        return return_info.strip()

    def run(self, task):
        light_planner_sys_prompt = '''You are Light Friday, a world-class programmer that can complete any goal by executing code...
    '''
        light_planner_user_prompt = '''
        User's information are as follows:
        System Version: {system_version}
        Task: {task}
        Current Working Directiory: {working_dir}'''.format(system_version=self.system_version, task=task, working_dir=self.environment.working_dir)
        message = [
        {"role": "system", "content": light_planner_sys_prompt},
        {"role": "user", "content": light_planner_user_prompt},
    ]

        while True:
            response = send_chat_prompts(message, self.llm)
            rich_print(response)
            message.append({"role": "system", "content": response})

            code, lang = extract_code(response)
            if code:
                result = self.execute_tool(code, lang)
                rich_print(result)
            else:
                result = ''

            if result != '':
                light_exec_user_prompt = 'The result after executing the code: {result}'.format(result=result)
                message.append({"role": "user", "content": light_exec_user_prompt})
            else:
                message.append({"role": "user", "content": "Please continue. If all tasks have been completed, reply with 'Execution Complete'. If you believe subsequent tasks cannot continue, reply with 'Execution Interrupted', including the reasons why the tasks cannot proceed, and provide the user with some possible solutions."})

            if 'Execution Complete' in response or 'Execution Interrupted' in response or 'script successfully' in response:
                break
                

        