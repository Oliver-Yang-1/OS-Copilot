from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import os
import pickle
from fastapi import Request
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import json

router = APIRouter()

# 设置 Google Calendar API 的作用域
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = 'credentials.json'
REDIRECT_URI = 'http://localhost:8000/tools/calendar/oauth2callback'

user_credentials = {}
# 定义事件创建的数据模型
class EventCreate(BaseModel):
    summary: str = Field(..., description="Title", example="Meeting")
    location: Optional[str] = Field(None, description="Event Location", example="Meeting Room")
    description: Optional[str] = Field(None, description="Event Description", example="Discussion")
    start_time: datetime = Field(..., description="Event Start Time", example="2023-10-28T09:00:00+08:00")
    end_time: datetime = Field(..., description="Event End Time", example="2023-10-28T10:00:00+08:00")
    time_zone: Optional[str] = Field("Asia/Shanghai", description="Time Zone", example="Asia/Shanghai")

# 定义事件更新的数据模型
class EventUpdate(BaseModel):
    summary: Optional[str] = Field(None, description="Event Title", example="Updated Meeting")
    location: Optional[str] = Field(None, description="Event Location", example="New Meeting Room")
    description: Optional[str] = Field(None, description="Event Description", example="Updated Discussion")
    start_time: Optional[datetime] = Field(None, description="Event Start Time", example="2023-10-28T09:00:00+08:00")
    end_time: Optional[datetime] = Field(None, description="Event End Time", example="2023-10-28T10:00:00+08:00")
    time_zone: Optional[str] = Field(None, description="Time Zone", example="Asia/Shanghai")

# 获取 Google Calendar 服务
@router.get("/tools/calendar/login", summary="User login to authorize Google Calendar access")
def login(user_id: str):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    # 将 state 与 user_id 关联
    user_credentials[user_id] = {'state': state}
    return {"authorization_url": authorization_url}

# 处理授权回调
@router.get("/tools/calendar/oauth2callback", summary="Handle OAuth2 callback")
def oauth2callback(request: Request, user_id: str):
    state = request.query_params.get('state')
    code = request.query_params.get('code')
    stored_state = user_credentials.get(user_id, {}).get('state')
    if state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    # 存储用户凭据
    user_credentials[user_id]['creds'] = json.loads(creds.to_json())
    return {"message": "Authorization successful"}

# 获取 Google Calendar 服务
def get_calendar_service(user_id: str):
    cred_info = user_credentials.get(user_id, {}).get('creds')
    if not cred_info:
        raise HTTPException(status_code=401, detail="User not authorized")
    creds = Credentials.from_authorized_user_info(cred_info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        # 更新凭据
        user_credentials[user_id]['creds'] = json.loads(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

import pytz
# 创建事件
@router.get("/tools/calendar/create", summary="Create a new calendar event using Google calendar")
async def create_event(event: EventCreate):
    service = get_calendar_service()
    start_time = event.start_time.isoformat()
    end_time = event.end_time.isoformat()
    print(start_time, end_time)
    event_data = {
        'summary': event.summary,
        'location': event.location,
        'description': event.description,
        'start': {
            'dateTime': start_time,
            'timeZone': event.time_zone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': event.time_zone,
        },
    }
    try:
        created_event = service.events().insert(calendarId='primary', body=event_data).execute()
        return {"event_id": created_event['id'], "htmlLink": created_event['htmlLink']}
    except Exception as e:
        print("something wrong with this event", e)
        raise HTTPException(status_code=500, detail=str(e))

# 获取即将发生的事件列表
@router.get("/tools/calendar/retrieve", summary="Retrieve the list of calendar event using Google calendar")
async def retrieve_events(max_results: int = 10):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z'表示UTC时间
    try:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 更新事件
@router.get("/tools/calendar/update/{event_id}", summary="Update an existing calendar event using Google calendar")
async def update_event(event_id: str, event: EventUpdate):
    service = get_calendar_service()
    try:
        event_data = service.events().get(calendarId='primary', eventId=event_id).execute()
        if event.summary:
            event_data['summary'] = event.summary
        if event.location:
            event_data['location'] = event.location
        if event.description:
            event_data['description'] = event.description
        if event.start_time and event.end_time:
            event_data['start'] = {
                'dateTime': event.start_time.isoformat(),
                'timeZone': event.time_zone or event_data['start'].get('timeZone', 'Asia/Shanghai'),
            }
            event_data['end'] = {
                'dateTime': event.end_time.isoformat(),
                'timeZone': event.time_zone or event_data['end'].get('timeZone', 'Asia/Shanghai'),
            }
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event_data).execute()
        return {"message": "Event updated", "event_id": updated_event['id'], "htmlLink": updated_event['htmlLink']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 删除事件
@router.get("/tools/calendar/delete/{event_id}", summary="Delete an existing calendar event using Google calendar")
async def delete_event(event_id: str):
    service = get_calendar_service()
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"message": "Event deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))