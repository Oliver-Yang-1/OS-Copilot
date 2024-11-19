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


@app.post("/process-task")
async def process_task(
    contain_html: bool = Form(...),  # 从 form-data 获取布尔值
    html_file: UploadFile = File(None),  # 从 form-data 获取文件
    userOrder: str = Form(""),  # 从 form-data 获取字符串
):
    if contain_html and html_file is not None:
        # Save the uploaded html_file to working_dir
        args = setup_config()
        working_dir = args.working_dir
        file_location = os.path.join(working_dir, html_file.filename)
        with open(file_location, "wb") as f:
            f.write(await html_file.read())
    else:
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
