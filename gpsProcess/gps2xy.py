#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   gps2xy.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/7/29 下午4:08   neardws      1.0         None
The objection is to obtain the converted UTM coordinates from WGS84 coordinates

utm usage
utm.from_latlon(latitude, longitude)
"""
import pandas as pd
import utm
from config.config import settings


def list_latlon_to_xy(list_latitude, list_longitude, base_latitude, base_longitude):
    """

    Args:
        list_latitude:
        list_longitude:
        base_latitude:
        base_longitude:

    Returns:

    """
    list_x = []
    list_y = []
    base_xy = utm.from_latlon(base_latitude, base_longitude)
    base_x = base_xy[0]
    base_y = base_xy[1]
    if len(list_latitude) == len(list_longitude):
        length = len(list_latitude)
        for i in range(length):
            xy_coordinate = utm.from_latlon(list_latitude[i], list_longitude[i])
            list_x.append(float(xy_coordinate[0]) - float(base_x))
            list_y.append(float(xy_coordinate[1]) - float(base_y))
            print(i)
    if len(list_x) == len(list_y):
        return list_x, list_y
    else:
        return None


def renew_csv():
    """

    """
    df = pd.read_csv(settings.csv_name)
    vehicle_id = df['id']
    time = df['time']
    latitude = df['latitude']
    longitude = df['longitude']
    print("read csv success")
    list_xy = list_latlon_to_xy(latitude, longitude, settings.base_latitude, settings.base_longitude)
    if list_xy:
        list_x = list_xy[0]
        list_y = list_xy[1]
        new_df = pd.DataFrame({'id': vehicle_id, 'time': time, 'x': list_x, 'y': list_y})
        new_df.to_csv(settings.xy_csv_name, index=False)


def fill_csv():
    """

    """
    df = pd.read_csv(settings.xy_csv_name)
    vehicle_id = df['id']
    time = df['time']
    x = df['x']
    y = df['y']

    # list_to_save_filled_csv
    list_vehicle_id = []
    list_time = []
    list_x = []
    list_y = []

    # init values
    base_vehicle_id = vehicle_id[0]
    base_time = time[0]
    base_x = x[0]
    base_y = y[0]

    for i in range(len(vehicle_id)):
        print(i)
        # add no.i point
        list_vehicle_id.append(base_vehicle_id)
        list_time.append(base_time)
        list_x.append(base_x)
        list_y.append(base_y)

        if i < (len(vehicle_id) - 1):
            # fill data to 1Hz
            if vehicle_id[i + 1] == vehicle_id[i]:
                if time[i + 1] == time[i]:
                    continue
                else:
                    time_difference = time[i + 1] - base_time
                    x_difference = (x[i + 1] - base_x) / time_difference
                    y_difference = (y[i + 1] - base_y) / time_difference
                    for j in range(1, time_difference):
                        list_vehicle_id.append(base_vehicle_id)
                        list_time.append(int(base_time) + j)
                        list_x.append(float(base_x) + float(x_difference) * j)
                        list_y.append(float(base_y) + float(y_difference) * j)

            # renew the base point
            base_vehicle_id = vehicle_id[i + 1]
            base_time = time[i + 1]
            base_x = x[i + 1]
            base_y = y[i + 1]

    new_df = pd.DataFrame({'id': list_vehicle_id, 'time': list_time, 'x': list_x, 'y': list_y})
    new_df.to_csv(settings.fill_xy_csv_name, index=False)


if __name__ == '__main__':
    renew_csv()
    fill_csv()
