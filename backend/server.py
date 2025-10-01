from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, date
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions for MongoDB datetime handling
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str):
                try:
                    if 'T' in value and (value.endswith('Z') or '+' in value[-6:]):
                        item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    elif len(value) == 10 and value.count('-') == 2:
                        item[key] = datetime.fromisoformat(value + 'T00:00:00').date()
                except:
                    pass
    return item

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict
class ClientStatusType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str = "#3B82F6"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientStatusTypeCreate(BaseModel):
    name: str
    color: Optional[str] = "#3B82F6"

class ActionStatusType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    key: str  # made_order, completed_survey, etc.
    color: str = "#3B82F6"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ActionStatusTypeCreate(BaseModel):
    name: str
    key: str
    color: Optional[str] = "#3B82F6"

class ActionStatus(BaseModel):
    made_order: bool = False
    completed_survey: bool = False
    notified_about_promotion: bool = False
    has_additional_questions: bool = False
    need_callback: bool = False
    not_answering: bool = False
    planning_order: bool = False

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    phone: Optional[str] = ""
    client_status: str
    crm_link: Optional[str] = ""
    expected_order_sets: Optional[int] = 0
    expected_order_amount: Optional[float] = 0.0
    sets_ordered_this_month: Optional[int] = 0
    amount_this_month: Optional[float] = 0.0
    debt: Optional[float] = 0.0
    last_contact_date: Optional[date] = None
    task_description: Optional[str] = ""
    comment: Optional[str] = ""
    action_status: ActionStatus = Field(default_factory=ActionStatus)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = ""
    client_status: str
    crm_link: Optional[str] = ""
    expected_order_sets: Optional[int] = 0
    expected_order_amount: Optional[float] = 0.0
    sets_ordered_this_month: Optional[int] = 0
    amount_this_month: Optional[float] = 0.0
    debt: Optional[float] = 0.0
    last_contact_date: Optional[date] = None
    task_description: Optional[str] = ""
    comment: Optional[str] = ""
    action_status: Optional[ActionStatus] = Field(default_factory=ActionStatus)

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    client_status: Optional[str] = None
    crm_link: Optional[str] = None
    expected_order_sets: Optional[int] = None
    expected_order_amount: Optional[float] = None
    sets_ordered_this_month: Optional[int] = None
    amount_this_month: Optional[float] = None
    debt: Optional[float] = None
    last_contact_date: Optional[date] = None
    task_description: Optional[str] = None
    comment: Optional[str] = None
    action_status: Optional[ActionStatus] = None

class DailyReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date
    orders_in_assembly: Optional[int] = 0
    sets_count: Optional[int] = 0
    orders_amount: Optional[float] = 0.0
    money_received_today: Optional[float] = 0.0
    call_attempts: Optional[int] = 0
    successful_calls: Optional[int] = 0
    self_messaged_client: Optional[int] = 0
    responses: Optional[int] = 0
    chats_today: Optional[int] = 0
    clients_no_order: Optional[int] = 0
    comment: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DailyReportCreate(BaseModel):
    date: date
    orders_in_assembly: Optional[int] = 0
    sets_count: Optional[int] = 0
    orders_amount: Optional[float] = 0.0
    money_received_today: Optional[float] = 0.0
    call_attempts: Optional[int] = 0
    successful_calls: Optional[int] = 0
    self_messaged_client: Optional[int] = 0
    responses: Optional[int] = 0
    chats_today: Optional[int] = 0
    clients_no_order: Optional[int] = 0
    comment: Optional[str] = ""

class DailyReportUpdate(BaseModel):
    date: Optional[date] = None
    orders_in_assembly: Optional[int] = None
    sets_count: Optional[int] = None
    orders_amount: Optional[float] = None
    money_received_today: Optional[float] = None
    call_attempts: Optional[int] = None
    successful_calls: Optional[int] = None
    self_messaged_client: Optional[int] = None
    responses: Optional[int] = None
    chats_today: Optional[int] = None
    clients_no_order: Optional[int] = None
    comment: Optional[str] = None

# Client Status Types Routes
@api_router.get("/client-status-types", response_model=List[ClientStatusType])
async def get_client_status_types():
    status_types = await db.client_status_types.find().to_list(1000)
    return [ClientStatusType(**parse_from_mongo(st)) for st in status_types]

