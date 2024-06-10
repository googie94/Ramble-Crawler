from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import time
import json
import re
import pytz

# SSL
import os
import ssl
import sys

sys.setrecursionlimit(10**5)
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context

# MYSQL
import pymysql

host = "HOST"
user = "USER"
pw = "PW"
db = "DB"


# USER
payload = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Referer": "https://apis.naver.com/",
    "cookie": "NNB=HGH4WWPQCS4WE; ASID=74ff635c00000181a508657c0000006e; MM_NEW=1; NFS=2; _ga=GA1.2.931062148.1657078256; _ga_7VKFYR6RV1=GS1.1.1663138298.48.1.1663138896.60.0.0; nx_ssl=2; page_uid=hJzA9lp0dwoss75RUpKssssssfd-075913; csrf_token=e7286068a1eb1e1521d017c311c7255876888e437176b268cf92c6eaf664b72136b24a257fac9b8a3757721b0576725e3c56443b51700d078ba9884ffe0e405d; _naver_usersession_=QY03x2z3n66exHh1+Ru0anQW; nid_inf=1148602420; NID_AUT=GD8IsCNrxyA8paYQqFBF2JGQk+nWgEBSEEWKmCWXevlaTclPKDN3eV7ZHugiMpl0; NID_JKL=aoVmXAuqTb1+5ENa6TYW2WnPHoCZOuBCjWSTFXdbLcI=; NID_SES=AAABqEx7iCsno60xd5d4gQGfqALhAYm8wlVdAggaW/ggOLp1AtSjirlHLExWOOTMucpcam2qttw/mwRaq4oWoxtzK2T9wJlJnpHg0m3cUaW3lkVRICqmXBLXns5/FVqKyBeCYPudf9owc/Urt2LEGmePXNkBfcbzafhi00y2BAWZV0kHYP2hF0flx2pa6IaW5H2yhAZc7GdaCgSCbgmLFgcP2wRoq4NzXncf3VL7HeBT9zO1KN/LRkiR7FYbJLp3tXqWyYS7cKerCNnZpLoDyxR+GXtw6fG10SYIgcgIS7W+k6HMieXPL+AMgVsrbreMkClOEdMUYFdyMPifYIOvb2kcZ7XCl/msWvkkVbz5JTlRUNF5FiMqy7cvqtInzlZGTF+IFEInFvAlpJwTXE8qFT4UmdUd8HUC9JFRNBMc2gby/6ReoR20408V5VyPsBH+xPoZrgSNwjX8s5Tfu9Zzn0Kf+NSekooaWbaR3cfHvpSozvOMezLBtoA3jCUPP2n47qVyBPODRxE8gZ9ifWJUzmizystDLYcBkB6LD5HHAXe5kH3OZWJZwT2bvv+rURLUfQHDHw==; page_uid=85f32ec6-eedf-49d8-b9de-6cb165fa3ad9",
    "Content-type": "application/json",
}


regions = [
    {
        "cortarNo": "1100000000",
        "centerLat": 37.566427,
        "centerLon": 126.977872,
        "cortarName": "서울시",
    },
    {
        "cortarNo": "4100000000",
        "centerLat": 37.274939,
        "centerLon": 127.008689,
        "cortarName": "경기도",
    },
    {
        "cortarNo": "2800000000",
        "centerLat": 37.456054,
        "centerLon": 126.705151,
        "cortarName": "인천시",
    },
    {
        "cortarNo": "2600000000",
        "centerLat": 35.180143,
        "centerLon": 129.075413,
        "cortarName": "부산시",
    },
    {
        "cortarNo": "3000000000",
        "centerLat": 36.350465,
        "centerLon": 127.384953,
        "cortarName": "대전시",
    },
    {
        "cortarNo": "2700000000",
        "centerLat": 35.87139,
        "centerLon": 128.601763,
        "cortarName": "대구시",
    },
    {
        "cortarNo": "3100000000",
        "centerLat": 35.5386,
        "centerLon": 129.311375,
        "cortarName": "울산시",
    },
    {
        "cortarNo": "3600000000",
        "centerLat": 36.592907,
        "centerLon": 127.292375,
        "cortarName": "세종시",
    },
    {
        "cortarNo": "2900000000",
        "centerLat": 35.160032,
        "centerLon": 126.851338,
        "cortarName": "광주시",
    },
    {
        "cortarNo": "4200000000",
        "centerLat": 37.885399,
        "centerLon": 127.72975,
        "cortarName": "강원도",
    },
    {
        "cortarNo": "4300000000",
        "centerLat": 36.636149,
        "centerLon": 127.491238,
        "cortarName": "충청북도",
    },
    {
        "cortarNo": "4400000000",
        "centerLat": 36.63629,
        "centerLon": 126.68957,
        "cortarName": "충청남도",
    },
    {
        "cortarNo": "4700000000",
        "centerLat": 36.518504,
        "centerLon": 128.437796,
        "cortarName": "경상북도",
    },
    {
        "cortarNo": "4800000000",
        "centerLat": 35.238343,
        "centerLon": 128.6924,
        "cortarName": "경상남도",
    },
    {
        "cortarNo": "4500000000",
        "centerLat": 35.820433,
        "centerLon": 127.108875,
        "cortarName": "전라북도",
    },
    {
        "cortarNo": "4600000000",
        "centerLat": 34.816358,
        "centerLon": 126.462443,
        "cortarName": "전라남도",
    },
    {
        "cortarNo": "5000000000",
        "centerLat": 33.488976,
        "centerLon": 126.498238,
        "cortarName": "제주도",
    },
]
current_city = ""
current_city_lat = ""
current_city_lon = ""
current_dvsn = ""
search_types = ["풋살장", "축구장"]
page = 1


