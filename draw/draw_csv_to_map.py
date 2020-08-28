#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   draw_csv_to_map.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/7/29 下午4:07   neardws      1.0         None
"""
import pandas as pd
import matplotlib.pyplot as plot
from config.config import settings


def main():
    df = pd.read_csv(settings.fill_xy_csv_name)
    x_max = df['x'].max()
    y_max = df['y'].max()
    plot.xlim(0, x_max)
    plot.ylim(0, y_max)

    chunk_size = 100000
    for chunk in pd.read_csv(settings.fill_xy_csv_name, error_bad_lines=False, chunksize=chunk_size):
        colors = ['r', 'g', 'c', 'b', 'y', 'k']
        trace_id = chunk['id'].drop_duplicates()
        for id in trace_id:
            trace = chunk[
                (chunk['id'] == id)]
            if len(trace):
                x = trace['x']
                y = trace['y']
                plot.scatter(x, y, 0.1, colors[id % 6])
                print(id)
    plot.show()


if __name__ == '__main__':
    main()