@api_router.post("/client-status-types", response_model=ClientStatusType)
async def create_client_status_type(input: ClientStatusTypeCreate):
    status_dict = input.dict()
    status_obj = ClientStatusType(**status_dict)
    status_data = prepare_for_mongo(status_obj.dict())
    await db.client_status_types.insert_one(status_data)
    return status_obj

@api_router.get("/client-status-types/{status_id}", response_model=ClientStatusType)
async def get_client_status_type(status_id: str):
    status_type = await db.client_status_types.find_one({"id": status_id})
    if not status_type:
        raise HTTPException(status_code=404, detail="Status type not found")
    return ClientStatusType(**parse_from_mongo(status_type))

@api_router.put("/client-status-types/{status_id}", response_model=ClientStatusType)
async def update_client_status_type(status_id: str, input: ClientStatusTypeCreate):
    status_dict = input.dict()
    result = await db.client_status_types.update_one(
        {"id": status_id},
        {"$set": prepare_for_mongo(status_dict)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Status type not found")
    
    updated_status = await db.client_status_types.find_one({"id": status_id})
    return ClientStatusType(**parse_from_mongo(updated_status))

@api_router.delete("/client-status-types/{status_id}")
async def delete_client_status_type(status_id: str):
    result = await db.client_status_types.delete_one({"id": status_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Status type not found")
    return {"message": "Status type deleted"}

# Action Status Types Routes
@api_router.get("/action-status-types", response_model=List[ActionStatusType])
async def get_action_status_types():
    status_types = await db.action_status_types.find().to_list(1000)
    return [ActionStatusType(**parse_from_mongo(st)) for st in status_types]

@api_router.post("/action-status-types", response_model=ActionStatusType)
async def create_action_status_type(input: ActionStatusTypeCreate):
    status_dict = input.dict()
    status_obj = ActionStatusType(**status_dict)
    status_data = prepare_for_mongo(status_obj.dict())
    await db.action_status_types.insert_one(status_data)
    return status_obj

@api_router.put("/action-status-types/{status_id}", response_model=ActionStatusType)
async def update_action_status_type(status_id: str, input: ActionStatusTypeCreate):
    status_dict = input.dict()
    result = await db.action_status_types.update_one(
        {"id": status_id},
        {"$set": prepare_for_mongo(status_dict)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Action status type not found")
    
    updated_status = await db.action_status_types.find_one({"id": status_id})
    return ActionStatusType(**parse_from_mongo(updated_status))

@api_router.delete("/action-status-types/{status_id}")
async def delete_action_status_type(status_id: str):
    result = await db.action_status_types.delete_one({"id": status_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Action status type not found")
    return {"message": "Action status type deleted"}

# Clients Routes
@api_router.get("/clients/statistics")
async def get_client_statistics():
    total_clients = await db.clients.count_documents({})
    
    stats = {
        "total_clients": total_clients,
        "made_order": await db.clients.count_documents({"action_status.made_order": True}),
        "completed_survey": await db.clients.count_documents({"action_status.completed_survey": True}),
        "notified_about_promotion": await db.clients.count_documents({"action_status.notified_about_promotion": True}),
        "has_additional_questions": await db.clients.count_documents({"action_status.has_additional_questions": True}),
        "need_callback": await db.clients.count_documents({"action_status.need_callback": True}),
        "not_answering": await db.clients.count_documents({"action_status.not_answering": True}),
        "planning_order": await db.clients.count_documents({"action_status.planning_order": True}),
        "has_debt": await db.clients.count_documents({"debt": {"$gt": 0}}),
    }
    
    return stats

@api_router.get("/clients/summary")
async def get_client_summary():
    # Aggregate pipeline to calculate totals
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_expected_sets": {"$sum": "$expected_order_sets"},
                "total_expected_amount": {"$sum": "$expected_order_amount"},
                "total_ordered_sets": {"$sum": "$sets_ordered_this_month"},
                "total_ordered_amount": {"$sum": "$amount_this_month"},
                "total_debt": {"$sum": "$debt"}
            }
        }
    ]
    
    result = await db.clients.aggregate(pipeline).to_list(1)
    
    if result:
        summary = result[0]
        return {
            "total_expected_sets": summary.get("total_expected_sets", 0),
            "total_expected_amount": round(summary.get("total_expected_amount", 0.0), 2),
            "total_ordered_sets": summary.get("total_ordered_sets", 0),
            "total_ordered_amount": round(summary.get("total_ordered_amount", 0.0), 2),
            "total_debt": round(summary.get("total_debt", 0.0), 2)
        }
    else:
        return {
            "total_expected_sets": 0,
            "total_expected_amount": 0.0,
            "total_ordered_sets": 0,
            "total_ordered_amount": 0.0,
            "total_debt": 0.0
        }
    
    return stats

@api_router.get("/clients", response_model=List[Client])
async def get_clients(status_filter: Optional[str] = None):
    query = {}
    if status_filter:
        # Filter by action status
        if status_filter == "made_order":
            query["action_status.made_order"] = True
        elif status_filter == "completed_survey":
            query["action_status.completed_survey"] = True
        elif status_filter == "notified_about_promotion":
            query["action_status.notified_about_promotion"] = True
        elif status_filter == "has_additional_questions":
            query["action_status.has_additional_questions"] = True
        elif status_filter == "need_callback":
            query["action_status.need_callback"] = True
        elif status_filter == "not_answering":
            query["action_status.not_answering"] = True
        elif status_filter == "planning_order":
            query["action_status.planning_order"] = True
        elif status_filter == "has_debt":
            query["debt"] = {"$gt": 0}
    
    clients = await db.clients.find(query).to_list(1000)
    return [Client(**parse_from_mongo(client)) for client in clients]

@api_router.post("/clients", response_model=Client)
async def create_client(input: ClientCreate):
    client_dict = input.dict()
    client_obj = Client(**client_dict)
    client_data = prepare_for_mongo(client_obj.dict())
    await db.clients.insert_one(client_data)
    return client_obj

@api_router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return Client(**parse_from_mongo(client))

@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, input: ClientUpdate):
    client_dict = {k: v for k, v in input.dict().items() if v is not None}
    if not client_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.clients.update_one(
        {"id": client_id},
        {"$set": prepare_for_mongo(client_dict)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    
    updated_client = await db.clients.find_one({"id": client_id})
    return Client(**parse_from_mongo(updated_client))

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted"}

@api_router.patch("/clients/{client_id}/comment")
async def update_client_comment(client_id: str, comment: dict):
    result = await db.clients.update_one(
        {"id": client_id},
        {"$set": {"comment": comment.get("comment", "")}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Comment updated"}

# Daily Reports Routes
@api_router.get("/daily-reports", response_model=List[DailyReport])
async def get_daily_reports():
    reports = await db.daily_reports.find().sort("date", -1).to_list(1000)
    return [DailyReport(**parse_from_mongo(report)) for report in reports]

@api_router.post("/daily-reports", response_model=DailyReport)
async def create_daily_report(input: DailyReportCreate):
    # Check if report for this date already exists
    existing = await db.daily_reports.find_one({"date": input.date.isoformat()})
    if existing:
        raise HTTPException(status_code=400, detail="Report for this date already exists")
    
    report_dict = input.dict()
    report_obj = DailyReport(**report_dict)
    report_data = prepare_for_mongo(report_obj.dict())
    await db.daily_reports.insert_one(report_data)
    return report_obj

@api_router.get("/daily-reports/{report_id}", response_model=DailyReport)
async def get_daily_report(report_id: str):
    report = await db.daily_reports.find_one({"id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return DailyReport(**parse_from_mongo(report))

@api_router.put("/daily-reports/{report_id}", response_model=DailyReport)
async def update_daily_report(report_id: str, input: DailyReportUpdate):
    report_dict = {k: v for k, v in input.dict().items() if v is not None}
    if not report_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.daily_reports.update_one(
        {"id": report_id},
        {"$set": prepare_for_mongo(report_dict)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    
    updated_report = await db.daily_reports.find_one({"id": report_id})
    return DailyReport(**parse_from_mongo(updated_report))

@api_router.delete("/daily-reports/{report_id}")
async def delete_daily_report(report_id: str):
    result = await db.daily_reports.delete_one({"id": report_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted"}

# Root route
@api_router.get("/")
async def root():
    return {"message": "CRM API Ready"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()