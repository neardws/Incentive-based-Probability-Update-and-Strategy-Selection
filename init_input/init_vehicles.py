#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   init_vehicles.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/28 下午3:10   neardws      1.0         None
"""
from config.config import settings
import random
import pandas as pd


def get_vehicle_trace():
    """输出实验选择时间段内的车辆轨迹
    :argument
        fill_xy_csv_name        车辆轨迹数据CSV文件, string
        experiment_start_time   实验开始时间, int
        experiment_last_time    实验持续时间, int
    :return:
        experiment_df           时间段内车辆轨迹，DataFrame
    """
    df = pd.read_csv(settings.fill_xy_csv_name)
    start_df = df[(df["time"] >= settings.experiment_start_time)]
    experiment_df = start_df[(start_df["time"] <= settings.experiment_start_time + settings.experiment_last_time - 1)]
    return experiment_df


def get_vehicle_id():
    """得到轨迹数据中所有车辆ID
    :argument
        df                  时间段内车辆轨迹，DataFrame
    :return
        vehicle_id_list     时间段内车辆ID, List
    """
    df = get_vehicle_trace()
    vehicle_id_list = df["id"].drop_duplicates().tolist()
    return vehicle_id_list


def get_edge_vehicle_id():
    """从所有车辆ID中随机选择一些车辆作为边缘节点, 边缘节点在所有时间内都出现
    :argument:
        edge_vehicle_num    边缘车辆节点数量, int
        experiment_start_time   实验开始时间, int
        experiment_last_time    实验持续时间, int
    :return
        edge_vehicle_id     边缘车辆节点ID, List
    :raise:
        ValueError("from init_vehicles.get_edge_vehicle_id() 满足条件的边缘节点车辆数量少于需求数量")
    """
    time_id_set = []
    for i in range(settings.experiment_start_time, settings.experiment_start_time + settings.experiment_last_time):
        time_df = get_vehicle_trace_in_time(i)
        time_id = set(time_df["id"].drop_duplicates().tolist())
        time_id_set.append(time_id)
    intersection_id_set = time_id_set[0]
    for id_set in time_id_set:
        intersection_id_set = intersection_id_set & id_set
    id = list(intersection_id_set)
    # print("----------------------------------------------------------")
    # print(id)
    # print("----------------------------------------------------------")
    if len(id) >= settings.edge_vehicle_num:
        edge_vehicle_id = random.sample(id, settings.edge_vehicle_num)
        return edge_vehicle_id
    else:
        raise ValueError("from init_vehicles.get_edge_vehicle_id() 满足条件的边缘节点车辆数量少于需求数量")


def get_customer_vehicle_id(edge_vehicle_id, id):
    """所有车辆ID中除去边缘车辆节点ID的 其他ID 作为普通客户车辆的ID, 普通客户车辆会生成数据传输任务
    :argument
        id                  时间段内所有车ID, List
        edge_vehicle_id     边缘车辆节点ID, List
    :return
        customer_vehicles_id 客户车辆节点ID, List
    """
    customer_vehicles_id = []
    for vehicle_id in id:
        if vehicle_id in edge_vehicle_id:
            pass
        else:
            customer_vehicles_id.append(vehicle_id)
    return customer_vehicles_id


def get_vehicle_location(vehicle_id, time):
    """根据车辆ID找到某一时间的车辆位置
    :argument
        vehicle_id  车辆ID, int
        time        时间， int
    :return
        x           车辆位置 x, double or float
        y           车辆位置 y, double or float
    OR
        None        当车辆在time 时没有出现时
    """
    df = get_vehicle_trace()
    vehicle_df = df[(df["id"] == vehicle_id)]
    if time in vehicle_df["time"].tolist():
        time_df = vehicle_df[(vehicle_df["time"] == time)]
        # get_vehicle_locationprint(time_df)
        x = float(time_df["x"])
        y = float(time_df["y"])
        # print("----------------------------------------------------------")
        # print(int(time_df["id"]), int(time_df["time"]), float(time_df["x"]), float(time_df["y"]))
        # print("----------------------------------------------------------")
        return x, y
    else:
        return


def get_vehicle_trace_in_time(time):
    """根据时刻time 得到时间time上所有车辆位置, 该数据可用于得到每个时间片上客户车辆的位置
    :argument
        time        时间，int
        df          时间段内车辆轨迹，DataFrame
    :return
        time_df     车辆位置数据，DataFrame
    """
    df = get_vehicle_trace()
    time_df = df[(df["time"] == time)]
    return time_df


if __name__ == '__main__':
    print("*" * 32)
    print("Vehicle Trace")
    print(get_vehicle_trace())
    df = get_vehicle_trace()
    id = get_vehicle_id()
    print("*" * 32)
    print("Vehicle ID")
    print(id)
    print(type(id))
    edge_id = get_edge_vehicle_id()
    customer_id = get_customer_vehicle_id(edge_id, id)
    print("*" * 32)
    print("Edge Vehicle ID")
    print(edge_id)
    print(type(edge_id))
    print("*" * 32)
    print("Customer Vehicle ID")
    print(customer_id)
    print(type(customer_id))
    print("*" * 32)
    print("Time Vehicle Trace")
    time_trace = get_vehicle_trace_in_time(2)
    print(time_trace)
    print(type(time_trace))
    print("Time Vehicle Location")
    time_location = get_vehicle_location(2, 2)
    print(time_location)
    print(time_location[0], time_location[1])
    print(type(time_location))
