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
from typing import Optional
import io
import sys
import os

app = FastAPI()

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

@app.post("/process-task")
async def process_task(
        contain_html: bool = Form(...),  # 从 form-data 获取布尔值
        html_file: UploadFile = File(None),  # 从 form-data 获取文件
        userOrder: str = Form(""),  # 从 form-data 获取字符串
):
    args = setup_config()
    try:
        if contain_html and html_file is not None:
            # Save the uploaded html_file to working_dir
            args = setup_config()
            working_dir = args.working_dir
            file_location = os.path.join(working_dir, html_file.filename)
            file_location = ensure_html_extension(file_location)
            args.query_file_path = file_location
            with open(file_location, "wb") as f:
                f.write(await html_file.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid HTML content."})

    # Generate query using userOrder
    args.query = userOrder
    task = setup_pre_run(args)

    # Initialize and run the agent
    agent = FridayAgent(
        FridayPlanner, FridayRetriever, FridayExecutor, ToolManager, config=args
    )

    # Run the agent and get result
    error, result = agent.run(task=task)

    if error:
        raise HTTPException(
            status_code=500,
            detail={"error": f"{error}"},
        )
    list = agent.extract_information(result,'<return>','</return>')
    if len(list)>0:
        result = ' '.join(list)

    return {
        "response": result,
        "script": "Not implemented yet",
    }


@app.get("/hello")
def hello_world():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
