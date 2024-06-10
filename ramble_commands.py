import sys
import re
import requests
import json
import uuid
import os
import ssl
import time

from datetime import datetime
from ramble_database import DatabaseManager

from bs4 import BeautifulSoup

sys.setrecursionlimit(10 ** 5)
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context

db = DatabaseManager(
    host="localhost",
    user="root",
    password="12341234",
    database="scraping",
)


class QuitCommand:
    def execute(self):
        sys.exit()


class AddDomainData:
    def execute(self, data, timestamp=None):
        data["domain"] = "naver-cafe"  # 현재 네이버 카페 한정
        data["created_at"] = timestamp or datetime.utcnow().isoformat()
        db.add(table_name="domain_info", data=data)
        return "추가 완료!"


class DeleteDomainData:
    def execute(self, data):
        db.delete("domain_info", {"id": data})
        return "삭제 완료!"


class ListDomainData:
    def __init__(self, order_by="created_at"):
        self.order_by = order_by

    def execute(self):
        results = db.select("domain_info", order_by=self.order_by).fetchall()
        formatted_results = "\n".join([str(row) for row in results])
        return formatted_results


class RambleNaverCafeForPhone:
    """네이버 카페 포스트 내 번호 수집"""

    # ID, PW
    naver_id = "ID를 입력하세요"
    naver_pw = "PW를 입력하세요"

    # 오늘 날짜부터 end_date까지 수집합니다. ex: 2024-01-01
    end_date = "YYYY-MM-DD"

    # 기본 설정값
    # cookie 와 cafe_uuid 는 get_header_info() 함수에서 가져옵니다.
    cafe_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://cafe.naver.com/haha999",
        "Content-type": "application/json",
        "cookie": "",
    }
    cafe_uuid = ""
    cafe_id = None
    menu_id = None
    page = 1
    page_last_article_id = None
    last_item_index = None
    last_ad_index = None

    def execute(self, domain_id):
        cursor = db.select("domain_info", {"id": domain_id})
        result = cursor.fetchone()

        # 잘못된 입력
        if result:
            column_names = [desc[0] for desc in cursor.description]
            result_dict = dict(zip(column_names, result))
            description = result_dict["description"]
            self.cafe_id = result_dict["naver_cafe_id"]
            self.menu_id = result_dict["naver_menu_id"]
        else:
            return "실패했습니다. L을 눌러 정확한 정보를 입력했는지 확인해주세요."

        # 요청시 필요한 header값 받기
        self.get_header_info()
        # 크롤링
        self.fetchArticleList()
        # 완료되면 반환
        return f"{description}수집이 완료됐습니다."

    def fetchArticleList(self):
        """글 목록 가져오기
        - 게시판의 글 목록을 가져옵니다.
        - 1페이지에 50개를 가져옵니다.
          - perPage={개수}
          - API에서 가져올 수 있는 페이지 당 게시글 최대가 50개 입니다.
        - 지정한 end_date까지 반복합니다.
        """
        url = f"""
        https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid={self.cafe_id}&search.queryType=lastArticle&search.menuid={self.menu_id}&search.page={self.page}&search.perPage=50&ad=true&adUnit=MW_CAFE_ARTICLE_LIST_RS&uuid={self.cafe_uuid}
            &search.pageLastArticleId={self.page_last_article_id}&search.replylistorder=
            &search.firstArticleInReply=false
            &lastItemIndex={self.last_item_index}&lastAdIndex={self.last_ad_index}
        """
        response = requests.get(url, headers=self.set_headers(), data={}).json()
        article_list = response["message"]["result"]["articleList"]

        for article in article_list:
            if article["type"] == "ARTICLE":
                timestamp = article["item"]["writeDateTimestamp"]
                format_end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
                end_date_ms = int(format_end_date.timestamp()) * 1000
                if timestamp < end_date_ms:
                    return

                # 글 확인하기
                time.sleep(2)
                article_id = article["item"]["articleId"]
                self.page_last_article_id = article_id
                self.fetchArticle()

        # 다음 페이지 호출하기위한 페이지 수 조정
        next_params = response["message"]["result"]["nextRequestParameter"]
        self.last_item_index = next_params["lastItemIndex"]
        self.last_ad_index = next_params["lastAdIndex"]
        print(self.page_last_article_id, self.last_item_index, self.last_ad_index)
        if self.page != next_params["page"]:
            self.page += 1
            print(f"{str(self.page)} 페이지 수집 완료! 페이지 당 50개의 번호가 수집됩니다.")
            self.fetchArticleList()

    def fetchArticle(self):
        """게시물에서 핸드폰 번호를 추출해 데이터베이스에 저장합니다"""
        url = f"""
        https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{self.cafe_id}/articles/{self.page_last_article_id}?fromList=true&menuId={self.menu_id}&tc=cafe_article_list&useCafeId=true&buid={self.cafe_uuid}
        """
        response = requests.get(url, headers=self.set_headers(), data={}).json()
        html = response["result"]["article"]["contentHtml"]
        content = BeautifulSoup(html, "html.parser")
        content = content.get_text().strip().replace("\n", "").replace(" ", "")
        start = content.find("연락처")
        end = content.find("코멘트")
        try:
            if start == -1 or end == -1:
                start = content.find("010")
                if start == -1:
                    raise ValueError
                else:
                    phone = self.replace_value(content[start : start + 13])
                    print("PHONE: ", content[start : start + 13])
            else:
                phone = self.replace_value(content[start + 4 : end])
                print("PHONE: ", content[start + 4 : end])
            data = {}
            data["phone"] = phone
            db.add(
                table_name="guest_recruit_event",
                data=data,
            )
        except Exception as e:
            print(e)
            pass

    def replace_value(self, text):
        """핸드폰 번호를 올바른 형태로 재가공합니다"""
        word_to_value = {
            "응": "010",
            "공": "0",
            "영": "0",
            "⓪": "0",
            "o": "0",
            "O": "0",
            "ㅇ": "0",
            "일": "1",
            "ㅣ": "1",
            "I": "1",
            "|": "1",
            "!": "1",
            "①": "1",
            "➀": "1",
            "₁": "1",
            "이": "2",
            "둘": "2",
            "②": "2",
            "➁": "2",
            "₂": "2",
            "삼": "3",
            "셋": "3",
            "③": "3",
            "➂": "3",
            "₃": "3",
            "넷": "4",
            "사": "4",
            "④": "4",
            "➃": "4",
            "₄": "4",
            "오": "5",
            "⑤": "5",
            "➄": "5",
            "₅": "5",
            "육": "6",
            "⑥": "6",
            "➅": "6",
            "₆": "6",
            "칠": "7",
            "⑦": "7",
            "➆": "7",
            "₇": "7",
            "팔": "8",
            "➇": "8",
            "⑧": "8",
            "₈": "8",
            "구": "9",
            "⑨": "9",
            "➈": "9",
            "₉": "9",
        }
        pattern = "|".join(re.escape(key) for key in word_to_value.keys())
        phone = re.sub(pattern, lambda x: word_to_value[x.group()], text)
        phone = "".join(re.findall(r"\d+", phone))
        phone = phone[:11]
        return phone

    def set_headers(self):
        """요청에 필요한 header 값을 구성합니다"""
        return {
            "User-Agent": self.cafe_header["User-Agent"],
            "Cookie": self.cafe_header["cookie"],
            "Referer": f"https://m.cafe.naver.com/ca-fe/web/cafes/11367414/articles/{self.last_item_index}?fromList=true&menuId={self.menu_id}&tc=cafe_article_list",
        }

    def get_header_info(self):
        """요청에 필요한 cookie와 cafe uuid 값을 selenium을 사용해 가져옵니다"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        import time
        import pyperclip

        chrome_driver_path = "/usr/local/bin/chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.executable_path = chrome_driver_path
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(excutable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(
            "https://nid.naver.com/nidlogin.login?mode=form&url=https://cafe.naver.com/haha999"
        )
        driver.implicitly_wait(5)
        driver.maximize_window()
        id = driver.find_element(By.CSS_SELECTOR, "#id")
        id.click()
        pyperclip.copy(self.naver_id)
        id.send_keys(Keys.COMMAND, "v")
        time.sleep(3)
        pw = driver.find_element(By.CSS_SELECTOR, "#pw")
        pw.click()
        pyperclip.copy(self.naver_pw)
        pw.send_keys(Keys.COMMAND, "v")
        time.sleep(3)
        login_btn = driver.find_element(By.CSS_SELECTOR, "#log\.login")
        login_btn.click()

        driver.implicitly_wait(5)
        #
        uuidv4_script = """
        function uuidv4() {
            var uuid = "", i, random;
            for (i = 0; i < 32; i++) {
                random = Math.random() * 16 | 0;
                if (i == 8 || i == 12 || i == 16 || i == 20) {
                    uuid += "-"
                }
                uuid += (i == 12 ? 4 : (i == 16 ? (random & 3 | 8) : random)).toString(16);
            }
            return uuid;
        }
        return uuidv4();
        """

        getDeviceId_script = """
        function getDeviceId() {
            try {
                if (!localStorage.getItem(LOG_KEY)) {
                    localStorage.setItem(LOG_KEY, uuidv4());
                }
                return localStorage.getItem(LOG_KEY);
            } catch (e) {
                // silent
                console.error("Can't access localStorage");
                return "__UNKNOWN__";
            }
        }
        return getDeviceId();
        """

        oBAStatSender_script = """
        var LOG_KEY = "CAFE_UUID";

        function uuidv4() {
            var uuid = "", i, random;
            for (i = 0; i < 32; i++) {
                random = Math.random() * 16 | 0;
                if (i == 8 || i == 12 || i == 16 || i == 20) {
                    uuid += "-"
                }
                uuid += (i == 12 ? 4 : (i == 16 ? (random & 3 | 8) : random)).toString(16);
            }
            return uuid;
        }

        function getDeviceId() {
            try {
                if (!localStorage.getItem(LOG_KEY)) {
                    localStorage.setItem(LOG_KEY, uuidv4());
                }
                return localStorage.getItem(LOG_KEY);
            } catch (e) {
                // silent
                console.error("Can't access localStorage");
                return "__UNKNOWN__";
            }
        }

        function getReferrerForBA() {
            if (typeof(window.top.articleReadBalog) === "undefined") {
                window.top.articleReadBalog = {
                    useIframeReferrer: false
                };
            }
            if (!window.top.articleReadBalog.useIframeReferrer && !!window.top.document.referrer) {
                window.top.articleReadBalog.useIframeReferrer = true;
                return window.top.document.referrer;
            }
            return document.referrer;
        }

        var oBAStatSender = new cafe.BAStatSender({
            oClient: {
                service_id: 'cafe',
                user_key: 'tmy7767',
                os_name: '__UNKNOWN__',
                os_ver: '-1',
                app_ver: '-1',
                country: 'XX',
                language: 'xx',
                device_id: getDeviceId(),
                device_model: '__UNKNOWN__',
                product: 'web',
                client_context: {
                    'nnb': 'PHXIEWT725QWE' // CafeBaseAction.java
                }
            },
            sEnv: 'real'
        });

        return {
            uuidv4: uuidv4(),
            getDeviceId: getDeviceId(),
            getReferrerForBA: getReferrerForBA(),
            oBAStatSender: oBAStatSender
        };
        """
        uuidv4_result = driver.execute_script(uuidv4_script)
        getDeviceId_result = driver.execute_script(getDeviceId_script)
        oBAStatSender_result = driver.execute_script(oBAStatSender_script)
        self.cafe_uuid = getDeviceId_result
        driver.get("https://m.cafe.naver.com/haha999")
        cookies = driver.get_cookies()
        cookie_string = "; ".join(
            [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
        )
        self.cafe_header["cookie"] = cookie_string
        driver.quit()
