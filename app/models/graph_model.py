import math
from collections import defaultdict
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel


# 节点
class Node(BaseModel, table=True):
    __tablename__ = "nodes"
    graph_id: int = Field(index=True)
    # 经度
    lng: float
    # 纬度
    lat: float
    graph: "Graph" = Relationship(
        back_populates="nodes",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Node.graph_id) == Graph.id"
        }
    )

    @property
    def label(self):
        return f"node-{self.id}"

    def to_dict(self):
        return {"id": self.id, "lng": self.lng, "lat": self.lat}


# 边
class Edge(BaseModel, table=True):
    __tablename__ = "edges"
    graph_id: int = Field(index=True)
    # 边的起点
    start_node_id: int = Field(index=True)
    # 边的终点
    end_node_id: int = Field(index=True)
    # 边的长度
    length: float = Field(default=0)
    start_node: "Node" = Relationship(
        # back_populates="start_edges",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Edge.start_node_id) == Node.id"
        }
    )
    end_node: "Node" = Relationship(
        # back_populates="end_edges",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Edge.end_node_id) == Node.id"
        }
    )
    graph: "Graph" = Relationship(
        back_populates="edges",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Edge.graph_id) == Graph.id"
        }
    )
    traffic_light: "TrafficLight" = Relationship(
        back_populates="edge",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(TrafficLight.edge_id) == Edge.id"
        }
    )

    @property
    def label(self):
        return f"edge-{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "start_node": self.start_node.to_dict(),
            "end_node": self.end_node.to_dict(),
        }

    # 计算两点间距离
    def set_length(self):
        lat1 = self.start_node.lat * math.pi / 180
        lat2 = self.end_node.lat * math.pi / 180
        lat_delta = lat2 - lat1
        lng_delta = self.end_node.lng - self.start_node.lng
        lng_delta = lng_delta * math.pi / 180
        s = 2 * math.asin(math.sqrt(
            math.pow(math.sin(lat_delta / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(lng_delta / 2),
                                                                                              2)))
        s = s * 6378137
        self.length = s


class TrafficLight(BaseModel, table=True):
    __tablename__ = "traffic_lights"
    edge_id: int = Field(index=True)
    # 周期
    period: float
    # 通过的间隔
    pass_interval: int
    # 通过开始时刻
    start_moment: int
    # 是否在地图显示
    is_show: bool = Field(default=False)

    edge: "Edge" = Relationship(
        back_populates="traffic_light",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(TrafficLight.edge_id) == Edge.id"
        }
    )

    @property
    def end_moment(self):
        return self.start_moment + self.pass_interval

    def get_start_moment(self, delta):
        return self.start_moment + delta

    def get_end_moment(self, delta):
        return self.end_moment + delta

    # 获取后面可经过的时间区间（只获取最近2次）
    def get_next_time_interval(self, moment, delta):
        n = (moment - self.get_end_moment(delta)) // self.period + 1
        yield [self.get_start_moment(delta) + n * self.period, self.get_end_moment(delta) + n * self.period]
        n += 1
        yield [self.get_start_moment(delta) + n * self.period, self.get_end_moment(delta) + n * self.period]

    # 获取等待时间
    def get_wait_time(self, moment, velocity, delta):
        for interval in self.get_next_time_interval(moment, delta):
            if moment <= interval[1] - self.edge.length / velocity:
                return max(moment, interval[0]) - moment


# 红绿灯修正值（所有红绿灯的时间都要加这个数）
class TrafficLightDelta(BaseModel, table=True):
    __tablename__ = "traffic_light_deltas"
    delta: int

    # 今日是否校准
    @property
    def is_today_updated(self):
        now = datetime.now()
        updated_at = self.updated_at
        return now.year == updated_at.year and now.month == updated_at.month and now.day == updated_at.day

# 图
class Graph(BaseModel, table=True):
    __tablename__ = "graphs"
    name: str
    start_node_id: int
    end_node_id: int
    nodes: List["Node"] = Relationship(
        back_populates="graph",
        sa_relationship_kwargs={
            "primaryjoin": "Graph.id == foreign(Node.graph_id)"
        }
    )
    edges: List["Edge"] = Relationship(
        back_populates="graph",
        sa_relationship_kwargs={
            "primaryjoin": "Graph.id == foreign(Edge.graph_id)"
        }
    )

    def to_json(self):
        nodes = [node.to_dict() for node in self.nodes]
        edges = [edge.to_dict() for edge in self.edges]
        return {
            "id": self.id,
            "name": self.name,
            "start_node_id": self.start_node_id,
            "end_node_id": self.end_node_id,
            "nodes": nodes,
            "edges": edges
        }

    # 图的邻接表表示
    def adjacency_list(self):
        results = defaultdict(list)
        for edge in self.edges:
            results[edge.start_node_id].append(edge)
        return results
