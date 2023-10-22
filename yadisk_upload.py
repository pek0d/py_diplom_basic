# тест API яндекс-диск
from configuration import YA_TOKEN
import requests  # type: ignore
import pprint
import pysnooper  # type: ignore
import json
from urllib.parse import urlencode
import urllib3
import enlighten


pp = pprint.PrettyPrinter(indent=2)

token = YA_TOKEN


class YA_disk:
    api_base_url = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": token}

    def _build_url(self, api_method):
        return f"{self.api_base_url}/{api_method}"

    def _write_responses(self, response):
        """Запись ответа в json"""
        with open("response_info.json", "w") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

    @pysnooper.snoop()
    def create_upload_folder(self):
        """Создание папки для загрузки"""
        url = self._build_url("resources")
        folder_name = input("Введите имя папки для загрузки: ")
        self.dir_name = f"{folder_name}"
        params = {"path": folder_name}
        response = requests.put(url, headers=self.headers, params=params)
        if response.status_code == 201:
            print(f"Папка с названием {folder_name} создана")
        else:
            print(response.json()["message"])

        response_info = requests.get(url, headers=self.headers, params=params)
        pp.pprint(response_info.json())
        return self.dir_name

    @pysnooper.snoop()
    def upload_ext_url(self, file_name, link2pic):
        """Загрузить файл на диск с указанной (внешеней) ссылкой"""
        url_for_upload = self._build_url("resources/upload")
        folder = f"{self.dir_name}/"
        # encdoded_url = urlencode(link2pic)
        params = {"path": f"{folder}{file_name}", "url": link2pic}
        response = requests.put(
            url_for_upload, headers=self.headers, params=params)
        if response.status_code == 202:
            print("Началась загрузка")
        else:
            print(response.json()["message"])

        # response_status_uploading = requests.get(
        #     self._build_url("operations") + "/" + response.json()["upload_id"]
        # )
        # print(response_status_uploading.json()["status"])
        #
        # @pysnooper.snoop()
        # def get_upload_url(self, file_name):
        #     """Получить ссылку на загрузку файла"""
        #     url = self._build_url("resources/upload")
        #     path = self.dir_name
        #     params = {"path": f"{path}{file_name}", "overwrite": "true"}
        #     response = requests.get(url, headers=self.headers, params=params)
        #     if response.status_code == 200:
        #         url_for_upload = response.json()["href"]
        #         print(f"Ссылка для загрузки: {url_for_upload}")
        #         self.url_for_upload = url_for_upload
        #         return self.url_for_upload
        #
        #     else:
        #         print(response.json()["message"])
        #
        #     # справочно
        #     self._write_responses(response)
        #
        # @pysnooper.snoop()
        # def upload_file(self, file_name):
        #     """Загрузить файл на яндекс диск"""
        #
        #     href = self.url_for_upload
        #     response = requests.put(href, data=open(file_name, "rb"))
        #     response.raise_for_status()
        #     if response.status_code == 201:
        #         print("Файл загружен")
        #     else:
        #         print(response.json()["message"])


if __name__ == "__main__":
    ya = YA_disk(token)
    ya.create_upload_folder()
    ya.upload_ext_url(
        "722280.jpg",
        "https://bmwguide.ru/wp-content/uploads/2016/07/bmw-at-2016-consorso-d-eleganza-bmw-2002-hommage-13.jpg",
    )
