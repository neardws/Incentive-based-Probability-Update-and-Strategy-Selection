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
from init_input.init_vehicles import get_vehicle_location, get_edge_vehicle_id


def generate_random_sub_channel(sub_channel_num, need_sub_channel):
    """从全部的子信道中随机选择出一些子信道
    :argument
        sub_channel_num     全部子信道数量, int
        need_sub_channel    所需子信道数量, int
    :return
        sub_channel         子信道， List
    """
    sub_channel = random.sample(range(sub_channel_num), need_sub_channel)
    return sub_channel


def get_sub_channel_transmission_power(transmission_power_max, channel_num):
    """根据子信道数量计算单个子信道上传输功率
    :argument:
        transmission_power_max  最大传输功率， int
        channel_num             子信道数量，int
    :return:
        sub_channel_transmission_power  信道传输功率
    """
    sub_channel_transmission_power = transmission_power_max / channel_num
    return sub_channel_transmission_power


def init_fixed_edge_node():
    """初始化所有固定边缘节点，包含了基站与RSU
    :return
        edge_node   固定边缘节点，list
    Example

    """
    fixed_edge_node = []
    for i in range(settings.base_station_num):
        base_station = {"id": i,
                        "x": settings.base_station_x[i],
                        "y": settings.base_station_y[i],
                        "radius": settings.base_station_communication_radius,
                        "channel_num": settings.base_station_sub_channel_num,
                        "sub_channel": generate_random_sub_channel(
                            sub_channel_num=settings.sub_channel_num,
                            need_sub_channel=settings.base_station_sub_channel_num),
                        "channel_power": get_sub_channel_transmission_power(
                            transmission_power_max=settings.base_station_transmission_power_max,
                            channel_num=settings.base_station_sub_channel_num)}
        fixed_edge_node.append(base_station)
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
        fixed_edge_node.append(rsu)
    return fixed_edge_node


def init_edge_vehicle_node(edge_vehicle_num, edge_vehicle_id):
    """初始化所有移动边缘节点
    :return
        edge_vehicles_node 移动边缘节点，List
    Example

    """
    edge_vehicles_node = []
    for i in range(edge_vehicle_num):
        x_list = []
        y_list = []
        for time in range(settings.experiment_start_time, settings.experiment_start_time + settings.experiment_last_time):
            vehicle_location = get_vehicle_location(vehicle_id=edge_vehicle_id[i],
                                                    time=time)
            x_list.append(vehicle_location[0])
            y_list.append(vehicle_location[1])
        edge_vehicle = {"vehicle_id": edge_vehicle_id,
                        "x_list": x_list,
                        "y_list": y_list,
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


if __name__ == '__main__':
    fixed_edge_node = init_fixed_edge_node()
    edge_vehicle_id = get_edge_vehicle_id()
    mobile_edge_node = init_edge_vehicle_node(edge_vehicle_num=settings.edge_vehicle_num,
                                              edge_vehicle_id=edge_vehicle_id)
    print("*" * 32)
    print("Fixed Edge Node")
    print(fixed_edge_node)
    print("*" * 32)
    print("Fixed Edge Node Example")
    print(fixed_edge_node[0])
    print("*" * 32)
    print("Edge Vehicle Id")
    print(edge_vehicle_id)
    print("*" * 32)
    print("Mobile Edge Node")
    print(mobile_edge_node)
    print("*" * 32)
    print("Mobile Edge Node Example")
    print(mobile_edge_node[0])
