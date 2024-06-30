from datetime import datetime
from uuid import UUID, uuid4
import uuid
from sqlalchemy import String, cast, delete, inspect, update, select # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from fastapi import HTTPException, status # type: ignore
from .models import Dashboard, DashboardComponent, Employee, Student, Guardian, Department, Tables, Vendor
from .schemas import DashboardCreate, DashboardComponentCreate, DashboardUpdate, DashboardComponentUpdate, JSONInsert
from app import models
from datetime import datetime
from sqlalchemy import select # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from fastapi import HTTPException # type: ignore
from .models import Dashboard, DashboardComponent, User
from .schemas import DashboardCreate, DashboardComponentCreate, DashboardUpdate, DashboardComponentUpdate, UserCreate
from passlib.hash import bcrypt
from .database import async_session_maker

# Task3 functions (unchanged)


async def get_dashboard(db: AsyncSession, dashboard_id: UUID):
    result = await db.execute(select(Dashboard).filter(Dashboard.id == dashboard_id))
    return result.scalars().first()


async def get_dashboard_components(db: AsyncSession, dashboard_id: str):
    result = await db.execute(
        select(DashboardComponent).filter(cast(DashboardComponent.dashboard_id, String) == dashboard_id)
    )
    return result.scalars().all()

async def delete_dashboard(db: AsyncSession, dashboard_id: str):
    result = await db.execute(
        delete(Dashboard).where(cast(Dashboard.id, String) == dashboard_id)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return {"message": "Dashboard deleted successfully"}

async def delete_dashboard_component(db: AsyncSession, component_id: str):
    result = await db.execute(
        select(DashboardComponent).filter(cast(DashboardComponent.id, String) == component_id)
    )
    component = result.scalars().first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    await db.delete(component)
    await db.commit()
    return {"message": "Component deleted successfully"}

async def update_dashboard(db: AsyncSession, dashboard_id: str, dashboard: DashboardUpdate):
    # Update the dashboard with the given ID
    result = await db.execute(
        update(Dashboard)
        .where(cast(Dashboard.id, String) == dashboard_id)
        .values(**dashboard.dict())
        .execution_options(synchronize_session=False)
    )
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return {"message": "Dashboard updated successfully"}

async def update_dashboard_component(db: AsyncSession, component_id: str, component: DashboardComponentUpdate):
    # Update the dashboard component with the given ID
    query = (
        update(DashboardComponent)
        .where(cast(DashboardComponent.id, String) == component_id)
        .values(**component.dict(exclude_unset=True))
        .execution_options(synchronize_session=False)
    )
    print(query)  # Print the query being executed for debugging
    await db.execute(query)
    await db.commit()

    # Fetch the updated component
    updated_component = await db.execute(
        select(DashboardComponent).filter(cast(DashboardComponent.id, String) == component_id)
    )
    db_component = updated_component.scalars().first()
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")

    return db_component

# Async functions for task2

async def get_table_names(db: AsyncSession):
    inspector = inspect(db.bind)
    return inspector.get_table_names()

async def get_column_info(db: AsyncSession, table_name: str):
    model_class = getattr(models, table_name.capitalize(), None)
    if model_class is None:
        raise HTTPException(status_code=404, detail="Table not found")
    
    columns = {}
    for column in model_class.__table__.columns:
        columns[column.name] = str(column.type)
    
    return columns

async def get_all_tables(db: AsyncSession):
    tables = await db.execute(select(Tables))
    table_names = sorted([table.table_name for table in tables.scalars().all()])
    
    return table_names


# Function to get a user by username
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    # Check if the username already exists
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create the new user if the username does not exist
    db_user = User(
        username=user.username,
        hashed_password=bcrypt.hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
    

async def get_user(username: str) -> User:
    async with async_session_maker() as session:
        async with session.begin():
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            return result.scalars().first()
        
import logging

# Create a logger instance
logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if user and user.verify_password(password):
        return user
    return None


async def create_dashboard(db: AsyncSession, dashboard: DashboardCreate):
    # Create the Dashboard entity
    db_dashboard = Dashboard(
        title=dashboard.title,
        components=dashboard.components  # Store the entire JSON structure here
    )
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)
     # Extract items from the "item" section
    items = dashboard.components.get("item", {}).get("items", [])

    # Create a list to hold DashboardComponent objects
    components_to_create = []

    # Iterate over items to create DashboardComponent entries
    for item in items:
        i_value = item.get("i")

        # Find corresponding content, configuration, and dataSource entries
        content_data = next((c for c in dashboard.components.get("content", []) if c.get("i") == i_value), {})
        config_data = next((c for c in dashboard.components.get("configuration", []) if c.get("i") == i_value), {})
        ds_data = next((d for d in dashboard.components.get("dataSource", []) if d.get("i") == i_value), {})

        # Create DashboardComponent object
        component = DashboardComponent(
            dashboard_id=db_dashboard.id,
            item=item,
            content=content_data,
            configuration=config_data,
            dataSource=ds_data
        )
        components_to_create.append(component)

    # Bulk insert all components
    db.add_all(components_to_create)
    await db.commit()

    # Return the created Dashboard entity with components included
    return {"id": db_dashboard.id, "title": db_dashboard.title}

async def create_dashboard_component(db: AsyncSession, component: DashboardComponentCreate, dashboard_id: str):
    db_component = DashboardComponent(
        dashboard_id=dashboard_id,
        item=component.item,
        content=component.content,
        configuration=component.configuration,
        dataSource=component.dataSource
    )
    db.add(db_component)
    await db.commit()
    await db.refresh(db_component)
    return db_component

# async def delete_dashboard(db: AsyncSession, dashboard_id: str):
#     await db.execute(delete(Dashboard).where(Dashboard.id == dashboard_id))
#     await db.commit()

# async def delete_dashboard_component(db: AsyncSession, component_id: str):
#     await db.execute(delete(DashboardComponent).where(DashboardComponent.id == component_id))
#     await db.commit()