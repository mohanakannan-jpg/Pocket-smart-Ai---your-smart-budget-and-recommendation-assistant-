import json, os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
from contextlib import asynccontextmanager
from typing import Any, Literal
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from .calculations import calculate_plan, money
from .ai import get_advice
from .models import Base, Plan, SessionLocal, User, engine
from .products import find_products, generate_required_items, rank_products
from .security import hash_password, issue_token, verify_password, verify_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield
app = FastAPI(title="PocketSmart AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN","http://localhost:5173")], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
def db_session():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def current_user(authorization: str | None = Header(default=None), db: Session = Depends(db_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Sign in required")
    user=db.get(User,verify_token(authorization[7:]))
    if not user: raise HTTPException(401,"Session no longer exists")
    return user
class RegisterIn(BaseModel):
    name: str = Field(min_length=1,max_length=100)
    email: str = Field(min_length=3,max_length=254)
    password: str = Field(min_length=8,max_length=128)
    @field_validator("email")
    @classmethod
    def email_shape(cls,v):
        if "@" not in v or len(v.split("@")[-1]) < 3: raise ValueError("Enter a valid email")
        return v.lower().strip()
class LoginIn(BaseModel): email:str; password:str = Field(min_length=1,max_length=128)
class PlanIn(BaseModel):
    plannerType: Literal["interior","event","jewelry"]
    title: str = Field(min_length=1,max_length=140)
    data: dict[str,Any]
class CalculateIn(BaseModel):
    budget: int = Field(ge=0,le=10_000_000_000)
    categories: list[dict[str,Any]] = Field(max_length=100)
class RecommendationIn(CalculateIn):
    plannerType: Literal["interior","event","jewelry"]
    preferences: dict[str,Any] = Field(default_factory=dict)
class AuthOut(BaseModel): token:str; user:dict[str,Any]
def user_data(u:User): return {"id":u.id,"email":u.email,"name":u.name}
@app.get("/health")
def health(): return {"status":"ok","aiConfigured":bool(os.getenv("GEMINI_API_KEY"))}
@app.post("/auth/register",response_model=AuthOut,status_code=201)
def register(data:RegisterIn,db:Session=Depends(db_session)):
    if db.scalar(select(User).where(User.email==data.email)): raise HTTPException(409,"An account with this email already exists")
    user=User(name=data.name.strip(),email=data.email,password_hash=hash_password(data.password)); db.add(user);db.commit();db.refresh(user)
    return {"token":issue_token(user.id),"user":user_data(user)}
@app.post("/auth/login",response_model=AuthOut)
def login(data:LoginIn,db:Session=Depends(db_session)):
    user=db.scalar(select(User).where(User.email==data.email.lower().strip()))
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"token":issue_token(user.id),"user":user_data(user)}
@app.get("/me")
def me(user:User=Depends(current_user)): return user_data(user)
@app.post("/calculate")
def calculate(data:CalculateIn):
    try:return calculate_plan(data.budget,data.categories)
    except ValueError as e: raise HTTPException(422,str(e))
@app.get("/products")
def products(q:str=Query(default="",max_length=100),category:str=Query(default="",max_length=30)): return {"items":find_products(q,category),"source":"illustrative"}
@app.post("/recommendations")
def recommendations(data:RecommendationIn):
    result=calculate_plan(data.budget,data.categories)
    if result["overBudget"]:
        explanation=f"Your current plan is over budget by ₹{result['overBudget']/100:,.0f}. Reduce quantities or choose a lower-cost option first."
    elif result["remaining"]:
        explanation=f"You have ₹{result['remaining']/100:,.0f} unallocated. Keep it as a contingency or compare higher-quality options."
    else: explanation="Your estimated plan matches the selected budget."
    matching=rank_products(data.plannerType,max(0,result["remaining"]))
    advice=get_advice(data.plannerType,data.preferences,result["remaining"],result["overBudget"])
    recommendations=[{"title":"Budget-aware guidance","reason":explanation,"source":"deterministic fallback"}]
    if advice: recommendations.insert(0,{**advice.model_dump(),"source":"AI-enhanced explanation (validated)"})
    required_items=generate_required_items(data.plannerType,data.categories,data.preferences)
    return {"calculation":result,"recommendations":recommendations,"generatedItems":required_items,"products":matching,"aiStatus":"available" if advice else ("unavailable" if not os.getenv("GEMINI_API_KEY") else "temporarily unavailable"),"disclaimer":"Generated items are editable, price-free checklists based on your inputs. Products are local illustrative samples, not live listings. AI explanations are optional; all totals are calculated by the server."}
@app.post("/plans",status_code=201)
def create_plan(payload:PlanIn,user:User=Depends(current_user),db:Session=Depends(db_session)):
    plan=Plan(user_id=user.id,planner_type=payload.plannerType,title=payload.title.strip(),data=json.dumps(payload.data));db.add(plan);db.commit();db.refresh(plan);return serialize(plan)
@app.get("/plans")
def list_plans(user:User=Depends(current_user),db:Session=Depends(db_session)):
    return [serialize(p) for p in db.scalars(select(Plan).where(Plan.user_id==user.id).order_by(Plan.updated_at.desc())).all()]
def owned_plan(plan_id:int,user:User,db:Session):
    plan=db.get(Plan,plan_id)
    if not plan or plan.user_id!=user.id: raise HTTPException(404,"Plan not found")
    return plan
def serialize(p:Plan): return {"id":p.id,"plannerType":p.planner_type,"title":p.title,"data":json.loads(p.data),"createdAt":p.created_at,"updatedAt":p.updated_at}
@app.get("/plans/{plan_id}")
def get_plan(plan_id:int,user:User=Depends(current_user),db:Session=Depends(db_session)): return serialize(owned_plan(plan_id,user,db))
@app.put("/plans/{plan_id}")
def update_plan(plan_id:int,payload:PlanIn,user:User=Depends(current_user),db:Session=Depends(db_session)):
    plan=owned_plan(plan_id,user,db);plan.title=payload.title.strip();plan.planner_type=payload.plannerType;plan.data=json.dumps(payload.data);db.commit();db.refresh(plan);return serialize(plan)
@app.delete("/plans/{plan_id}",status_code=204)
def delete_plan(plan_id:int,user:User=Depends(current_user),db:Session=Depends(db_session)):
    db.delete(owned_plan(plan_id,user,db));db.commit()
