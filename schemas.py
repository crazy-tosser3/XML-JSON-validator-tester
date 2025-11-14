from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ValidationResponse(BaseModel):
    test_uuid: str
    status: str
    errors_count: int
    validation_time_ms: float
    server_processing_time_ms: float
    errors: List[str]


class ValidationResultDB(BaseModel):
    id: int
    validation_type: str
    input_file_name: Optional[str]
    is_valid: bool
    execution_time_ms: float
    error_count: int
    errors: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    json_avg_time: float
    xml_avg_time: float
    json_total_count: int
    xml_total_count: int
    json_valid_count: int
    xml_valid_count: int
