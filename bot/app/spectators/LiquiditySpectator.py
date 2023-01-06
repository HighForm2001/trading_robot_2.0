import datetime
# currently useless

class LiquiditySpectator:
    session_high = None
    session_low = None
    previous_day_high = None
    previous_day_low = None
    previous_session = None
    current_date = None
    previous_session_start = None
    previous_session_end = None

    def __init__(self, session, date, df):

        self.__operation(session,date,df)
        print(__name__ + " initialized")

    def __operation(self,session,date,df):
        self.previous_session = session
        self.current_date = date
        if date.weekday() == 0:
            previous_date = date - datetime.timedelta(days=3)
        else:
            previous_date = date - datetime.timedelta(days=1)
        split = datetime.time(0, 0, 0)
        if session == "London":
            self.previous_session_start = datetime.time(9, 0, 0)
            self.previous_session_end = datetime.time(12, 0, 0)
        elif session == "Asian":
            self.previous_session_start = datetime.time(2, 0, 0)
            self.previous_session_end = datetime.time(4, 0, 0)
        else:
            self.previous_session_start = datetime.time(14, 0, 0)
            self.previous_session_end = datetime.time(17, 0, 0)
        temp_array_time = []
        temp_array_date = []
        for rows in range(0, len(df)):
            #
            # print(type(rows))
            # print(rows)
            converted = df.iloc[rows]["time"].to_pydatetime()
            if converted.date() == previous_date:
                temp_array_date.append(df["high"][rows])
                temp_array_date.append(df["low"][rows])
                if self.previous_session == "New York" and split < converted.time() and self.__in_between(
                        self.previous_session_start, converted.time(), self.previous_session_end):
                    temp_array_time.append(df["high"][rows])
                    temp_array_time.append(df["low"][rows])
            if converted.date() == self.current_date and self.__in_between(self.previous_session_start,
                                                                           converted.time(), self.previous_session_end):
                temp_array_time.append(df["high"][rows])
                temp_array_time.append(df["low"][rows])
        self.session_low = min(temp_array_time)
        self.session_high = max(temp_array_time)
        self.previous_day_high = max(temp_array_date)
        self.previous_day_low = min(temp_array_date)
        pass

    def check_update(self, session,date,df):
        if self.previous_session != session or self.current_date != date:
            self.__operation(session,date,df)

    def __in_between(self,start,now,end):
        return start <= now <= end