def get_latlon(address):
    # address = "서울 성동구 옥수동 490-7"
    url = "https://dapi.kakao.com/v2/local/search/address.json?query={}".format(address)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Authorization": "KakaoAK cbb06342576b319dc2e2bf70f873b1da",
    }
    response = requests.get(
        url,
        headers=headers,
    )
    response = json.loads(response.text)
    return response["documents"][0]["address"]
    # print(response["documents"][0]["address"]["x"])
    # print(response["documents"][0]["address"]["y"])


# get_latlon()


def save(
    name,
    address,
    roadAddress,
    phone,
    region,
    district,
    ground_type,
    page,
    facility,
    latitude,
    longitude,
    source,
    size_x,
    size_y,
):
    conn = pymysql.connect(host=host, user=user, passwd=pw, db=db, charset="utf8")
    cur = conn.cursor()
    cur.execute("USE scraping")
    cur.execute(
        "INSERT INTO stadium_group (name, address, road_address, phone, region, district, ground_type, page, facility, latitude, longitude, source, size_x, size_y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            name,
            address,
            roadAddress,
            phone,
            region,
            district,
            ground_type,
            page,
            facility,
            latitude,
            longitude,
            source,
            size_x,
            size_y,
        ),
    )
    cur.connection.commit()
    cur.close()
    conn.close()


def scrap():
    # 아이엠그라운드
    for index in range(1606):
        print("======")
        print(index)
        try:
            url = "https://m.iamground.kr/futsal/detail/{}".format(index)
            res = requests.get(url, headers=headers, data=payload).text
            content = BeautifulSoup(res, "html.parser")
            scripts = content.findAll("script")
            script_list = []
            for script in scripts:
                if "SERVER.facInfo" in script.text:
                    script_list.append(script)

            # print(script_list)

            script = script_list[0].get_text().replace("\n", "").replace(" ", "")
            # 구장 정보
            # stad_start = script.find("SERVER.facGroup=")
            # stad_end = script.find(";", stad_start)
            # stad_info = json.loads(script[stad_start + 16 : stad_end])

            # 시설 정보
            fac_start = script.find("SERVER.facInfo=")
            fac_end = script.find(";", fac_start)
            fac_info = json.loads(script[fac_start + 15 : fac_end])

            # print(len(stad_info))

            if fac_info["ballrent"] == "":
                fac_info["ballrent"] = "알수없음"

            if fac_info["parking"] == "":
                fac_info["parking"] = "알수없음"

            if fac_info["shoesrent"] == "":
                fac_info["shoesrent"] = "알수없음"

            if fac_info["shower"] == "":
                fac_info["shower"] = "알수없음"

            if fac_info["vestrent"] == "":
                fac_info["vestrent"] = "알수없음"

            if fac_info["temp"] == "":
                fac_info["temp"] = "알수없음"

            if fac_info["lighting"] == "":
                fac_info["lighting"] = "알수없음"

            if fac_info["indoor"] == "":
                fac_info["indoor"] = "알수없음"

            if fac_info["floor"] == "":
                fac_info["indoor"] = "알수없음"

            facility = {
                "parking": fac_info["parking"],
                "shower": fac_info["shower"],
                "lighting": fac_info["lighting"],
                "temp": fac_info["temp"],
                "shoesrent": fac_info["shoesrent"],
                "ballrent": fac_info["ballrent"],
                "vestrent": fac_info["vestrent"],
                "indoor": fac_info["indoor"],
            }

            if fac_info["size"]:
                x = fac_info["size"].split("*")[0]
                y = fac_info["size"].split("*")[1]

            print("이름: ", fac_info["fName"])
            print("주소: ", fac_info["fAddress"])
            print("홈페이지: ", fac_info["homepage"])
            print("잔디: ", fac_info["floor"])
            print("연락처: ", fac_info["tel"])
            print("x: ", x)
            print("y: ", y)
            print("시설: ", facility)
            print("위도: ", fac_info["latitude"])
            print("경도: ", fac_info["longitude"])
            print("소스: IAMGROUND")
            print("=====")
            time.sleep(3)

            save(
                fac_info["fName"],
                fac_info["fAddress"],
                None,
                fac_info["tel"],
                None,
                None,
                fac_info["floor"],
                fac_info["homepage"],
                str(facility),
                fac_info["latitude"],
                fac_info["longitude"],
                "IAMGROUND",
                x,
                y,
            )
        except:
            pass

    # 네이버
    # global regions
    # global current_city
    # global current_city_lat
    # global current_city_lon

    # for region in regions:
    #     current_city = region["cortarName"]
    #     current_city_lat = str(region["centerLat"])
    #     current_city_lon = str(region["centerLon"])
    #     fetchRegion(region["cortarNo"])


