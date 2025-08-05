from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from models import get_customer, get_task
from services.auth import get_current_active_user
from tasks.import_customers import import_customers_task

from bson import ObjectId

router = APIRouter(prefix="/customers", tags=["Customers"])


class CustomerCreate(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    company: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    company: Optional[str]
    is_active: bool


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new customer."""
    Customer = get_customer()
    
    existing_customer = await Customer.find_one({"email": customer_data.email})
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists"
        )
    
    customer = Customer(**customer_data.dict())
    await customer.commit()
    
    return CustomerResponse(
        id=str(customer.id),
        email=customer.email,
        full_name=customer.full_name,
        phone=customer.phone,
        company=customer.company,
        is_active=customer.is_active
    )


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user)
):
    """List customers with pagination."""
    Customer = get_customer()
    customers = await Customer.find().skip(skip).limit(limit).to_list(length=limit)
    
    return [
        CustomerResponse(
            id=str(c.id),
            email=c.email,
            full_name=c.full_name,
            phone=c.phone,
            company=c.company,
            is_active=c.is_active
        )
        for c in customers
    ]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer_by_id(
    customer_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get customer by ID."""
    Customer = get_customer()
    obj_id = ObjectId(customer_id)
    customer = await Customer.find_one({"_id": obj_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse(
        id=str(customer.id),
        email=customer.email,
        full_name=customer.full_name,
        phone=customer.phone,
        company=customer.company,
        is_active=customer.is_active
    )


@router.post("/import")
async def import_customers(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """Import customers from CSV file using TaskIQ."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Save file temporarily
    import os
    from config.settings import settings
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
        
    # Start background task
    result = await import_customers_task.kiq(
        file_path=file_path,
        user_id=str(current_user.id)
    )

    job_id = result.task_id

    Task = get_task()
    task = Task(
        job_id=job_id,
        task_name="import_customers",
        status="pending",
        user_id=str(current_user.id),
        parameters={"file_path": file_path, "original_filename": file.filename}
    )
    await task.commit()
    
    return {
        "message": "CSV import started",
        "job_id": task.job_id,
        "task_id": str(task.id),
        "file_name": file.filename,
        "status": "queued"
    } 