#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   __init__.py.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/28 下午1:23   neardws      1.0         None
"""
from init_input.experiment_input_save_and_reload import save_pickle
from init_input.init_distance import get_fixed_distance_matrix, get_mobile_distance_matrix
from init_input.init_edge_node import init_fixed_edge_node, init_edge_vehicle_node
from config.config import settings
from init_input.init_task_by_time import init_task_by_time
from init_input.init_vehicles import get_edge_vehicle_id, get_customer_vehicle_id, get_vehicle_id
from tqdm import tqdm


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


def print_to_console(msg):
    print("*" * 32)
    print(msg)


if __name__ == '__main__':
    print_to_console("Start")

    fixed_edge_node = init_fixed_edge_node()

    edge_vehicle_id = get_edge_vehicle_id()
    edge_vehicle_node = init_edge_vehicle_node(edge_vehicle_num=settings.edge_vehicle_num,
                                               edge_vehicle_id=edge_vehicle_id)

    print_to_console("Edge Node Inited")

    vehicle_id = get_vehicle_id()
    customer_vehicle_id = get_customer_vehicle_id(edge_vehicle_id=edge_vehicle_id,
                                                  id=vehicle_id)

    experiment_start_time = settings.experiment_start_time
    experiment_end_time = settings.experiment_start_time + settings.experiment_last_time
    task_by_time_list = []
    fixed_distance_matrix_list = []
    mobile_distance_matrix_list = []

    for time in tqdm(range(experiment_start_time, experiment_end_time)):
        print_to_console("Processing task and distance matrix in time " + str(time))

        task_by_time = init_task_by_time(customer_vehicle_id=customer_vehicle_id,
                                         time=time)
        task_by_time_list.append(task_by_time)

        fixed_distance_matrix = get_fixed_distance_matrix(fixed_edge_node=fixed_edge_node,
                                                          task_list=task_by_time)
        fixed_distance_matrix_list.append(fixed_distance_matrix)

        mobile_distance_matrix = get_mobile_distance_matrix(time=time,
                                                            edge_vehicle_node=edge_vehicle_node,
                                                            task_list=task_by_time)
        mobile_distance_matrix_list.append(mobile_distance_matrix)

    if save_pickle(fixed_edge_node,
                edge_vehicle_node,
                task_by_time_list,
                fixed_distance_matrix_list,
                mobile_distance_matrix_list,
                ):
        print_to_console("实验设置配置存储成功")