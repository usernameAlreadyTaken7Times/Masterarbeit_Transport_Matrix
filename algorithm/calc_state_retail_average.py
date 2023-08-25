import numpy as np
from scipy.optimize import curve_fit
import matplotlib.axes as mae
import matplotlib.pyplot as plt
from IO.excel_input import load_excel


def get_state_num_from_state_name(state_name):
    # use the input state name to find a corresponding state index
    name = state_name
    state_num = -1

    # check if the input name is a string
    if not isinstance(name, str):
        print("Input type error. please use string instead.")
        return -1
    else:
        if name.lower() == "baden-württemberg" or name.lower() == "baden-wuerttemberg":
            state_num = 1
        elif name.lower() == "bayern":
            state_num = 2
        elif name.lower() == "berlin":
            state_num = 3
        elif name.lower() == "brandenburg":
            state_num = 4
        elif name.lower() == "bremen":
            state_num = 5
        elif name.lower() == "hamburg":
            state_num = 6
        elif name.lower() == "hessen":
            state_num = 7
        elif name.lower() == "mecklenburg-vorpommern":
            state_num = 8
        elif name.lower() == "niedersachsen":
            state_num = 9
        elif name.lower() == "nordrhein-westfalen":
            state_num = 10
        elif name.lower() == "rheinland-pfalz":
            state_num = 11
        elif name.lower() == "saarland":
            state_num = 12
        elif name.lower() == "sachsen":
            state_num = 13
        elif name.lower() == "sachsen-anhalt":
            state_num = 14
        elif name.lower() == "schleswig-holstein":
            state_num = 15
        elif name.lower() == "thüringen" or name.lower() == "thueringen":
            state_num = 16
        else:
            print("state name not match. please check your input.")
            state_num = -1

    return state_num


