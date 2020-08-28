#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   init_edge_node.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/28 下午2:35   neardws      1.0         None
"""
from config.config import settings
import random


def generate_random_sub_channel(sub_channel_num, need_sub_channel):
    return random.sample(range(sub_channel_num), need_sub_channel)


def get_sub_channel_transmission_power(transmission_power_max, channel_num):
    return transmission_power_max / channel_num


def init_edge_node():
    edge_node = []
    for i in range(settings.base_station_num):
        base_station = {"id": i,
                        "x": settings.base_station_x[i],
                        "y": settings.base_station_y[i],
                        "radius": settings.base_station_communication_radius,
                        "channel_num": settings.base_station_sub_channel_num,
                        "sub_channel": generate_random_sub_channel(
                            sub_channel_num=settings.sub_channel_num,
                            need_sub_channel=settings.base_station_sub_channal_num),
                        "channel_power": get_sub_channel_transmission_power(
                            transmission_power_max=settings.base_station_transmission_power_max,
                            channel_num=settings.base_station_sub_channel_num)}
        edge_node.append(base_station)
    for j in range(settings.rsu_num):
        rsu = {"id": settings.base_station_num + j,
               "x": settings.rsu_x[j],
               "y": settings.rsu_y[j],
               "radius": settings.rsu_communication_radius,
               "channel_num": settings.rsu_sub_channel_num,
               "sub_channel": generate_random_sub_channel(
                   sub_channel_num=settings.sub_channel_num,
                   need_sub_channel=settings.rsu_sub_channel_num),
               "channel_power": get_sub_channel_transmission_power(
                   transmission_power_max=settings.rsu_transmission_power_max,
                   channel_num=settings.rsu_sub_channel_num)}
        edge_node.append(rsu)
    return edge_node


def init_edge_vehicle_node(edge_vehicle_num, edge_vehicle_id, time):
    edge_vehicles_node = []
    for i in range(edge_vehicle_num):
        edge_vehicle = {"vehicle_id": edge_vehicle_id,
                        "x": settings.base_station_x[i],
                        "y": settings.base_station_y[i],
                        "radius": settings.edge_vehicle_communication_radius,
                        "channel_num": settings.edge_vehicle_sub_channel_num,
                        "sub_channel": generate_random_sub_channel(
                            sub_channel_num=settings.sub_channel_num,
                            need_sub_channel=settings.edge_vehicle_sub_channel_num),
                        "channel_power": get_sub_channel_transmission_power(
                            transmission_power_max=settings.edge_vehicle_transmission_power_max,
                            channel_num=settings.edge_vehicle_sub_channel_num)}
        edge_vehicles_node.append(edge_vehicle)
    return edge_vehicles_node
