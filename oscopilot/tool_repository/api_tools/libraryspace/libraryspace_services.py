
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, HTTPException,UploadFile,File,Form, Depends
from oscopilot.tool_repository.api_tools.libraryspace.libraryspace import parse_library_space

router = APIRouter()

@router.get("/tools/hku/libraryspace", summary=
"""
Fetch and parse real-time availability data of HKU library spaces.

Returns:
--------
list of dict
    A list of dictionaries containing space availability information.
    Each dictionary has the following keys:
    - Location: str, location code
    - Description: str, human-readable location description
    - Available: int, number of available spaces
    - Occupied: int, number of occupied spaces
    - Total: int, total number of spaces

Returns None if there's an error fetching or parsing the data.

Example:
--------
>>> spaces = parse_library_space()
>>> spaces[0]
{
    'Location': 'DEN05DR',
    'Description': 'Dental Library Discussion Rooms',
    'Available': 1,
    'Occupied': 3,
    'Total': 4
}          
""")
async def get_library_spaces():
    try:
        library = parse_library_space()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"library":library}
