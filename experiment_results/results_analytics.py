#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   results_analytics.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/3/20 11:17 下午   neardws      1.0         None
"""
import json

import numpy as np
import pandas as pd

from config.config import settings


if __name__ == '__main__':


    # "iteration": iteration,
    # "finished": sum(finished),
    # "potential_value_list": list(potential_value_list),
    # "sum_max_potential_value": sum(max_potential_value),
    # "max_potential_value": list(max_potential_value),
    # "strategy_selection_probability_dict_list": list(strategy_selection_probability_dict_list)},
    """
    __________________________________________________________________________
    """
    # print("iteration          finished")
    # with open(json_file_name, "r") as json_file:
    #     line = json_file.readline()
    #     while line:
    #         json_object = json.loads(str(line))
    #         iteration = json_object["iteration"]
    #         finished = json_object["finished"]
    #         print(str(iteration) + "          "+ str(finished))
            # strategy_selection_probability_dict_list = json_object["strategy_selection_probability_dict_list"]

    """
    __________________________________________________________________________
    """
    # benefits = np.zeros((1000, 19))
    # 
    # print("iteration        finished       sum")
    # with open(settings.JSON_FILE_VER3, "r") as json_file:
    #     i = 0
    #     line = json_file.readline()
    #     while line:
    #         if i >= 0:
    #             try:
    #                 json_object = json.loads(str(line))
    #                 # print(json_object)
    #                 # if i == 1:
    #                 #     break
    #                 iteration = json_object["iteration"]
    #                 finished = json_object["finished_num"]
    #                 sum_max_potential_value = json_object["sum_max_potential_value"]
    #                 print(str(iteration) + "          " + str(finished) + "    " + str(sum_max_potential_value) + "   "
    #                       , end="")
    #                 benefits[i][0] = sum_max_potential_value
    #                 print("\n")
    #                 potential_value_list = json_object["potential_value_list"]
    #                 for potential_value in potential_value_list:
    #                     print(potential_value, end="  ")
    #                 print("  ", end="")
    # 
    #                 print("\n")
    #                 max_potential_value_list = json_object["max_potential_value"]
    #                 for j, max_potential in enumerate(max_potential_value_list):
    #                     print(max_potential, end="  ")
    #                     benefits[i][j+1] = max_potential
    #                 print("  ", end="")
    # 
    #                 strategy_selection_probability_dict_list = json_object["strategy_selection_probability_dict_list"]
    #                 for strategy_selection_probability_dict in strategy_selection_probability_dict_list:
    #                     print(strategy_selection_probability_dict, end="")
    #                     print("  ", end="")
    # 
    #                 print("\n")
    # 
    #                 # strategy = json_object["strategy"]
    #                 # for i in range(17):
    #                 #     print(strategy[str(i)], end="")
    #                 #     print("  ", end="")
    #                 # print("\n")
    # 
    #             except json.decoder.JSONDecodeError:
    #                 line = json_file.readline()
    #                 continue
    #         i += 1
    #         line = json_file.readline()
    # df = pd.DataFrame(benefits, columns=['sum_max_potential_value', '1', '2', '3', '4', '5', '6','7', '8', '9', '10',
    #                                      '11', '12', '13', '14', '15', '16', '17', '18'])
    # print(df)
    # df.to_csv("out.csv")
    # print("保存成功")
    
    csv = pd.read_csv("out.csv")
    csv.to_excel("out.xlsx")