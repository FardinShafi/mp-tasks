# app/schemas.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Task 3 schemas
class DashboardBase(BaseModel):
    title: str

class DashboardCreate(DashboardBase):
    components: Dict[str, Any]

class DashboardUpdate(BaseModel):
    title: str

class Dashboard(DashboardBase):
    id: str
    components: Dict[str, Any]

    class Config:
        from_attributes = True

class DashboardComponentBase(BaseModel):
    item: Dict[str, Any]
    content: Dict[str, Any]
    configuration: Dict[str, Any]
    dataSource: Dict[str, Any]

class DashboardComponentCreate(DashboardComponentBase):
    dashboard_id: str

class DashboardComponentUpdate(DashboardComponentBase):
    pass

class DashboardComponent(DashboardComponentBase):
    id: str
    dashboard_id: str

    class Config:
        from_attributes = True


# Task 2 schemas
class EmployeeBase(BaseModel):
    name: str
    department: str
    is_manager: Optional[bool] = False
    start_date: Optional[datetime] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    department_id: int

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    grade: int
    is_active: Optional[bool] = True
    enrollment_date: Optional[datetime] = None

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    guardian_id: int

    class Config:
        from_attributes = True

class GuardianBase(BaseModel):
    name: str
    contact_number: str

class GuardianCreate(GuardianBase):
    pass

class Guardian(GuardianBase):
    id: int
    students: List[Student] = []

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    employees: List[Employee] = []

    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    contact_number: str

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int

    class Config:
        from_attributes = True

class TablesBase(BaseModel):
    table_name: str

class TablesCreate(TablesBase):
    pass

class Tables(TablesBase):
    id: int

    class Config:
        from_attributes = True

# Auth schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class JSONInsert(BaseModel):
    json_data: Dict[str, Any]