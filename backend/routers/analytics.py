from fastapi import APIRouter, Query
from typing import Optional, List, Dict
import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

class AnalyticsDataPoint(BaseModel):
    timestamp: str
    value: float

class AnalyticsResponse(BaseModel):
    metric: str
    data: List[AnalyticsDataPoint]

@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    metric: Optional[str] = Query("visitors", description="Metric to retrieve (e.g., visitors, revenue, errors)")
):
    # Mock some data based on dates if provided
    base_date = datetime.datetime.now()
    if start_date:
        try:
            base_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass

    data = []
    # Generate mock 7 days of data if no end_date provided for simplicity
    num_days = 7
    if end_date and start_date:
        try:
            ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            delta = (ed - sd).days
            if delta > 0 and delta <= 30:
                num_days = delta + 1
        except ValueError:
            pass

    import random
    random.seed(metric) # Consistent mock data per metric

    for i in range(num_days):
        current_date = base_date + datetime.timedelta(days=i)
        value = random.uniform(10.0, 1000.0)
        data.append(AnalyticsDataPoint(
            timestamp=current_date.strftime("%Y-%m-%d"),
            value=round(value, 2)
        ))

    return AnalyticsResponse(
        metric=metric,
        data=data
    )
