import time
from typing import List, Sequence, Type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import get_session
from app.models.graph_model import Graph, Node, TrafficLight, TrafficLightDelta, Edge
from app.schemas.graph_schema import GraphDetailSchema, FastestPathResponse, TrafficLightSchema, GraphListSchema
from app.schemas.response_schema import create_response, IResponseBase
from app.services.fastest_path import FastestPath

router = APIRouter()


# 最短路径
@router.get("/fastest_path")
def fastest_path(id: int, velocity: float, session: Session = Depends(get_session)) -> IResponseBase[FastestPathResponse]:
    graph: Graph | None = session.exec(
        select(Graph)
        .where(Graph.id == id)
        .options(
            selectinload(Graph.edges).selectinload(Edge.traffic_light)
        )
    ).first()
    delta = session.get(TrafficLightDelta, 1).delta
    result = FastestPath(graph).find_fastest_path(time.time(), velocity, delta)
    return create_response(data=result)


# 列表
@router.get("/", response_model=IResponseBase[Sequence[GraphListSchema]])
def list_items(session: Session = Depends(get_session)) -> IResponseBase[Sequence[Graph]]:
    graphs = session.exec(
        select(Graph)
    ).all()
    return create_response(data=graphs)


# 详情
@router.get("/{id}", response_model=IResponseBase[GraphDetailSchema])
def get_item(id: int, session: Session = Depends(get_session)) -> IResponseBase[Graph]:
    graph: Graph | None = session.get(Graph, id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    return create_response(data=graph)


# 红绿灯列表
@router.get("/{id}/traffic_lights")
def get_traffic_lights(id: int, session: Session = Depends(get_session)) -> IResponseBase[Sequence[TrafficLightSchema]]:
    delta = session.get(TrafficLightDelta, 1).delta

    traffic_lights = session.exec(
        select(TrafficLight)
        .select_from(Edge)
        .join(TrafficLight, TrafficLight.edge_id == Edge.id)
        .where(TrafficLight.is_show == True, Edge.graph_id == id)
        .options(
            selectinload(TrafficLight.edge).selectinload(Edge.start_node),
            selectinload(TrafficLight.edge).selectinload(Edge.end_node),
        )
    ).all()
    traffic_lights = [TrafficLightSchema.from_orm(traffic_light).correct_schema(delta) for traffic_light in traffic_lights]
    return create_response(data=traffic_lights)


# 红绿灯调整
@router.post("/adjust")
def adjust(params: dict, session: Session = Depends(get_session)):
    traffic_light = session.get(TrafficLight, 0)
    delta = params['time'] - traffic_light.start_moment
    traffic_light_delta = session.get(TrafficLightDelta, 1)
    traffic_light_delta.delta = delta
    session.add(traffic_light_delta)
    session.commit()
    return create_response(data={})
