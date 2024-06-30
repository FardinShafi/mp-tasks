import asyncio
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import MetaData, inspect, select, text, delete
from typing import Any, List, Dict
from .database import get_async_session, async_engine, async_session_maker
from .crud import *
from .models import Tables
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .auth import create_access_token, get_current_user
from .schemas import UserCreate, UserLogin, Token, DashboardCreate, DashboardUpdate, DashboardComponentCreate, DashboardComponentUpdate, JSONInsert
from .crud import create_user, authenticate_user, create_dashboard, get_dashboard, create_dashboard_component, get_dashboard_components, delete_dashboard, delete_dashboard_component, update_dashboard, update_dashboard_component
from .models import Tables
from sqlalchemy.sql.expression import delete


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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    db_user = await create_user(db, user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Protected routes example using JWT authentication
@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}

# Endpoint to get table names
@app.get("/tables/")
async def get_tables(db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
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

    return {"message": "Executed successfully", "data": {"tables": list(current_table_names)}}

# Endpoint to get column names and data types for a specific table

# Endpoint to get column names and data types for a specific table
@app.get("/tables/{table_name}/columns", response_model=Dict[str, Any])
async def get_columns(table_name: str, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    logger.debug(f"Retrieving columns for table: {table_name}")

    # Get the correct model class based on table name, ignoring case
    model_class = next((cls for cls in models.__dict__.values() if isinstance(cls, type) and getattr(cls, '__tablename__', '').lower() == table_name.lower()), None)

    if model_class is None:
        logger.error(f"Table not found for name: {table_name}")
        raise HTTPException(status_code=404, detail="Table not found")

    # Get the column names and data types for the table
    columns = []
    for column in model_class.__table__.columns:
        columns.append({
            "name": column.name,
            "title": column.name,
            "type": str(column.type)
        })

    logger.debug(f"Columns for table {table_name}: {columns}")
    return {"message": "columns retrieved successfully", "data": columns}

# Endpoint to get the list of tables from the tables table
@app.get("/all-tables", response_model=List[str])
async def get_all_tables(db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    tables = await db.execute(select(Tables))
    table_names = sorted([table.table_name for table in tables.scalars().all()])
    
    return table_names

# Task3 routes (unchanged)
# Route to create a dashboard
@app.post("/dashboards/")
async def create_dashboard_handler(dashboard: DashboardCreate, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    created_dashboard = await create_dashboard(db, dashboard)
    return {"message": "Dashboard created successfully", "data": created_dashboard}

@app.get("/dashboards/")
async def get_all_dashboards(db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    dashboards = await db.execute(select(Dashboard))
    dashboard_ids_and_titles = [{"dashboard_id": dashboard.id, "title": dashboard.title} for dashboard in dashboards.scalars().all()]
    return {"message": "dashboards retrieved successfully", "data": dashboard_ids_and_titles}

# Route to get a dashboard
@app.get("/dashboards/{dashboard_id}")
async def read_dashboard(dashboard_id: UUID, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    # Cast the dashboard_id to String
    dashboard_id_str = str(dashboard_id)

    # Query the dashboard using the casted ID
    dashboard = await get_dashboard(db, dashboard_id_str)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard
    
# Route to get all dashboard components
@app.get("/dashboard_components")
async def get_all_dashboard_components(db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    components = await db.execute(select(DashboardComponent))
    component_ids_and_dashboard_ids = [{"component_id": component.id, "dashboard_id": component.dashboard_id} for component in components.scalars().all()]
    return {"message": "components retrieved successfully", "data": component_ids_and_dashboard_ids}

# Route to create a dashboard component
@app.post("/dashboards/{dashboard_id}/components/")
async def create_dashboard_component_handler(dashboard_id: str, component: DashboardComponentCreate, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    created_component = await create_dashboard_component(db, component, dashboard_id)
    return created_component

# Route to get dashboard components
@app.get("/dashboards/{dashboard_id}/components/")
async def read_dashboard_components(dashboard_id: str, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    components = await get_dashboard_components(db, dashboard_id)
    return components

# Route to delete a dashboard
@app.delete("/dashboards/{dashboard_id}")
async def delete_dashboard_handler(dashboard_id: str, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    deleted_dashboard = await delete_dashboard(db, dashboard_id)
    return deleted_dashboard

# Route to delete a dashboard component
@app.delete("/dashboards/components/{component_id}")
async def delete_dashboard_component_handler(component_id: UUID, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    component_id_str = str(component_id)
    deleted_component = await delete_dashboard_component(db, component_id_str)
    return deleted_component

# Route to update a dashboard
@app.put("/dashboards/{dashboard_id}")
async def update_dashboard_handler(dashboard_id: UUID, dashboard: DashboardUpdate, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    dashboard_id_str = str(dashboard_id)
    updated_dashboard = await update_dashboard(db, dashboard_id_str, dashboard)
    return updated_dashboard

# Route to update a dashboard component
@app.put("/dashboards/components/{component_id}")
async def update_dashboard_component_handler(component_id: UUID, component: DashboardComponentUpdate, db: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_user)):
    component_id_str = str(component_id)
    updated_component = await update_dashboard_component(db, component_id_str, component)
    return updated_component

