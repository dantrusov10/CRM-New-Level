"""FastAPI application exposing endpoints for the Sales Intelligence Hub."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from .db import SessionLocal, engine
from . import models


# Create tables on startup
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Sales Intelligence Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    """Simple health check endpoint."""
    return {"ok": True}


# Pydantic schemas

class CompanyBase(BaseModel):
    name: str = Field(..., description="Company name")
    inn: Optional[str] = Field(None, description="Tax ID")
    industry: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    inn: Optional[str] = None
    industry: Optional[str] = None


class CompanyOut(CompanyBase):
    id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    name: str
    position: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    company_id: int


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None


class ClientOut(ClientBase):
    id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True


class DealBase(BaseModel):
    name: str
    company_id: int
    stage: Optional[str] = None
    owner: Optional[str] = None
    probability: Optional[float] = None
    potential_economy: Optional[float] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    name: Optional[str] = None
    stage: Optional[str] = None
    owner: Optional[str] = None
    probability: Optional[float] = None
    potential_economy: Optional[float] = None


class DealOut(DealBase):
    id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True


class EventCreate(BaseModel):
    type: str
    source: str
    payload: str
    company_id: Optional[int] = None


class EventOut(BaseModel):
    id: int
    type: str
    source: str
    payload: str
    created_at: Optional[str]
    company_id: Optional[int] = None

    class Config:
        orm_mode = True


# CRUD endpoints

@app.post("/companies", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@app.get("/companies", response_model=List[CompanyOut])
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(models.Company).offset(skip).limit(limit).all()
    return companies


@app.get("/companies/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.put("/companies/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, update: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@app.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return None


@app.post("/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Ensure company exists
    company = db.query(models.Company).filter(models.Company.id == client.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Associated company does not exist")
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/clients", response_model=List[ClientOut])
def list_clients(company_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Client)
    if company_id is not None:
        query = query.filter(models.Client.company_id == company_id)
    return query.all()


@app.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=ClientOut)
def update_client(client_id: int, update: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client


@app.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return None


@app.post("/deals", response_model=DealOut, status_code=status.HTTP_201_CREATED)
def create_deal(deal: DealCreate, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == deal.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Associated company does not exist")
    db_deal = models.Deal(**deal.dict())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal


@app.get("/deals", response_model=List[DealOut])
def list_deals(company_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Deal)
    if company_id is not None:
        query = query.filter(models.Deal.company_id == company_id)
    return query.all()


@app.get("/deals/{deal_id}", response_model=DealOut)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@app.put("/deals/{deal_id}", response_model=DealOut)
def update_deal(deal_id: int, update: DealUpdate, db: Session = Depends(get_db)):
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(deal, key, value)
    db.commit()
    db.refresh(deal)
    return deal


@app.delete("/deals/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    db.delete(deal)
    db.commit()
    return None


@app.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events", response_model=List[EventOut])
def list_events(
    company_id: Optional[int] = None,
    type: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)
    if company_id is not None:
        query = query.filter(models.Event.company_id == company_id)
    if type is not None:
        query = query.filter(models.Event.type == type)
    if source is not None:
        query = query.filter(models.Event.source == source)
    query = query.order_by(models.Event.created_at.desc())
    return query.offset(skip).limit(limit).all()
