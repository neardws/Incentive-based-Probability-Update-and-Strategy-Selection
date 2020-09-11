#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   converage_analytics.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/4/20 4:20 下午   neardws      1.0         None
"""
import json
import pandas as pd
from tqdm import tqdm
from config.config import settings


if __name__ == '__main__':

    one_list = []
    with open(settings.JSON_FILE_VER2_9, "r") as fp:
        for line in tqdm(fp):
            json_list = []
            json_object = json.loads(str(line))
            iteration = json_object["iteration"]
            finish_num = json_object["sum_max_potential_value"]
            potential_value_list = json_object["max_potential_value"]
            json_list.append(iteration)
            json_list.append(finish_num)
            for potential_value in potential_value_list:
                json_list.append(potential_value)
            one_list.append(json_list)
    df = pd.DataFrame(one_list)
    df.to_csv("one_list2.csv")