import sys

import pandas
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from settings.Anylogic_related_settings import Anylogic_related_settings


def del_files(path):
    """delete all files in the given path."""
    ls = os.listdir(path)
    for i in ls:
        f_path = os.path.join(path, i)
        if os.path.isdir(f_path):
            del_files(f_path)
        else:
            os.remove(f_path)


def Anylogic_output_csv_process(csv_file_path1, csv_file_name1, csv_file_path2, csv_file_name2,
                                 v_info_file, v_info_sheet, day_num, store_path):
    """This function aims to process the output .csv file from Anylogic model.
    :param str csv_file_path1: The .csv file of original Anylogic program, which contains Anylogic model's running result,
    :param str csv_file_name1: the .csv file of original Anylogic program name,
    :param str csv_file_path2: The .csv file of new Anylogic program, which contains Anylogic model's running result,
    :param str csv_file_name2: the .csv file of new Anylogic program name,
    :param str v_info_file: the .xlsx file, containing the vehicle information,
    :param str v_info_sheet: the .xlsx sheet name,
    :param int day_num: the number of the record days, (how many of the days you want to process),
    :param str store_path: the output .jpg files' store path.
    """

    def time_anchor_2_continuous_data(list_input, full_capacity_v):
        """This function converts a 2D list of unknown length with time anchor data into a continuous data list."""

        # create a standard continuous 1D data list with time data from 08:00-24:00, total 960 minutes
        rst = [0] * 960

        def write_data(list_1D, idx1, idx2, data):
            """Write data to 1D list element from idx1 to idx2"""
            idx = idx1
            while idx < idx2:
                list_1D[idx] = data
                idx += 1
            return list_1D

        for num in range(len(list_input) - 1):
            rst = write_data(rst, list_input[num][0], list_input[num + 1][0], list_input[num][1])

        # write the last part of result, from input list[-1] to result[-1]
        rst = write_data(rst, list_input[-1][0], len(rst), list_input[-1][1])

        rst = [rst[i] - full_capacity_v for i in range(len(rst))]
        return rst

    # check if the file exists or not
    if os.path.exists(csv_file_path1 + csv_file_name1):
        pass
    else:
        print("Original Anylogic Model output file does not exist. Please check and retry.")
        raise FileNotFoundError
    if os.path.exists(csv_file_path2 + csv_file_name2):
        pass
    else:
        print("New Anylogic Model output file does not exist. Please check and retry.")
        raise FileNotFoundError
    if os.path.exists(v_info_file):
        pass
    else:
        print("Vehicle information file does not exist. Please check and retry.")
        raise FileNotFoundError

    # Check the size of two .csv files. They should not be empty.
    if os.path.getsize(csv_file_path1 + csv_file_name1) < 60 or os.path.getsize(csv_file_path2 + csv_file_name2) < 60:
        print('Seems one of the .csv file is empty. Please check and retry.')
        raise FileNotFoundError

    # read the data from two .csv files
    csv_org = pandas.read_csv(csv_file_path1 + csv_file_name1)
    csv_new = pandas.read_csv(csv_file_path2 + csv_file_name2)

    # read the vehicle information from.xlsx file data
    v_info = pandas.read_excel(v_info_file, sheet_name=v_info_sheet)

    # Please note: because of the different system region and format settings, there could be a format problem in
    # the Anylogic output .csv file: the pandas could have recognition errors.
    # In such case, a manually check before running this process program is necessary.

    # fix the problem that some records in .csv file have only even minute records
    for record_row in range(len(csv_org)-1):
        if csv_org.values[record_row][0] == csv_org.values[record_row + 1][0]:
            if csv_org.values[record_row][1] == csv_org.values[record_row + 1][1]:
                if csv_org.values[record_row][2] == csv_org.values[record_row + 1][2]:
                    if csv_org.values[record_row][3] == csv_org.values[record_row + 1][3]:
                        csv_org.iloc[record_row+1, 3] = csv_org.values[record_row + 1][3] + 1

    for record_row in range(len(csv_new)-1):
        if csv_new.values[record_row][0] == csv_new.values[record_row + 1][0]:
            if csv_new.values[record_row][1] == csv_new.values[record_row + 1][1]:
                if csv_new.values[record_row][2] == csv_new.values[record_row + 1][2]:
                    if csv_new.values[record_row][3] == csv_new.values[record_row + 1][3]:
                        csv_new.iloc[record_row+1, 3] = csv_new.values[record_row + 1][3] + 1

    # cal the whole capacity of the transport fleet, unit in ton
    whole_capacity = 0
    for v_row in range(len(v_info)):
        whole_capacity += (v_info.values[v_row][1] * v_info.values[v_row][2])

    # split the csv file with its day
    csv_org_day_group = csv_org.groupby(csv_org.columns[1])
    csv_new_day_group = csv_new.groupby(csv_new.columns[1])

    # for every day, every different kinds of vehicle's record
    # only deal with the first 10 days
    org_data = []
    new_data = []
    for day in range(day_num):

        # create a list containing this day's time-remaining capacity relationship, unit in ton
        day_remain_cap_org = [whole_capacity] * 960  # from 8:00-24:00
        day_remain_cap_new = [whole_capacity] * 960  # from 8:00-24:00

        # consider the situation that in one day, no truck is assigned, thus no record for that day
        if (day + 1) in csv_org_day_group.groups and (day + 1) in csv_new_day_group.groups:

            # split the day's records according to vehicle ID
            csv_org_day_group_id_group = csv_org_day_group.get_group(day + 1).groupby('id')
            csv_new_day_group_id_group = csv_new_day_group.get_group(day + 1).groupby('id')

            # active vehicle number for that day
            org_v_active = len(list(csv_org_day_group_id_group.groups.keys()))
            new_v_active = len(list(csv_new_day_group_id_group.groups.keys()))

            # (the original file) for every vehicle, which is in use in that day, generates its capacity changeset
            for v_id_org in range(org_v_active):
                list0 = csv_org_day_group_id_group.get_group(list(csv_org_day_group_id_group.groups.keys())[v_id_org])

                # this vehicle's capacity
                cap = float(list0.values[0][0].split('_')[1])

                # create a 2D list to store the change-sheet of this vehicle
                list_2D = []
                for rcd_num in range(len(list0)):

                    # set time unit as minute counts: 08:00 -> 0, 08:20 -> 20, 12:20 -> 260, 16:30 -> 510,
                    # no more than 960
                    # others can be deduced in this way
                    list_2D.append(((list0.values[rcd_num][2]-8)*60+list0.values[rcd_num][3], list0.values[rcd_num][6]))

                # add an init record, in case some vehicle does not have a (time=0800, free_capacity=cap) record
                # and thus cause undesired questions
                if list_2D[0][0] != 0:
                    list_2D.insert(0, (0, cap))

                v_remain_cap = time_anchor_2_continuous_data(list_2D, cap)
                day_remain_cap_org = [day_remain_cap_org[i] + v_remain_cap[i] for i in range(len(day_remain_cap_org))]

            # (the new file) for every vehicle, which is in use in that day, generates its capacity changeset
            for v_id_new in range(new_v_active):
                list0 = csv_new_day_group_id_group.get_group(list(csv_new_day_group_id_group.groups.keys())[v_id_new])

                # this vehicle's capacity
                cap = float(list0.values[0][0].split('_')[1])

                # create a 2D list to store the change-sheet of this vehicle
                list_2D = []
                for rcd_num in range(len(list0)):
                    # set time unit as minute counts: 08:00 -> 0, 08:20 -> 20, 12:20 -> 260, 16:30 -> 510,
                    # no more than 960
                    # others can be deduced in this way
                    list_2D.append(
                        ((list0.values[rcd_num][2] - 8) * 60 + list0.values[rcd_num][3], list0.values[rcd_num][6]))

                # add an init record, in case some vehicle does not have a (time=0800, free_capacity=cap) record
                # and thus cause undesired questions
                if list_2D[0][0] != 0:
                    list_2D.insert(0, (0, cap))

                v_remain_cap = time_anchor_2_continuous_data(list_2D, cap)
                day_remain_cap_new = [day_remain_cap_new[i] + v_remain_cap[i] for i in range(len(day_remain_cap_new))]

        elif (day + 1) in csv_org_day_group.groups or (day + 1) in csv_new_day_group.groups:
            # here just assume the situation
            # that no record for a specific day should not occur only for one Anylogic-program.
            pass

        else:
            # the situation that one day's record is not available for both .csv results
            # in such case, no adjustments need to be made here.
            # the day_remain_cap_org and day_remain_cap_new should remain the whole capacity of the fleet
            pass

        # write this day's original program data into org_data
        org_data.append(day_remain_cap_org)

        # write this day's new program data into new_data
        new_data.append(day_remain_cap_new)

    # try to find a minute slot, after which, all vehicles are back to the logistic center every day
    # and then cut the data from that minute

    threshold_minute_temp = 0  # default minute threshold as the last element in the list
    for j in range(len(new_data)):
        for r in reversed(range(960)):  # from last element to the front
            if new_data[j][r] != whole_capacity or org_data[j][r] != whole_capacity:
                if r > threshold_minute_temp:
                    threshold_minute_temp = r
                break

    threshold_minute = threshold_minute_temp

    # split the new_data and org_data, and discard the values after threshold_minute point
    for j in range(len(new_data)):
        del new_data[j][(threshold_minute+2):]
        del org_data[j][(threshold_minute+2):]

    length_data = len(new_data[0])  # the data length

    # create plot relevant values: x_ax as minutes from 08:00;
    # new_data_pct, org_data_pct as the percentages of the whole fleet's utilization rate
    x_ax = list(range(length_data))
    new_data_pct = [[1] * length_data for i in range(day_num)]  # use the same format to init
    org_data_pct = [[1] * length_data for i in range(day_num)]  # use the same format to init
    for i in range(len(org_data)):
        for j in range(len(org_data[i])):
            new_data_pct[i][j] = new_data[i][j] / whole_capacity
            org_data_pct[i][j] = org_data[i][j] / whole_capacity

    # set a public y-axis limitation to make all subplots have the same scaling ratio
    min_pct = 1
    for i in range(len(org_data)):
        min_pct_temp = min(min(new_data_pct[i]), min(org_data_pct[i]))
        if min_pct_temp < min_pct:
            min_pct = min_pct_temp
    if min_pct >= 0.02:
        min_pct = min_pct - 0.02
    elif min_pct >= 0:
        pass
    else:
        print('There should be some error in the data or the processing program. Please check.')

    # the needed parameter for the average data over days
    new_data_pct_avg = [1] * length_data  # use the same length as init
    org_data_pct_avg = [1] * length_data  # use the same length as init

    for i in range(length_data):

        new_data_sum_temp = 0
        org_data_sum_temp = 0

        for day in range(day_num):
            new_data_sum_temp += new_data_pct[day][i]
            org_data_sum_temp += org_data_pct[day][i]

        new_data_pct_avg[i] = new_data_sum_temp / day_num
        org_data_pct_avg[i] = org_data_sum_temp / day_num
    del new_data_sum_temp, org_data_sum_temp

    # clear the graphs' store path
    del_files(store_path)

    # generate the graphs for every day
    for day in range(day_num):
        save_str = f'savefig_day_{str(day + 1)}.png'

        # plt.plot(x_ax, org_data_pct[day], c='b', ls='-', lw=2)
        # plt.plot(x_ax, new_data_pct[day], c='b', ls='-', lw=2)
        # plt.ylim(min_pct, 1.02)

        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())

        plt.plot(x_ax, [org_data_pct[day][i] * 100 for i in range(len(org_data_pct[day]))], c='r', ls='-', lw=2)
        plt.plot(x_ax, [new_data_pct[day][i] * 100 for i in range(len(new_data_pct[day]))], c='b', ls='-', lw=2)
        plt.plot(x_ax, [org_data_pct_avg[i] * 100 for i in range(len(org_data_pct_avg))], c='r', ls='--', lw=1)
        plt.plot(x_ax, [new_data_pct_avg[i] * 100 for i in range(len(new_data_pct_avg))], c='b', ls='--', lw=1)
        plt.ylim(min_pct * 100, 102)

        plt.legend(["anfängliche Methode ohne Warennachfrage",
                    "neue Methode mit Warennachfrage",
                    "durchschnittlicher Prozentsatz der anfänglichen Methode",
                    "durchschnittlicher Prozentsatz der neuen Methode"], loc="lower left", prop={'size': 5})

        plt.xlabel('Zeit / Minuten (seit 08:00)', fontsize=8)
        plt.ylabel('Prozentsatz', fontsize=8)
        plt.title(f'Leerlaufquote der Transportflotte für Tag {day + 1}')
        plt.grid()

        plt.savefig(store_path + save_str,
                    dpi=300, bbox_inches='tight')
        plt.close()

    print('Process program ends here. Graphs exported to the specified folder.')


if __name__ == '__main__':

    config = Anylogic_related_settings

    # how many days do you want to process and generate the result?
    # Noted: the two .csv files must contain such information!
    # Please check the .csv file before you type in this parameter.
    day_num = 6

    # the result graphs' store path, needs to be an empty path, because in the program, it will be cleared first.
    store_path = 'C:/Users/86781/PycharmProjects/graphs/'

    # test code
    Anylogic_output_csv_process(config.csv_org_result_path, config.csv_org_result_name,
                                config.csv_new_result_path, config.csv_new_result_name,
                                config.v_info_file_new, config.v_info_file_sheet,
                                day_num, store_path)
    print('-------------------------------------------------------------------------------------------------')
    sys.exit()
