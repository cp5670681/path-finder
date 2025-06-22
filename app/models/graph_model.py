import math
from collections import defaultdict
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from app.models.base_model import BaseModel


# 节点
class Node(BaseModel, table=True):
    __tablename__ = "nodes"
    graph_id: int = Field(foreign_key="graphs.id")
    # 经度
    lng: float
    # 纬度
    lat: float
    graph: "Graph" = Relationship(back_populates="nodes")

    @property
    def label(self):
        return f"node-{self.id}"

    def to_dict(self):
        return {"id": self.id, "lng": self.lng, "lat": self.lat}


# 边
class Edge(BaseModel, table=True):
    __tablename__ = "edges"
    graph_id: int = Field(foreign_key="graphs.id")
    # 边的起点
    start_node_id: int = Field(foreign_key="nodes.id")
    # 边的终点
    end_node_id: int = Field(foreign_key="nodes.id")
    # 边的长度
    length: float = Field(default=0)
    start_node: "Node" = Relationship(
        # back_populates="start_edges",
        sa_relationship_kwargs={"foreign_keys": "Edge.start_node_id"}
    )
    end_node: "Node" = Relationship(
        # back_populates="end_edges",
        sa_relationship_kwargs={"foreign_keys": "Edge.end_node_id"}
    )
    graph: "Graph" = Relationship(back_populates="edges")
    traffic_light: "TrafficLight" = Relationship(back_populates="edge")

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
    edge_id: int = Field(foreign_key="edges.id")
    # 周期
    period: int
    # 通过的间隔
    pass_interval: int
    # 通过开始时刻
    start_moment: int

    edge: "Edge" = Relationship(
        back_populates="traffic_light",
        sa_relationship_kwargs={"foreign_keys": "TrafficLight.edge_id"}
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

# 图
class Graph(BaseModel, table=True):
    __tablename__ = "graphs"
    name: str
    start_node_id: int
    end_node_id: int
    nodes: List["Node"] = Relationship(back_populates="graph")
    edges: List["Edge"] = Relationship(back_populates="graph")

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


    def dijkstra(self, moment, velocity, delta):
        # 总花费时间
        all_take_time = 0
        # 总等待时间
        all_wait_time = 0
        # 某个点有没有访问
        visited_dict = {node.id: False for node in self.nodes}
        # 起点到每个点的最短花费时间
        minimum_duration_dict = {node.id: float('inf') for node in self.nodes}
        minimum_duration_dict[self.start_node_id] = 0
        # 前驱节点
        prev_dict = {}
        # 每个节点到达时刻
        arrive_moment_dict = {self.start_node_id: moment}
        wait_times = {}
        adjacency_list = self.adjacency_list()
        while True:
            # 在没有访问的节点中，找出花费时间最短的节点
            not_visited = [[node_id, duration] for node_id, duration in minimum_duration_dict.items() if not visited_dict[node_id]]
            if not not_visited:
                break
            min_node_id = min(not_visited, key=lambda x: x[1])[0]
            visited_dict[min_node_id] = True
            for edge in adjacency_list[min_node_id]:
                if not visited_dict[edge.end_node_id]:
                    traffic_light = edge.traffic_light
                    wait_time = traffic_light.get_wait_time(arrive_moment_dict[min_node_id], velocity, delta) if traffic_light else 0
                    new_duration = minimum_duration_dict[min_node_id] + wait_time + edge.length / velocity
                    if new_duration < minimum_duration_dict[edge.end_node_id]:
                        minimum_duration_dict[edge.end_node_id] = new_duration
                        arrive_moment_dict[edge.end_node_id] = arrive_moment_dict[min_node_id] + wait_time + edge.length / velocity
                        prev_dict[edge.end_node_id] = edge
                        wait_times[edge.start_node_id] = wait_time
        node_id = self.end_node_id
        path_edges = []
        while node_id != self.start_node_id:
            edge = prev_dict[node_id]
            path_edges.append({
                **edge.to_dict(),
                "wait_time": wait_times[edge.start_node_id],
                "duration": edge.length / velocity
            })
            node_id = edge.start_node_id
            all_wait_time += wait_times[edge.start_node_id]
            all_take_time += wait_times[edge.start_node_id] + edge.length / velocity
        path_edges.reverse()
        return [path_edges, wait_times, all_wait_time, all_take_time]
