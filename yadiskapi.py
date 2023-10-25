from configuration import YA_TOKEN, CLIENT_ID_YA_APP
import requests  # type: ignore
import pprint
import pysnooper  # type: ignore
import json
import time
from urllib.parse import urlencode
from enlighten import get_manager  # type: ignore
import webbrowser

pp = pprint.PrettyPrinter(indent=2)

token = YA_TOKEN
client_id = CLIENT_ID_YA_APP


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
    def request_confirmantion_code(self):
        """Получение кода подтверждения от пользователя"""
        url = "https://oauth.yandex.ru/authorize?response_type=code"
        params = {"client_id": client_id}
        response = requests.get(url, params=params)
        webbrowser.open(response.url)

    @pysnooper.snoop()
    def request_token(self):
        """Получение токена для доступа к API"""
        code = input("Введите код подтверждения из браузера: ")
        params = {
            "grant_type": "authorization_code",
            "code": code,
        }
        encoded_params = urlencode(params)
        response = requests.post(
            "https://oauth.yandex.ru/", params=encoded_params)
        if response.status_code == 200:
            self.user_access_token = response.json()["access_token"]
        else:
            print(response.json()["error_description"])

        return self.user_access_token

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

    # @pysnooper.snoop()
    def upload_ext_url(self, file_name, link2pic):
        """Загрузить файл на диск с указанной (внешеней) ссылкой"""
        # формирование ссылки для запроса
        url_for_upload = self._build_url("resources/upload")
        # объявление имени папки из ранее заданного имени
        folder = f"{self.dir_name}"
        params = {"path": f"disk:/{folder}/{file_name}", "url": link2pic}
        # кодирование параметров согласно требованию документации Яндекса
        encoded_params = urlencode(params)
        # запрос на загрузку c помощью POST
        response = requests.post(
            url_for_upload, headers=self.headers, params=encoded_params
        )
        # проверка статуса запроса
        if response.status_code == 202:
            # начало работы статус-бара
            with get_manager() as manager:
                with manager.counter(
                    total=100, desc=f"Загрузка {file_name}", unit="%"
                ) as pbar:
                    for _ in range(100):
                        time.sleep(0.05)
                        pbar.update()
            print(
                """Список загруженных копий фото содержится в файле\nphotos_info.json"""
            )

        else:
            print(response.json()["message"])

    # @pysnooper.snoop()
    def upload_from_json(self):
        """Загрузить на Диск по ссылкам из json"""
        with open("for_upload_to_yadisk.json") as f:
            data = json.load(f)
            for photo_url in data:
                self.upload_ext_url(photo_url["file_name"], photo_url["url"])


if __name__ == "__main__":
    ya = YA_disk(token)
    ya.request_confirmantion_code()
    ya.request_token()
    # ya.create_upload_folder()
    # ya.upload_from_json()
