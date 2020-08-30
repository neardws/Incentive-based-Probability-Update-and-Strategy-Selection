#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   IPUSS.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 下午5:11   neardws      1.0         None
"""
from datetime import *
from init_input.experiment_input_save_and_reload import load_pickle
from pathlib import Path
import pickle
import numpy as np
from init_input.init_distance import get_task_time_limitation_under_edge_node, get_task_id_under_edge_node
from config.config import settings
import itertools
from tqdm import tqdm


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


def read_experiment():
    pickle_file = Path(load_pickle(2))
    with pickle_file.open("rb") as fp:
        fixed_edge_node = pickle.load(fp)
        print_to_console("fixed_edge_node", fixed_edge_node)

        edge_vehicle_node = pickle.load(fp)
        print_to_console("edge_vehicle_node", edge_vehicle_node)

        task_by_time_list = pickle.load(fp)
        print_to_console("task_by_time_list", task_by_time_list)

        fixed_distance_matrix_list = pickle.load(fp)
        print_to_console("fixed_distance_matrix_list", fixed_distance_matrix_list)

        mobile_distance_matrix_list = pickle.load(fp)
        print_to_console("mobile_distance_matrix_list", mobile_distance_matrix_list)

        task_id = get_task_id_under_edge_node(node_type="BaseStation",
                                              node_id=1,
                                              distance_matrix=fixed_distance_matrix_list[0])
        print_to_console("task_id", task_id)


        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(node_type="BaseStation",
                                                                                        node_id=1,
                                                                                        distance_matrix_list=fixed_distance_matrix_list,
                                                                                        task_list=task_by_time_list[0])

        print_to_console("task_time_limitation_under_edge_node", task_time_limitation_under_edge_node)


def init_useful_channel(node_type, node_id, fixed_edge_node, edge_vehicle_node):
    if node_type == "BaseStation":
        node = fixed_edge_node[node_id]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel":node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == "RSU":
        node = fixed_edge_node[node_id + settings.base_station_num]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == "Vehicle":
        node = edge_vehicle_node[node_id]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    else:
        raise ValueError("from IPUSS.init_userful_channel 节点类型出错， 不是指定类型")


def update_useful_channel(strategy, useful_channel):
    for i in range(len(useful_channel)):
        if strategy[i][0] != 0:
            channel_time = strategy[i][1]
            useful_channel["channel_status"][i] = channel_time


def get_usable_channel_list(useful_channel):
    # 下一个时间片，对其自减
    for i in range(len(useful_channel)):
        if useful_channel["channel_status"][i] != 0:
            useful_channel["channel_status"][i] -= 1

    usable_channel_list = []

    channel_status = useful_channel["channel_status"]
    node_channel = useful_channel["node_channel"]
    for i in range(len(useful_channel)):
        if channel_status[i] == 0:
            usable_channel_list.append(node_channel[i])

    return usable_channel_list


def generator_of_strategy_matrix(usable_channel_list, task_id_under_edge_node, task_time_limitation_under_edge_node):

    # x 轴，节点当前可用的信道
    x_length = len(usable_channel_list)

    # y 轴, 节点的所有任务数
    # task_id = get_task_id_under_edge_node(node_type=node_type,
    #                                       node_id=node_id,
    #                                       distance_matrix=distance_matrix_list[time])
    y_length = len(task_id_under_edge_node)

    # task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(node_type="BaseStation",
    #                                                                                 node_id=1,
    #                                                                                 distance_matrix_list=distance_matrix_list,
    #                                                                                 task_list=task_by_time_list[
    #                                                                                     time - 1])
    j_strategy_list = [np.zeros(2)]

    for j in range(y_length):
        for k in range(task_time_limitation_under_edge_node[j]):
            j_strategy = np.zeros(2)
            j_strategy[0] = j + 1
            j_strategy[1] = k + 1
            j_strategy_list.append(j_strategy)
    print(j_strategy_list)
    print(len(j_strategy_list))

    strategy_list = []
    for strategy in itertools.product(j_strategy_list, repeat=x_length):
        strategy_list.append(strategy)

    return strategy_list


def get_strategy(x_length, y_length, task_time_limitation_under_edge_node):
    strategy_list = []

    j_strategy_list = [np.zeros(2)]

    for j in tqdm(range(y_length)):
        for k in range(task_time_limitation_under_edge_node[j]):
            j_strategy = np.zeros(2)
            j_strategy[0] = j + 1
            j_strategy[1] = k + 1
            j_strategy_list.append(j_strategy)
    print(j_strategy_list)
    print(len(j_strategy_list))

    for strategy in tqdm(itertools.product(j_strategy_list, repeat=x_length)):
        strategy_list.append(strategy)

    return strategy_list


if __name__ == '__main__':
    # read_experiment()
    x_length = 5
    y_length = 4
    task_time_limitation_under_edge_node = [3, 2, 6, 2]
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    strategy_list = get_strategy(5, 4, task_time_limitation_under_edge_node)
    print(strategy_list[1])
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(len(strategy_list))
