from app.models.graph_model import Graph
from app.schemas.graph_schema import FastestPathResponse, FastestPathItem, EdgeSchema


class FastestPath:
    def __init__(self, graph: Graph):
        self.graph = graph

    def find_fastest_path(self, moment: float, velocity: float, delta: float) -> FastestPathResponse:
        """
        计算从起点到终点的最快路径
        :param moment: 出发时刻
        :param velocity: 速度
        :param delta: 红绿灯偏移量
        :return:
        """
        # 总花费时间
        all_take_time = 0
        # 总等待时间
        all_wait_time = 0
        # 某个点有没有访问
        visited_dict = {node.id: False for node in self.graph.nodes}
        # 起点到每个点的最短花费时间
        minimum_duration_dict = {node.id: float('inf') for node in self.graph.nodes}
        minimum_duration_dict[self.graph.start_node_id] = 0
        # 前驱节点
        prev_dict = {}
        # 每个节点到达时刻
        arrive_moment_dict = {self.graph.start_node_id: moment}
        wait_times = {}
        adjacency_list = self.graph.adjacency_list()
        while True:
            # 在没有访问的节点中，找出花费时间最短的节点
            not_visited = [[node_id, duration] for node_id, duration in minimum_duration_dict.items() if
                           not visited_dict[node_id]]
            if not not_visited:
                break
            min_node_id = min(not_visited, key=lambda x: x[1])[0]
            visited_dict[min_node_id] = True
            for edge in adjacency_list[min_node_id]:
                if not visited_dict[edge.end_node_id]:
                    traffic_light = edge.traffic_light
                    wait_time = traffic_light.get_wait_time(arrive_moment_dict[min_node_id], velocity,
                                                            delta) if traffic_light else 0
                    new_duration = minimum_duration_dict[min_node_id] + wait_time + edge.length / velocity
                    if new_duration < minimum_duration_dict[edge.end_node_id]:
                        minimum_duration_dict[edge.end_node_id] = new_duration
                        arrive_moment_dict[edge.end_node_id] = arrive_moment_dict[
                                                                   min_node_id] + wait_time + edge.length / velocity
                        prev_dict[edge.end_node_id] = edge
                        wait_times[edge.start_node_id] = wait_time
        node_id = self.graph.end_node_id
        path_edges = []
        while node_id != self.graph.start_node_id:
            edge = prev_dict[node_id]
            path_edges.append(FastestPathItem(edge=EdgeSchema.from_orm(edge), velocity=velocity, wait_time=wait_times[edge.start_node_id]))
            node_id = edge.start_node_id
            all_wait_time += wait_times[edge.start_node_id]
            all_take_time += wait_times[edge.start_node_id] + edge.length / velocity
        path_edges.reverse()
        return FastestPathResponse(
            paths=path_edges,
            all_take_time=all_take_time,
            all_wait_time=all_wait_time
        )
