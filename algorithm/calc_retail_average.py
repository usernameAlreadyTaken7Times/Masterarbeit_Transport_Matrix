import numpy as np
from scipy.optimize import curve_fit
import matplotlib.axes as mae
import matplotlib.pyplot as plt
from IO.excel_input import load_excel


def get_state_num_from_state_name(state_name):
    # use the input state name to find a corresponding state index
    name = state_name
    if isinstance(name, str):
        print("Input type not match. please use string instead.")
        return -1
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


def get_retail_average(predict_year, predict_state, data_filename='C:/Users/86781/PycharmProjects/pythonProject/data/BIP und Einkommen.xlsx'):
    """This funktion is used to calculate the relationship between GDP of a german state and its population.
    Then use the input state name and year to predict the state's retail sale average amount (Euro/per person).
    Then in other scripts, this value can be used to multiply the predicted population in the chosen test area and
    get the retail amount for the area. To achieve the goal, an Excel file containing the relevant data is applied,
    and inside this funktion, several regression equations are needed for such process. First, init: read data from
    file and variables init, Second, curve fitting: try to use curve_fit function and preset functions f(x) to fit
    the data and third, forecast value acquiring: use the given year to output the predict retail amount and population
    of the chosen state and time.

    :param int predict_year: The year you want to predict
    :param str predict_state: the german state you want to predict
    :param str data_filename: the .xlsx file containing the BIP_handel, BIP_je_Person and Population data
    :return: the BIP_Handel je Person at the time point of the chosen year, chosen state, unit of measurement Euro/Person
    """

    # ------------------------------------------------------1-init------------------------------------------------------
    year = predict_year
    state = predict_state
    retail_xlsx_filename = data_filename

    # BIP_handel is the GDP with german industry division standard 'WZ 2008',
    # item 'Handel; Instandhaltung und Reparatur von Kraftfahrzeugen (G)'. The data is from 'www.statistikportal.de' and
    # shows the sale amount of 'Einzelhandel' in every state of Germany. However, the data is only avaivable from 2008
    # to 2020, but so the data of year 2021 and 2022 for other variables(BIP_je_Person, Einwohner) are discarded.
    BIP_handel = load_excel(retail_xlsx_filename, 'BIPhandel')
    # BIP_handel data for state init
    BIP_handel_state = np.zeros(len(BIP_handel) - 5)

    # BIP_je_Person is the GDP in every state divides its population number. Likewise, the data is also from german
    # statistic department. In this program, this value together with the BIP_handel, can be used to determine and
    # predict the sale amount for a specific year.
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

    # use a cycle to read all relevant data of the chosen state, these array indexes' numbers are based on the format of
    # the original xlsx file containing the data, which was directly copied from the website of Deutsche Statistiksamt,
    # so the format could be a little messy.
    for year_tmp in range(5, len(BIP_handel)):
        BIP_handel_state[year_tmp - 5] = float(BIP_handel.values[year_tmp][state_num])
        BIP_je_Person_state[year_tmp - 5] = float(BIP_je_Person.values[year_tmp + 17][state_num])
        Einwohner_state[year_tmp - 5] = float(Einwohner.values[year_tmp + 17][state_num])
        year_state[year_tmp - 5] = float(year_tmp + 2003)

    # --------------------------------------2-curve fitting-------------------------------------------------------------

    # first, try to fit the population number with BIP_je_Person
    def func1(x, kd, bd):
        return 1 / x * bd + kd

    popt1, pcov1 = curve_fit(func1, Einwohner_state, BIP_je_Person_state)

    '''
    # these codes can be used to plot the population-average GDP relationship.
    fig, ax = plt.subplots()
    ax.plot(Einwohner_state, BIP_je_Person_state, 'bo', label='Rohdaten')
    ax.plot(Einwohner_state, func1(Einwohner_state, *popt1), 'r-', label='Kurvenanpassung')
    ax.legend()
    ax.grid(True)
    # ax.set_titel('Das Verhältnis zwischen Bevölkerung und Produktion pro Kopf in' + state)
    ax.set_xlabel('Einwohnerinnen und Einwohner')
    ax.set_ylabel('BIP in jeweiligen Preisen je Einwohnerin bzw. Einwohner')
    plt.show()
    '''

    # second, try to find the relationhip between time and population
    def func2(x, ky, by):
        return x * ky + by

    popt2, pcov2 = curve_fit(func2, year_state, Einwohner_state)

    '''
    # these codes can be used to plot the time-population relationship.
    fig2, ax2 = plt.subplots()
    ax2.plot(year_state, Einwohner_state, 'bo', label='Jahre')
    ax2.plot(year_state, func2(year_state, *popt2), 'r-', label='Kurvenanpassung')
    ax2.legend()
    ax2.grid(True)
    # ax2.set_titel('Das Verhältnis zwischen Bevölkerung und Produktion pro Kopf in' + state)
    ax2.set_xlabel('Jahre')
    ax2.set_ylabel('Einwohnerinnen und Einwohner')
    plt.show()
    '''

    # third, try to fit the ln(d) with W/P
    def func3(x, kp, bp):
        return kp * x + bp

    popt3, pcov3 = curve_fit(func3, np.log(BIP_je_Person_state), BIP_handel_state / Einwohner_state)

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

    # ----------------------------------------3-forecast value acquiring------------------------------------------------

    # Now all the parameters of the curve fitting are determined. Forecast values can be calculated with these
    # parameters. From the given year, the state retail amount(predict) and the state population(predict)
    # can be calculated.

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
    # these codes can be used to plot the time-BIP relationship, and can be used to output a diagram to show the fitting
    # effect
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
