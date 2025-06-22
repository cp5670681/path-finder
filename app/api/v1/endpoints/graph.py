import time

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_session
from app.models.graph_model import Graph, Node, TrafficLight, TrafficLightDelta
from app.schemas.response_schema import create_response

router = APIRouter()

# 最短路径
@router.get("/fastest_path")
def fastest_path(id: int, velocity: float, session: Session = Depends(get_session)):
    graph = session.get(Graph, id)
    delta = session.get(TrafficLightDelta, 1).delta
    edges, wait_times, all_wait_time, all_take_time = graph.dijkstra(time.time(), velocity, delta)
    edge_start_node_ids = [edge["start_node"]["id"] for edge in edges]
    return create_response(data={
        "edges": edges,
        "wait_times": [{**Node.find(node_id).to_dict(), "wait_time": int(wait_time)} for node_id, wait_time in wait_times.items() if node_id in edge_start_node_ids and wait_time > 0],
        "all_wait_time": all_wait_time,
        "all_take_time": all_take_time
    })

# 列表
@router.get("/")
def list_items(session: Session = Depends(get_session)):
    graphs = session.exec(select(Graph)).all()
    results = [{"id": graph.id, "name": graph.name} for graph in graphs]
    return create_response(data=results)

# 详情
@router.get("/{id}")
def get_item(id: int, session: Session = Depends(get_session)):
    graph = session.get(Graph, id)
    if graph is None:
        return create_response(data={})
    return create_response(data=graph.to_json())

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
