from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.telecom import Provider, RechargePlan
from app.schemas.telecom import PlanOut, ProviderOut

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("", response_model=list[PlanOut])
def list_plans(
    provider_id: int | None = Query(None),
    max_price: int | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(RechargePlan)
    if provider_id:
        query = query.filter(RechargePlan.provider_id == provider_id)
    if max_price:
        query = query.filter(RechargePlan.price <= max_price)
    return query.order_by(RechargePlan.price).all()


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(RechargePlan).filter(RechargePlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/providers/all", response_model=list[ProviderOut])
def list_providers(db: Session = Depends(get_db)):
    return db.query(Provider).all()