def fetchRegion(cortarNo):
    """
    도 -> 시군구 검색
    """
    global current_dvsn
    global search_types

    url = "https://new.land.naver.com/api/regions/list?cortarNo={}".format(cortarNo)
    res = requests.get(url, headers=headers, data=payload).json()
    devisions = res["regionList"]
    for devision in devisions:
        current_dvsn = devision["cortarName"]
        fetchStadium()


def fetchStadium():
    """
    # 이름: 부산환경공단 수영사업소 축구장 stadium["name"]
    # 주소: 부산광역시 동래구 안락동 1108 stadium["address"]
    # 상세주소: 부산광역시 동래구 온천천남로 185 (안락동) 수영사업소 stadium["roadAddress"]
    # 연락처: stadium["telDisplay"]
    # 도시: current_ciry
    # 시군구: current_dvsn
    # 가로: X
    # 세로: X
    # 구장유형: X
    # 홈페이지: stadium["homePage"]
    # 주차: X
    # 위도: stadium["x"]
    # 경도: stadium["y"]
    """
    global current_city
    global current_dvsn
    global search_types
    global current_city_lat
    global current_city_lon
    global page

    time.sleep(5)

    if len(current_dvsn.split(" ")) < 2:
        current_dvsn = current_city + " " + current_dvsn

    try:
        for search_type in search_types:
            search_query = current_dvsn + " " + search_type
            print("===========")
            print("PAGE: ", page)
            print("SEARCH_QUERY: ", search_query)
            url = "https://map.naver.com/v5/api/search?caller=pcweb&query={}&type=all&searchCoord={};{}&page={}&displayCount=20&lang=ko".format(
                search_query, current_city_lat, current_city_lon, page
            )
            res = requests.get(url, headers=headers, data=payload)
            print(res)
            res = res.json()
            print(res)
            stadium_list = res["result"]["place"]["list"]
            print("LENGTH: ", len(stadium_list))
            print("TOTAL COUNT: ", res["result"]["place"]["totalCount"])
            if len(stadium_list) != 0:
                for stadium in stadium_list:
                    print("------")
                    print("도시: ", current_city)
                    print("시군구: ", current_dvsn)
                    print("이름: ", stadium["name"])
                    print("주소: ", stadium["address"])
                    print("상세주소: ", stadium["roadAddress"])
                    print("연락처: ", stadium["telDisplay"])
                    print("홈페이지: ", stadium["homePage"])
                    print("위도: ", stadium["x"])
                    print("경도: ", stadium["y"])

                    save(
                        stadium["name"],
                        stadium["address"],
                        stadium["roadAddress"],
                        stadium["telDisplay"],
                        current_city,
                        current_dvsn,
                        None,
                        stadium["homePage"],
                        None,
                        stadium["x"],
                        stadium["y"],
                        "NAVER",
                    )
            elif len(stadium_list) >= 20:
                page = page + 1
                fetchStadium()
    except:
        pass


# 스크랩
scrap()
