#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   get_compara_evaluation.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/4/20 8:24 下午   neardws      1.0         None
"""
import random

from algorithm.random_selection import random_selection_strategy
from pathlib import Path
import pickle

from algorithm.water_filling import water_filling_selection
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from experiment_results.strategy_evaluation import common_get_evaluation

if __name__ == '__main__':

    node_num_list = [16, 15, 15, 17, 16]

    random_result_list = []
    water_filling_result_list = []

    for i, experiment_median_num in enumerate([9, 11, 12, 13, 15]):

        pickle_file = Path(load_experiment_median_from_pickle(experiment_median_num))
        fp = pickle_file.open("rb")
        iteration = pickle.load(fp)
        fixed_edge_node = pickle.load(fp)
        edge_vehicle_node = pickle.load(fp)
        fixed_distance_matrix = pickle.load(fp)
        mobile_distance_matrix = pickle.load(fp)
        task_list = pickle.load(fp)
        node_num_not_used = pickle.load(fp)
        fixed_node_num = pickle.load(fp)
        mobile_node_num = pickle.load(fp)
        max_potential_value = pickle.load(fp)
        useful_channel_under_node = pickle.load(fp)
        task_id_under_each_node_list = pickle.load(fp)
        usable_channel_of_all_nodes = pickle.load(fp)
        task_time_limitation_of_all_nodes = pickle.load(fp)
        combination_and_strategy_length_of_all_nodes = pickle.load(fp)

        combination_list = []
        for combination_and_strategy_length in combination_and_strategy_length_of_all_nodes:
            if combination_and_strategy_length is not None:
                combination_list.append(combination_and_strategy_length["combination_of_task_and_time"])
        print(combination_list)

        strategy_list = random_selection_strategy(combination_list, length=10)
        random_evaluation_result = common_get_evaluation(strategy_list, experiment_median_num, node_num_list[i])

        random_result_list.append(random_evaluation_result)

        new_random_strategy_list = random_selection_strategy(combination_list, length=10)
        water_filling_strategy_list = water_filling_selection(combination_list, 10,
                                experiment_median_num, node_num_list[i])
        water_filling_result = common_get_evaluation(water_filling_strategy_list, experiment_median_num, node_num_list[i])
        water_filling_result_list.append(water_filling_result)

    print(random_result_list)
    print(water_filling_result_list)
