import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any
from taskiq import TaskiqDepends, Context
from models import get_task
from models import get_customer
from taskiq_redis import RedisStreamBroker

from config.settings import settings

from worker import broker

@broker.task
async def import_customers_task(
    file_path: str,
    user_id: str,
    context: Context = TaskiqDepends(),
) -> Dict[str, Any]:
    Task = get_task()
    Customer = get_customer()
    job_id = context.message.task_id
    task_obj = await Task.find_one({"job_id": job_id})
    if not task_obj:
        raise Exception(f"Task {job_id} not found")

    try:
        task_obj.status = "running"
        task_obj.started_at = datetime.now()
        await task_obj.commit()
        df = pd.read_csv(file_path)
        total_rows = len(df)
        task_obj.total_items = total_rows
        await task_obj.commit()

        def safe_str(val, default=''):
            """Chuyển về str và strip, nếu NaN thì trả về default."""
            if pd.isna(val):
                return default
            return str(val).strip()

        for idx, (_, row) in enumerate(df.iterrows()):
            try:
                email = safe_str(row.get('email'))
                full_name = safe_str(row.get('full_name'))
                if not email or not full_name:
                    task_obj.failed_items += 1
                    print(f"[IMPORT] Row {idx+1} missing email or full_name: {row.to_dict()}")
                    continue
                existing = await Customer.find_one({"email": email})
                if existing:
                    task_obj.failed_items += 1
                    print(f"[IMPORT] Row {idx+1} duplicate email: {email}")
                    continue
                customer_data = {
                    "email": email,
                    "full_name": full_name,
                    "phone": safe_str(row.get('phone'), None),
                    "company": safe_str(row.get('company'), None),
                    "position": safe_str(row.get('position'), None),
                    "address": safe_str(row.get('address'), None),
                    "city": safe_str(row.get('city'), None),
                    "country": safe_str(row.get('country'), None),
                    "language": safe_str(row.get('language'), 'vi'),
                    "tags": [tag.strip() for tag in str(row.get('tags') or '').split(',') if tag.strip()] if pd.notna(row.get('tags')) else []
                }
                customer = Customer(**customer_data)
                await customer.commit()
                task_obj.processed_items += 1
                print(f"[IMPORT] Row {idx+1} imported: {customer_data['email']}")
            except Exception as e:
                task_obj.failed_items += 1
                print(f"[IMPORT] Row {idx+1} error: {str(e)} -- {row.to_dict()}")
            if (idx + 1) % 10 == 0:
                task_obj.progress = (idx + 1) / total_rows
                await task_obj.commit()

        task_obj.progress = 1.0
        task_obj.status = "completed"
        task_obj.completed_at = datetime.now()
        await task_obj.commit()
        try:
            os.remove(file_path)
        except Exception:
            pass
        result = {
            "status": "completed",
            "total_rows": total_rows,
            "processed": task_obj.processed_items,
            "failed": task_obj.failed_items,
            "success_rate": f"{(task_obj.processed_items / total_rows) * 100:.1f}%"
        }
        task_obj.result = result
        await task_obj.commit()
        return result
    except Exception as e:
        task_obj.status = "failed"
        task_obj.error_message = str(e)
        task_obj.completed_at = datetime.now()
        await task_obj.commit()
        raise
