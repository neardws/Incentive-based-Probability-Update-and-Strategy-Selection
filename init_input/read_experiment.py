#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   read_experiment.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 下午3:56   neardws      1.0         None
"""
from init_input.experiment_input_save_and_reload import load_pickle
from pathlib import Path
import pickle

from init_input.init_distance import get_task_time_limitation_under_edge_node, get_task_id_under_edge_node


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


if __name__ == '__main__':
    pickle_file = Path(load_pickle(1))
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