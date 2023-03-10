from fastapi import Depends, FastAPI
from sqlmodel import select  # type: ignore
from sqlmodel import Session

from database import get_engine, init_db
from models import SVProperty

app = FastAPI()


def get_main_engine():
    engine = get_engine("production")
    init_db(engine)
    return engine


def get_session():
    with Session(get_main_engine()) as session:
        yield session


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/create/property/{name}")
async def create_property_anonymously(
    *, session: Session = Depends(get_session), name: str
):
    property = SVProperty(name=name)
    session.add(property)
    session.commit()
    return {"created": {"name": name}}


@app.get("/user/{user}/create/property/{name}")
async def user_create_property(
    *, session: Session = Depends(get_session), user: str, name: str
):
    property = SVProperty(name=name, created_by=user)

    session.add(property)
    session.commit()

    session.refresh(property)
    # TODO error handling
    # return {"created": {"name": name}}
    return {"created": property.dict()}


@app.get("/user/{user}/veto/property/{name}")
async def user_veto_property(
    *, session: Session = Depends(get_session), user: str, name: str
):

    statement = select(SVProperty).where(SVProperty.name == name)
    results = session.exec(statement)
    property = results.one()

    if property:
        property.vetoed_by = property.vetoed_by + [user]
        session.commit()

        session.refresh(property)
        # return {"vetoed": {"name": name}}
        return {"vetoed": property.dict()}
    else:
        return {"error": "property not found"}
