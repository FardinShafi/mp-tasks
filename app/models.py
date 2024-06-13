# app/models.py

import uuid
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)

class Dashboard(Base):
    __tablename__ = 'dashboards'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String)
    updated_by = Column(String)

    components = relationship("DashboardComponent", back_populates="dashboard")

class DashboardComponent(Base):
    __tablename__ = "dashboard_components"

    id = Column(String, primary_key=True, unique=True, index=True)
    title = Column(String, nullable=False)
    property = Column(JSON, nullable=False)
    data_property = Column(JSON, nullable=False)
    filter_property = Column(JSON, nullable=False)
    dashboard_id = Column(String, ForeignKey('dashboards.id'), nullable=False)

    dashboard = relationship("Dashboard", back_populates="components", lazy="select")

class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department = Column(String)
    is_manager = Column(Boolean, default=False) 
    start_date = Column(Date)  

    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship("Department", back_populates="employees")

class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True) 
    enrollment_date = Column(Date) 

    guardian_id = Column(Integer, ForeignKey('guardian.id'))
    guardian = relationship("Guardian", back_populates="students")

class Guardian(Base):
    __tablename__ = 'guardian'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_number = Column(String)

    students = relationship("Student", back_populates="guardian")

class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    employees = relationship("Employee", back_populates="department")

class Tables(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, unique=True, index=True)

class Vendor(Base):
    __tablename__ = 'vendor'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_number = Column(String)
