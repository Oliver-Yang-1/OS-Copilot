import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi import Form

from oscopilot import (
    FridayAgent,
    ToolManager,
    FridayExecutor,
    FridayPlanner,
    FridayRetriever,
)
from oscopilot.utils import setup_config, setup_pre_run
from examples.light_friday.light_friday import LightFriday
from typing import Dict, List, Optional
import io
import sys
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ensure_html_extension(file_location):
    """
    Ensures the given file location ends with '.html'. If not, renames the file by adding '.html'.

    Args:
        file_location (str): The path to the file.

    Returns:
        str: The updated file location, ensuring it ends with '.html'.
    """
    if not file_location.lower().endswith(".html"):
        new_file_location = file_location + ".html"
        return new_file_location
    return file_location


def run_full_friday(args, task, session_list):
    print("Running Full Friday ...")
    agent = FridayAgent(
        FridayPlanner, FridayRetriever, FridayExecutor, ToolManager, config=args
    )
    error, result = agent.run(task=task)
    list = agent.extract_information(result, "<return>", "</return>")
    if len(list) > 0:
        result = " ".join(list)

    return error, result


def run_light_friday(args, task, session_list):
    print("Running Light Friday ...")
    agent = LightFriday(args)
    result = agent.run(task=task)
    #print("Light Friday error: ", error)
    print("Light Friday result: ", result)
    return result



@app.post("/process-task")
async def process_task(
    contain_html: bool = Form(...),  # Specifies if the request includes an HTML file
    html_file: UploadFile = File(None),  # The uploaded HTML file (optional)
    userOrder: str = Form(""),  # The user's order
    session_list: str = Form(""),  # The session list (optional)
    use_light_friday: bool = Form(False),  # Use Light Friday or full Friday
):
    args = setup_config()
    try:
        # 将 session_list 转换为 Python 对象
        session_list_data = json.loads(session_list)
        if not isinstance(session_list_data, list):
            raise ValueError("session_list is not a list")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail={"error": "Invalid session_list format."}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

    try:
        if contain_html and html_file is not None:
            # Save the uploaded html_file to working_dir
            working_dir = args.working_dir
            file_location = os.path.join(working_dir, html_file.filename)
            file_location = ensure_html_extension(file_location)
            args.query_file_path = file_location
            with open(file_location, "wb") as f:
                f.write(await html_file.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid HTML content."})

    # Generate query using userOrder
    args.query = userOrder + f"\n{session_list}"
    task = setup_pre_run(args)

    error, result = None, None
    if use_light_friday:
        error, result = run_light_friday(args, task, session_list)
    else:
        error, result = run_full_friday(args, task, session_list)

    if error:
        raise HTTPException(
            status_code=500,
            detail={"error": f"{error}"},
        )

    return {
        "response": result,
        "script": "Not implemented yet",
    }


@app.get("/hello")
def hello_world():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
