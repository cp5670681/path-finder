from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.base_schema import BaseSchema


class NodeSchema(BaseSchema):
    graph_id: int
    lng: float
    lat: float

    model_config = ConfigDict(from_attributes=True)


class EdgeSchema(BaseSchema):
    graph_id: int
    start_node_id: int
    end_node_id: int
    length: float
    start_node: NodeSchema
    end_node: NodeSchema

    model_config = ConfigDict(from_attributes=True)


class GraphListSchema(BaseSchema):
    name: str


class GraphDetailSchema(BaseSchema):
    name: str
    start_node_id: int
    end_node_id: int
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]

    model_config = ConfigDict(from_attributes=True)


# 最短路径的一条路径
class FastestPathItem(BaseModel):
    edge: EdgeSchema
    velocity: float
    wait_time: float

    model_config = ConfigDict(from_attributes=True)


class FastestPathResponse(BaseModel):
    paths: List[FastestPathItem]
    all_take_time: float
    all_wait_time: float

    # 智能调整速度
    def adjust_velocity(self):
        pass


class TrafficLightSchema(BaseSchema):
    edge_id: int
    period: float
    pass_interval: int
    start_moment: int
    end_moment: int
    is_show: bool

    edge: EdgeSchema

    model_config = ConfigDict(from_attributes=True)

    def correct_schema(self, delta):
        self.start_moment += delta
        self.end_moment += delta
        return self
