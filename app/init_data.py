from sqlmodel import Session, SQLModel, select

from app.models.graph_model import Graph, Node, Edge, TrafficLight
from app.db.session import engine

coordinates = [
    [121.480981, 31.228522],
    [121.481535, 31.228795],
    [121.481575, 31.228818],
    [121.482265, 31.229156],
    [121.482306, 31.229178],
    [121.480241, 31.22946],
    [121.480787,31.229712],
    [121.480837,31.22974],
    [121.481581, 31.230151],
    [121.481631, 31.230178],
    [121.480053, 31.229736],
    [121.481382, 31.230493],
    [121.481438, 31.230521],
]

edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [5, 6],
    [6, 7],
    [7, 8],
    [8, 9],
    [10, 11],
    [11, 12],
    [0, 5],
    [1, 6],
    [2, 7],
    [3, 8],
    [4, 9],
    [5, 10],
    [8, 11],
    [9, 12]
]

traffic_lights = [
    [15, 190, 53, 156],
    [7, 190, 116, 0],
    [9, 190, 116, 0],
    [16, 190, 74, 116],
    [17, 190, 74, 116],
]

def create_data():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        graph = Graph(name='大世界上班', start_node_id=0, end_node_id=12)
        session.add(graph)
        session.commit()
        graph_id = graph.id
        for index, coordinate in enumerate(coordinates):
            node = Node(id=index, graph_id=graph_id, lat=coordinate[1], lng=coordinate[0])
            session.add(node)
        session.commit()
        for index, edge in enumerate(edges):
            e = Edge(id=index, graph_id=graph_id, start_node_id=edge[0], end_node_id=edge[1])
            session.add(e)
        session.commit()
        for edge in session.exec(select(Edge)).all():
            edge.set_length()
            session.add(edge)
            session.commit()
        for traffic_light in traffic_lights:
            traffic_light = TrafficLight(
                edge_id=traffic_light[0],
                period=traffic_light[1],
                pass_interval=traffic_light[2],
                start_moment=traffic_light[3],
            )
            session.add(traffic_light)
        session.commit()

create_data()
