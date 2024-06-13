
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import MetaData, inspect, select, text
from typing import List, Dict
from .database import get_async_session, async_engine, async_session_maker
from .crud import *
from .models import Tables
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncConnection

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can be restricted to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")



# Endpoint to get table names
# @app.get("/tables/")
# async def get_tables():
#     async with async_session_maker() as session:
#         async with session.begin():
#             result = await session.execute(
#                 text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
#             )
#             table_name = [row[0] for row in result.fetchall()]
#     return {"tables": table_name}

@app.get("/tables/")
async def get_tables(db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        # Get table names from the database
        result = await db.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        )
        current_table_names = {row[0] for row in result.fetchall()}

        # Get table names from the Tables table
        result = await db.execute(select(Tables))
        tables_in_db = {table.table_name for table in result.scalars().all()}

        # Insert new table names
        new_tables = current_table_names - tables_in_db
        for table_name in new_tables:
            new_table = Tables(table_name=table_name)
            db.add(new_table)

        # Delete old table names
        obsolete_tables = tables_in_db - current_table_names
        if obsolete_tables:
            await db.execute(delete(Tables).where(Tables.table_name.in_(obsolete_tables)))

    return {"tables": list(current_table_names)}



# Endpoint to get column names and data types for a specific table
@app.get("/tables/{table_name}/columns", response_model=Dict[str, str])
async def get_columns(table_name: str, db: AsyncSession = Depends(get_async_session)) -> Dict[str, str]:
    
    model_class = getattr(models, table_name.capitalize(), None)

    if model_class is None:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Get the column names and data types for the table
    columns = {}
    for column in model_class.__table__.columns:
        columns[column.name] = str(column.type)
    
    return columns

# Endpoint to get the list of tables from the tables table
@app.get("/all-tables", response_model=List[str])
async def get_all_tables(db: AsyncSession = Depends(get_async_session)):
    tables = await db.execute(select(Tables))
    table_names = sorted([table.table_name for table in tables.scalars().all()])
    
    return table_names

# Task3 routes (unchanged)
# Route to create a dashboard
@app.post("/dashboards/")
async def create_dashboard_handler(dashboard: DashboardCreate, db: AsyncSession = Depends(get_async_session)):
    created_dashboard = await create_dashboard(db, dashboard)
    return created_dashboard

# Route to get a dashboard
@app.get("/dashboards/{dashboard_id}")
async def read_dashboard(dashboard_id: UUID, db: AsyncSession = Depends(get_async_session)):
    # Cast the dashboard_id to String
    dashboard_id_str = str(dashboard_id)

    # Query the dashboard using the casted ID
    dashboard = await get_dashboard(db, dashboard_id_str)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

# Route to create a dashboard component
@app.post("/dashboards/{dashboard_id}/components/")
async def create_dashboard_component_handler(dashboard_id: str, component: DashboardComponentCreate, db: AsyncSession = Depends(get_async_session)):
    created_component = await create_dashboard_component(db, component, dashboard_id)
    return created_component

# Route to get dashboard components
@app.get("/dashboards/{dashboard_id}/components/")
async def read_dashboard_components(dashboard_id: str, db: AsyncSession = Depends(get_async_session)):
    components = await get_dashboard_components(db, dashboard_id)
    return components

# Route to delete a dashboard
@app.delete("/dashboards/{dashboard_id}")
async def delete_dashboard_handler(dashboard_id: str, db: AsyncSession = Depends(get_async_session)):
    deleted_dashboard = await delete_dashboard(db, dashboard_id)
    return deleted_dashboard

# Route to delete a dashboard component
@app.delete("/dashboards/components/{component_id}")
async def delete_dashboard_component_handler(component_id: UUID, db: AsyncSession = Depends(get_async_session)):
    component_id_str = str(component_id)
    deleted_component = await delete_dashboard_component(db, component_id_str)
    return deleted_component

# Route to update a dashboard
@app.put("/dashboards/{dashboard_id}")
async def update_dashboard_handler(dashboard_id: UUID, dashboard: DashboardUpdate, db: AsyncSession = Depends(get_async_session)):
    dashboard_id_str = str(dashboard_id)
    updated_dashboard = await update_dashboard(db, dashboard_id_str, dashboard)
    return updated_dashboard

# Route to update a dashboard component
@app.put("/dashboards/components/{component_id}")
async def update_dashboard_component_handler(component_id: UUID, component: DashboardComponentUpdate, db: AsyncSession = Depends(get_async_session)):
    component_id_str = str(component_id)
    updated_component = await update_dashboard_component(db, component_id_str, component)
    return updated_component