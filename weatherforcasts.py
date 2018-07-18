from urllib import request
from bs4 import BeautifulSoup


class Weather():
    # 此处的city先用带网页后缀的，便于测试
    def __init__(self, province, city):
        self.HOST = "http://www.nmc.cn/publish/forecast/"
        self.province = province
        self.city = city
        # 天气的关键字
        self.weather_items = ["date", "week", "wicon", "wdesc",
                              "temp", "direct", "wind"]
        # 天气关键字对应的中文
        self.weather_items_cn = {"date": "日期", "week": "星期", "wicon": "天气图标",
                                 "wdesc": "天气", "temp": "温度", "direct": "风向",
                                 "wind": "风力"}
        self.forecasts = []

        self.init_forcasts()
        self.update_forecasts()
        self.forecast_info()

    def init_forcasts(self):
        for i in range(7):
            self.forecasts.append(self.weather_items_cn.copy())

    # 打印天气预报信息
    def forecast_info(self):
        print(self.forecasts)

    def update_forecasts(self):
        URL = self.HOST+self.province+'/'+self.city
        """
        生成请求，读取网页
        """
        weather_request = request.Request(URL)
        try:
            with request.urlopen(weather_request, timeout=20) as f:
                data = f.read()
        except Exception as e:
            raise e
        else:
            """
            使用BeautifulSoup解析网页
            """
            soup = BeautifulSoup(data, 'html.parser')
            # 发布时间
            publish_time = soup.find(class_="btitle")
            # print(publish_time.span.string.strip())

            # 获取天气预报部分
            forecasts = soup.find("div", {"id": "forecast"})
            todays = forecasts.find_all("div", class_="today")
            days = forecasts.find_all("div", class_="day")

            # 处理天气
            for i, forecast in enumerate(self.forecasts):
                for item in self.weather_items:
                    day_value = days[i].find(class_=item)
                    if item == "wicon" and day_value.img is not None:
                        forecast[item] = day_value.img['src']
                    elif item == "wdesc":
                        today_values = todays[i].find_all(class_=item)
                        if len(today_values) > 1 \
                            and today_values[0].string.strip() \
                                != today_values[1].string.strip():
                            forecast[item] = today_values[0].string.strip() \
                                + "转" + today_values[1].string.strip()
                        else:
                            forecast[item] = day_value.string.strip()
                    elif item == "temp":
                        today_values = todays[i].find_all(class_=item)
                        if len(today_values) > 1 \
                            and today_values[0].string.strip() \
                                != today_values[1].string.strip():
                            forecast[item] = today_values[0].string.strip() \
                                + "~" + today_values[1].string.strip()
                        else:
                            forecast[item] = day_value.string.strip()
                    else:
                        forecast[item] = day_value.string.strip()
