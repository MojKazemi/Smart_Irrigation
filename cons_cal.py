import json
from datetime import datetime
import calendar

class consumption_calc:
    def __init__(self,status_file, IDs, cost):
        with open(status_file) as file:
            self.statis = json.load(file)
        self._root = f"{IDs['farmID']}/{IDs['sectionID']}"
        
        self.cost = cost

    def selective_time(self, start, end):
        start_time = datetime.strptime(start,  "%d/%m/%Y %H:%M:%S")
        end_time = datetime.strptime(end, "%d/%m/%Y %H:%M:%S")
        # time_on_list = []
        time_on_seconds = 0
        first_status = None
        last_status = None
        f_state = None

        for _dict in self.statis['pump_status']:
            if _dict['r'] == self._root:
                _dict_t = datetime.strptime(_dict['t'], "%d/%m/%Y %H:%M:%S")

                if start_time <= _dict_t <= end_time:
                    if first_status == None:
                        first_status = _dict['status']
                        _first_t = _dict_t
                    last_status = _dict['status']

                    if f_state == None and _dict['status'] == 'on':
                        f_state = _dict['status']
                        time_s = _dict_t

                    elif f_state == 'on' and _dict['status'] == 'off':
                        time_on = _dict_t - time_s
                        # time_on_list.append(time_on)
                        time_on_seconds = time_on_seconds + time_on.total_seconds()
                        f_state = None
        if last_status == 'on':
            time_on = end_time - time_s
            time_on_seconds = time_on_seconds + time_on.total_seconds()

        if first_status == 'off':
            time_on = _first_t - start_time
            time_on_seconds = time_on_seconds + time_on.total_seconds()
    
        power_cons = round(time_on_seconds/3600 * self.cost,2)  # 1 KW/h * Elec_price (Euro)

        return time_on_seconds, power_cons

    def daily_usage(self, day):
        '''
            Day should be present as %d/%m/%Y
        '''
        
        start_time = day +" 00:00:00"
        end_time = day +" 23:59:59"
        on_sec, power_cons = self.selective_time(start_time,end_time)

        return on_sec, power_cons

    def monthly_usage(self, month_year = '01/2023'):
        mm = month_year.split('/')[0]
        if mm.isdigit() and len(mm) == 1:
            month_year = f"0{mm}/" + month_year.split("/")[1]

        if int(month_year.split('/')[0]) == datetime.now().month and int(month_year.split('/')[1]) == datetime.now().year:
            now_time = datetime.now()
            end_time = now_time.strftime('%d/%m/%Y %H:%M:%S')

        else:
            month = month_year.split('/')[0]
            if month == '02':
                end_day = '28'
            elif month == '04'or month == '06' or month == '09' or month == '11':
                end_day = '30'
            else:
                end_day = '31'

            end_time = f'{end_day}/{month_year} 23:59:59'

        start_time = f'01/{month_year} 00:00:00'
        on_sec, power_cons = self.selective_time(start_time,end_time)

        return on_sec, power_cons
        
    def yearly(self, year = '2023'):
        year_cost ={}
        for i in range(1,13):
            month_year = f'{i}/{year}'
            _, power_cons = self.monthly_usage(month_year)
            month_name = calendar.month_name[i]
            year_cost[month_name] = power_cons
        return year_cost
            


if __name__ == "__main__":

    IDs = {
    'farmID': 'Farm_2',
    'sectionID': 'Section1'
    }

    cost = 0.12 #cost per min 

    cons = consumption_calc('./pump_status.json', IDs, cost)
    # on_sec, power_cons = cons.selective_time(start='25/03/2023 00:00:00',end='01/04/2023 23:59:59')

    # print(f'on_sec: {on_sec}\npower cons: {power_cons}')

    # on_sec, power_cons = cons.daily_usage('25/03/2023')
    # print(f'on_sec: {on_sec}\npower cons: {power_cons}')

    on_sec, power_cons = cons.monthly_usage(month_year = '5/2023')
    print(f'on_sec: {on_sec}\npower cons: {power_cons}')

    # _dict = cons.yearly(year = '2024')
    # print(_dict)