def get_retail_average(predict_year, predict_state,
                       BIP_filename='C:/Users/86781/PycharmProjects/pythonProject/data/BIP und Einkommen.xlsx',
                       BIP_filesheet='BIPhandel'):
    """This function is used to calculate the relationship between GDP of a german state and its population.
    Then use the input state name and year to predict the state's retail sale average amount (Euro/per person).
    Then in other scripts, this value can be used to multiply the predicted population in the chosen test area and
    get the retail amount for the area. To achieve the goal, an Excel file containing the relevant data is applied,
    and inside this funktion, several regression equations are needed for such process. First, init: read data from
    file and variables init, Second, curve fitting: try to use curve_fit function and preset functions f(x) to fit
    the data and third, forecast value acquiring: use the given year to output the predict retail amount and population
    of the chosen state and time.

    :param int predict_year: The year you want to predict, should between 2000-2025;
        for period of 2000-2007 and 2021-2025, use regression prediction;
        for period of 2008-2020, use historical data,
    :param str predict_state: the german state which you want to predict,
    :param str BIP_filename: the .xlsx file containing the BIP_handel, BIP_je_Person and Population data,
    :param str BIP_filesheet: the .xlsx file sheet containing the BIP_handel, BIP_je_Person and Population data,
    :return: the BIP_Handel je Person at the time point of the chosen year, chosen state, unit of measurement
     Euro/Person.
    """

    # para init
    year = predict_year
    state = predict_state
    retail_xlsx_filename = BIP_filename

    # BIP_handel is the GDP with german industry division standard 'WZ 2008', whole data of WZ08-45-47, expect only 47;
    # item 'Handel; Instandhaltung und Reparatur von Kraftfahrzeugen (G)'. The data is from 'www.statistikportal.de' and
    # shows the sale amount of 'Handel' in every state of Germany. However, the data is only available from 2008
    # to 2020, so the data of year 2021 and 2022 and before 2008 for other variables(BIP_je_Person, Einwohner) are
    # discarded.
    BIP_handel = load_excel(retail_xlsx_filename, BIP_filesheet)
    # BIP_handel data for state init
    BIP_handel_state = np.zeros(len(BIP_handel) - 5)

    # BIP_je_Person is the GDP in every state divides its population number. Likewise, the data is also from the
    # german statistics department. In this program, these values, together with the BIP_handel, can be used to
    # determine and predict the sale amount for a specific year.
    BIP_je_Person = load_excel(retail_xlsx_filename, 'BIPjePerson')
    # BIP_je_Person data for state init
    BIP_je_Person_state = np.zeros(len(BIP_handel) - 5)

    # the population of states in Germany
    Einwohner = load_excel(retail_xlsx_filename, 'Einwohnen')
    # BEinwohner data for state init
    Einwohner_state = np.zeros(len(BIP_handel) - 5)

    # year data init
    year_state = np.zeros(len(BIP_handel) - 5)

    # use an index to determine the state
    state_num = get_state_num_from_state_name(state)

    # Use a loop to read all relevant data of the chosen state.
    # These array indexes' numbers are based on the format of the original xlsx file containing the data,
    # which was directly copied from the website of Deutsche Statistiksamt, so the format could be a little messy.
    # Noted: because the BIP_handel's data in only available from 2014 to 2022, so all predictions are based on the
    # data in that period.
    for year_tmp in range(5, len(BIP_handel)):
        BIP_handel_state[year_tmp - 5] = float(BIP_handel.values[year_tmp][state_num])
        BIP_je_Person_state[year_tmp - 5] = float(BIP_je_Person.values[year_tmp + 17][state_num])
        Einwohner_state[year_tmp - 5] = float(Einwohner.values[year_tmp + 17][state_num])
        year_state[year_tmp - 5] = float(year_tmp + 2003)

    # set mode based on the input year
    mode = -1  # init mode

    # check if the input year in the chosen periods and set mode
    if isinstance(year, int):
        pass
    else:
        print('Input year format error. Please check your input year and then retry.')
        return 0

    # use prediction data for BIP_handel only,
    # while for BIP_je_Person and Einwohnen use historical data
    if 2000 <= year <= 2013:
        print(f'Input year is {str(year)}, using historical data from .csv file.')
        mode = 2

    # use historical data
    elif 2014 <= year <= 2022:
        print(f'Input year is {str(year)}, using historical data from .csv file.')
        mode = 0

    # # use prediction data for Einwohnen, historical data for BIP_handel
    # # update: this part should never be reached after altering the calculation method
    # elif 2021 <= year <= 2022:
    #     print(f'Input year is {str(year)}, using predication data from .csv file.')
    #     mode = 3

    # use prediction data for BIP_handel, BIP_je_Person and Einwohnen.
    elif 2023 <= year <= 2025:
        print(f'Input year is {str(year)}, using predication data and historical data from .csv file together.')
        mode = 1

    # other input, raise error
    else:
        print('Your input year is beyond limitation. Please check your input year(should from 2000 to 2025) and then '
              'retry.')
        return 0

    # For different modes, use different methods to get state average retail sale amount
    # mode 0: year 2014-2022, use historical data in .csv file
    if mode == 0:
        # directly return the data in .csv file, unit of measurement Euro/person
        return BIP_handel_state[year-2008] / Einwohner_state[year-2008] * 1000

    # mode 1: year 2023-2025, need to use predication method for all the three values
    elif mode == 1:

        # first, try to fit the population number with BIP_je_Person
        def func_P_with_BIP_P(x, kd, bd):
            return 1 / x * bd + kd

        popt1, pcov1 = curve_fit(func_P_with_BIP_P, Einwohner_state, BIP_je_Person_state)

        '''
        # these codes can be used to plot the population-average GDP relationship.
        fig, ax = plt.subplots()
        ax.plot(Einwohner_state, BIP_je_Person_state, 'bo', label='Rohdaten')
        ax.plot(Einwohner_state, func_P_with_BIP_P(Einwohner_state, *popt1), 'r-', label='Kurvenanpassung')
        ax.legend()
        ax.grid(True)
        # ax.set_titel('Das Verhältnis zwischen Bevölkerung und Produktion pro Kopf in' + state)
        ax.set_xlabel('Einwohnerinnen und Einwohner')
        ax.set_ylabel('BIP in jeweiligen Preisen je Einwohnerin bzw. Einwohner')
        plt.show()
        '''

        # second, try to fit time and population
        def func_t_with_P(x, ky, by):
            return x * ky + by

        popt2, pcov2 = curve_fit(func_t_with_P, year_state, Einwohner_state)

        '''
        # these codes can be used to plot the time-population relationship.
        fig2, ax2 = plt.subplots()
        ax2.plot(year_state, Einwohner_state, 'bo', label='Jahre')
        ax2.plot(year_state, func_t_with_P(year_state, *popt2), 'r-', label='Kurvenanpassung')
        ax2.legend()
        ax2.grid(True)
        # ax2.set_titel('Das Verhältnis zwischen Bevölkerung und Produktion pro Kopf in' + state)
        ax2.set_xlabel('Jahre')
        ax2.set_ylabel('Einwohnerinnen und Einwohner')
        plt.show()
        '''

        # third, try to fit the ln(d) with W/P. Instead of rename it with two parameters; this function I will just use
        # func3 because it is way too annoying to describe it in the function name.
        def func3(x, kp, bp):
            return kp * x + bp

        popt3, pcov3 = curve_fit(func3, np.log(BIP_je_Person_state)[6:], BIP_handel_state[6:] / Einwohner_state[6:])

        '''
        # these codes can be used to plot the np.log(BIP_je_Person_state) - BIP_handel_state / Einwohner_state relationship.
        fig3, ax3 = plt.subplots()
        ax3.plot(np.log(BIP_je_Person_state), BIP_handel_state / Einwohner_state, 'bo', label='Rohdaten')
        ax3.plot(np.log(BIP_je_Person_state), func3(np.log(BIP_je_Person_state), *popt3), 'r-', label='Kurvenanpassung')
        ax3.legend()
        ax3.grid(True)
        # ax3.set_titel('Das Verhältnis zwischen Bevölkerung und Produktion pro Kopf in' + state) # change titel
        ax3.set_xlabel('ln(d)') # change name
        ax3.set_ylabel('W/P') # change name
        plt.show()
        '''

        # Now all the parameters of the curve fitting are determined. Forecast values can be calculated with these
        # parameters. From the given year between 2020 and 2025, the state retail amount(predict) and the state
        # population(predict) can be calculated.

        # get the parameters from fitting codes before
        kp, bp = popt3[0], popt3[1]
        ky, by = popt2[0], popt2[1]
        kd, bd = popt1[0], popt1[1]

        # output the predict state retail amount from the given year
        def get_predict_retail_from_year(test_year):
            part1 = kp * (ky * test_year + by)
            part2 = np.log(kd + bd / (ky * test_year + by))
            part3 = bp * (ky * test_year + by)
            return part1 * part2 + part3

        '''
        # these codes can be used to plot the time-BIP relationship, 
        # and can be used to output a diagram to show the fitting effect
        fig4, ax4 = plt.subplots()
        ax4.plot(year_state, BIP_handel_state, 'bo', label='Rohdaten')
        ax4.plot(year_state, get_predict_retail_from_year(year_state), 'r-', label='Kurvenanpassung')
        ax4.legend()
        ax4.grid(True)
        # ax4.set_titel('Das Verhältnis zwischen Zeit und BIP in Handel in' + state) # change titel
        ax4.set_xlabel('Time/year')  # change name
        ax4.set_ylabel('BIP in Handel/million Euro')  # change name
        plt.show()
        '''

        # output the predict state population from the given year
        def get_predict_pop_from_year(test_year):
            return ky * test_year + by

        return get_predict_retail_from_year(year) / get_predict_pop_from_year(year) * 1000

    # mode 2: year 2000-2013, need to use predication for BIP_handel only
    elif mode == 2:

        # try to fit the ln(d) with W/P. Instead of rename it with two parameters;
        # Noted: the data for this curve fitting is only for year 2008-2020, and for
        # predication for year 2000-2007 only.
        def func4(x, kp, bp):  # Although has different names, the content is totally the same as the func3 in mode 1.
            return kp * x + bp

        popt4, pcov4 = curve_fit(func4, np.log(BIP_je_Person_state), BIP_handel_state / Einwohner_state)
        kp_4, bp_4 = popt4[0], popt4[1]

        # load BIP_je_Person data from .xlsx file for year 2000-2007 and import it into the above curve-fitting function
        BIP_je_Person_state_add = np.zeros(8)
        for year_temp_2 in range(14, 22):
            BIP_je_Person_state_add[year_temp_2 - 14] = float(BIP_je_Person.values[year_temp_2][state_num])

        return (kp_4 * np.log(BIP_je_Person_state_add[year-2000]) + bp_4) * 1000

    # mode 3: year 2021-2022, need to predict population
    # update: this part should never be reached after altering the calculation method.
    # this part cab be deleted.
    elif mode == 3:

        # try to fit time and population. likewise, this function is also the same as the one in mode 1 for the
        # same purpose
        def func_t_with_P(x, ky, by):
            return x * ky + by

        popt5, pcov5 = curve_fit(func_t_with_P, year_state, Einwohner_state)
        ky, by = popt5[0], popt5[1]

        return BIP_handel_state[year-2008] / (ky * year + by) * 1000

    else:
        return 0

# # test code
# abc = get_retail_average(2014,'Niedersachsen')
# pass