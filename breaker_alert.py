import requests
import time
import json
import pychromecast

remo_e_token ="enter_your remo_api_token"
hue_ip = "enter_hue_bridge_ip"
hue_user_id = "enter_your_hue_user_id"
hue_group = 3
color_hue = 65318
remo_mini_ip = "enter_remo_ip"

# エアコン停止の信号
aircon_off_ir = {"format":"us",
               "freq":38,
               "data":[3226,1682,367,445,369,445,371,1261,367,447,367,1264,364,441,372,451,367,446,369,1262,365,1261,367,441,372,465,349,451,365,1258,373,1257,366,451,365,442,372,442,370,444,372,447,366,446,369,442,372,445,367,445,370,454,364,445,370,446,365,445,371,1259,368,450,363,447,369,443,369,445,370,444,371,445,369,450,364,1262,367,442,373,447,365,449,367,447,365,1264,376,425,380,447,365,449,368,450,375,430,371,445,370,1264,365,445,372,1260,366,1261,370,1262,366,1259,368,1263,365,1261,366]}

# スマートメーター情報取得
def power_get():
    url = 'https://api.nature.global/1/appliances'
    headers = {'Authorization': 'Bearer ' + remo_e_token, 'accept':'application/json'}
    appliances = requests.get(url, headers=headers).json()

    # 電力情報を取得
    list = appliances[0]['smart_meter']['echonetlite_properties']
    dict={}
    for item in list:
        key=item['name']
        dict[key]=item['val']

    power = int(dict['measured_instantaneous'])
    print('Power_Now:' + str(power))
    return power

# hueで赤点滅
def blink_hue():
    url_hue = f"http://{hue_ip}/api/{hue_user_id}/groups/{hue_group}/action"

    body = json.dumps({"on":"true", "hue": color_hue, "bri":254, "sat": 254, "alert":"lselect"})
    requests.put(url_hue, data=body)

def reflesh_hue():
    url_hue = f"http://{hue_ip}/api/{hue_user_id}/groups/{hue_group}/action"
    body = json.dumps({"xy":[0.4448, 0.4066]})
    requests.put(url_hue, data=body)


def turn_off_aircon():
    url = f'http://{remo_mini_ip}/messages'
    headers = {'X-Requested-With': 'local', 'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(aircon_off_ir), headers=headers)
    

def speak_alert_3000watt():
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["ベッドルーム"])
    cast = chromecasts[0]
    mc = cast.media_controller
    cast.wait()
    mc.play_media('https://github.com/bohemian916/google_home_speech/blob/main/alert_3000watt.mp3?raw=true','audio/mp3')

def speak_alert_3500watt():
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["ベッドルーム"])
    cast = chromecasts[0]
    mc = cast.media_controller
    cast.wait()
    mc.play_media('https://github.com/bohemian916/google_home_speech/blob/main/alert_3500watt.mp3?raw=true','audio/mp3')


# ここからスタート
if __name__ == '__main__':

    print('Start')

    # 電力値取得
    power = power_get()

    if power > 3500:
        blink_hue()
        speak_alert_3500watt()
        turn_off_aircon()
        time.sleep(20)
        reflesh_hue()
        exit()

    # 過去５回の計測値
    with open("5time_value.txt", 'r') as f:
        last5 = json.load(f)

    new_last5 = [last5[i] for i in range(1,5)]
    new_last5.append(int(power))
    print(new_last5)
    power_average = sum(new_last5) /5.0 

    if power_average > 3000:
        blink_hue()
        speak_alert_3000watt()
        turn_off_aircon()
        time.sleep(20)
        reflesh_hue() 

    print("average: " + str(power_average))
    with open("5time_value.txt", 'w') as f:
        json.dump(new_last5, f)

    print('End')
