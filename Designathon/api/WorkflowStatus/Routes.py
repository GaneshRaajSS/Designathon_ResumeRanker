# ✅ ROUTES FILE: api/WorkflowStatus/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.Schema import WorkflowStatusResponse
from api.WorkflowStatus.Service import get_all_workflows_db, get_workflow_status_by_jd_db, get_db
from api.Auth.okta_auth import get_current_user

router = APIRouter()

@router.get("/workflow-status", response_model=list[WorkflowStatusResponse])
def get_all_workflows(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_all_workflows_db(user, db)

@router.get("/jd/{jd_id}/workflow-status", response_model=WorkflowStatusResponse)
def get_workflow_status_by_jd(jd_id: str, db: Session = Depends(get_db)):
    status = get_workflow_status_by_jd_db(jd_id, db)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status
