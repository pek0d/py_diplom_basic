from configuration import YA_TOKEN
import requests  # type: ignore
import pprint
import pysnooper  # type: ignore
import json
from urllib.parse import urlencode


pp = pprint.PrettyPrinter(indent=2)

token = YA_TOKEN


class YA_disk:
    api_base_url = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": token}

    def _build_url(self, api_method):
        """Собрать ссылку на API"""
        return f"{self.api_base_url}/{api_method}"

    def _write_responses(self, response):
        """Запись ответа в json"""
        with open("response_info.json", "w") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

    @pysnooper.snoop()
    def create_upload_folder(self):
        """Создание папки для загрузки"""
        # формирование ссылки для запроса
        url = self._build_url("resources")
        folder_name = input("Введите имя папки для загрузки: ")
        self.dir_name = f"{folder_name}"
        params = {"path": folder_name}
        response = requests.put(url, headers=self.headers, params=params)
        # проверка статуса запроса
        if response.status_code == 201:
            print(f"Папка с названием {folder_name} создана")
        else:
            print(response.json()["message"])

        # ответ по состоянию запроса на яндекс диск
        response_info = requests.get(url, headers=self.headers, params=params)

        # для отображения статуса запроса в отдельном файле
        self._write_responses(response_info)

        return self.dir_name

    @pysnooper.snoop()
    def upload_ext_url(self, file_name, link2pic):
        """Загрузить файл на диск с указанной (внешеней) ссылкой"""
        # формирование ссылки для запроса
        url_for_upload = self._build_url("resources/upload")
        # объявление имени папки из ранее заданного имени
        folder = f"{self.dir_name}"
        params = {"path": f"disk:/{folder}/{file_name}", "url": link2pic}
        encoded_params = urlencode(params)
        # запрос на загрузку c помощью POST
        response = requests.post(
            url_for_upload, headers=self.headers, params=encoded_params
        )
        # проверка статуса запроса
        if response.status_code == 202:
            print("Началась загрузка файла в папку на ЯндексДиск")
        else:
            print(response.json()["message"])


if __name__ == "__main__":
    ya = YA_disk(token)
    ya.create_upload_folder()
    ya.upload_ext_url(
        "test_pic.jpg",
        "https://bmwguide.ru/wp-content/uploads/2016/07/bmw-at-2016-consorso-d-eleganza-bmw-2002-hommage-13.jpg",
    )
