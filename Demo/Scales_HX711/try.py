
from utime import localtime, sleep


class DigitalClock:
    def __init__(self):
        self.current_time = localtime()
        self.alarm_times = []
        self.weight_threshold = 100  # 100 c.c
        self.time_threshold = 60*60  # in seconds
        self.log_file_name = 'weigth_log.txt'

    def update_clock(self):
        self.current_time = localtime()
        print("time = {}:{}:{}".format(
            self.current_time[3], self.current_time[4], self.current_time[5]))
        # read weight
        with open(self.log_file_name, 'w+') as file:
            file.write('{}:{}:{}- {}c.c.\n'.format(
                self.current_time[4], self.current_time[5], self.current_time[6], 340))

    def set_alarm(self, hour, minute, second):

        self.alarm_times.append(
            (self.current_time[0], self.current_time[1], self.current_time[2], hour, minute, second))

    def check_alarm(self):
        for alarm_time in self.alarm_times:
            if alarm_time[3] == self.current_time[3] and alarm_time[4] == self.current_time[4] and alarm_time[5] == self.current_time[5]:
                print('Alarm')
                return True
        return False


class WalterCup():
    def __init__(self):
        self.cup_weight = 0
        self.walter_weight = 0

    def update_walter_weight(self):
        read_weight = 100
        now_walter_weight = read_weight - self.cup_weight
        if self.walter_weight != now_walter_weight:
            self.walter_weight = now_walter_weight
            return True

    def set_cup_weight(self):
        read_weight = 10
        self.cup_weight = read_weight


if __name__ == '__main__':
    from machine import RTC
    rtc = RTC()
    rtc.datetime((2023, 1, 24, 2, 23, 2, 0, 0))  # set a time for start RTC

    t = DigitalClock()
    t.set_alarm(23, 3, 0)
    while True:
        t.update_clock()
        t.check_alarm()
        sleep(1)
