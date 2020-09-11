#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   get_results.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/5/20 10:04 上午   neardws      1.0         None
"""
import json

from config.config import settings


if __name__ == '__main__':
    node_num_list = [15, 15, 15, 17, 16]
    experiment_median = [9, 11, 12, 13, 15]

    only_result_json_files = [settings.RESULT_FILE_VER2_9,
                              settings.RESULT_FILE_VER2_11,
                              settings.RESULT_FILE_VER2_12,
                              settings.RESULT_FILE_VER2_13,
                              settings.RESULT_FILE_VER2_15]

    for experiment_median_no, only_result_json_file in enumerate(only_result_json_files):

        ipus_results = []

        json_file = open(only_result_json_file, "r")
        lines = json_file.readlines()
        last_line = lines[-1]
        json_object = json.loads(str(last_line))
        iteration = json_object["iteration"]
        strategy_selection_probability_dict_list = json_object["strategy_selection_probability_dict_list"]
        json_file.close()
        # 得到所有策略可能性
        print(strategy_selection_probability_dict_list)
        print("\n")
        # strategy_no_dict = dict()
        # for i, strategy_selection_probability_dict in enumerate(strategy_selection_probability_dict_list):
        #     if strategy_selection_probability_dict:
        #         strategy_no_dict[i] = list(strategy_selection_probability_dict.keys())
