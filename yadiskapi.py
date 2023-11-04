from urllib.parse import urlencode

import requests  # type: ignore
import pprint
import json
import time
import sys
import base64
import webbrowser

from configuration import CLIENT_ID_YA_APP, CLIENT_YA_APP_SECRET

pp = pprint.PrettyPrinter(indent=2)

# credentials for app
client_id = CLIENT_ID_YA_APP
client_secret = CLIENT_YA_APP_SECRET


class YA_disk:
    api_base_url = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self):
        self.client_id = client_id
        self.client_secret = client_secret

    def _build_url(self, api_method) -> str:
        """Формирование ссылки на API"""

        return f"{self.api_base_url}/{api_method}"

    def _write_responses(self, response) -> None:
        """Запись ответа в json для отладки"""

        with open("response_info.json", "w") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

    def request_confirm_code(self) -> None:
        """Получение кода подтверждения от пользователя"""

        redirect_uri = "https://oauth.yandex.ru/verification_code"
        url_to_get_code = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={client_id}&{redirect_uri}"
        user_input = input(
            "Для предоставления доступа к Вашему ЯндексДиску вам необходимо ввести код из браузера. Продолжить? (y/n)"
        )
        if user_input in ["y", "yes", "да", "д", "Y"]:
            webbrowser.open(url_to_get_code)
        else:
            print("До свидания!")
            exit(0)

    def request_token_with_code(self) -> str:
        """Получение токена для доступа к API на основе кода подтверждения"""

        # формирование заголовков
        client_credentials = f"{self.client_id}:{self.client_secret}"
        encoded_client_credentials = base64.b64encode(
            client_credentials.encode())
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_client_credentials.decode()}",
        }
        # формирование тела запроса
        code = input(
            "Для доступа к Вашему ЯндексДиску введите код подтверждения из браузера: "
        )
        data = {
            "grant_type": "authorization_code",
            "code": code.strip(),
        }
        payload = urlencode(data)
        # запрос на получение токена
        response = requests.post(
            "https://oauth.yandex.ru/token", headers=headers, data=payload
        )
        if response.status_code == 200:
            self.user_access_token = response.json()["access_token"]
        else:
            print(response.json()["error_description"])

        return self.user_access_token

    def create_upload_folder(self) -> str:
        """Создание папки для загрузки"""

        url = self._build_url("resources")
        # формирование параметров запроса
        folder_name = input("Введите имя папки для загрузки: ")
        self.dir_name = folder_name
        params = {"path": folder_name}
        # запрос на создание папки
        response = requests.put(
            url,
            headers={"Authorization": f"{self.user_access_token}"},
            params=params,
        )
        # проверка статуса запроса
        if response.status_code == 201:
            print(f"Папка с названием {folder_name} создана")
        else:
            print(response.json()["message"])

        return self.dir_name

    def upload_ext_url(self, file_name: str, link2pic: str) -> None:
        """Загрузить файл на диск с указанной(внешеней) ссылкой"""

        url_for_upload = self._build_url("resources/upload")
        # объявление имени папки из ранее заданного имени
        folder = self.dir_name
        # формирование параметров
        params = {"path": f"disk:/{folder}/{file_name}", "url": link2pic}
        encoded_params = urlencode(params)
        # запрос на загрузку c помощью POST
        response = requests.post(
            url_for_upload,
            headers={"Authorization": f"{self.user_access_token}"},
            params=encoded_params,
        )

    def upload_from_json(self) -> None:
        """Загрузить на Диск по ссылкам из json"""
        with open("for_upload_to_yadisk.json") as f:
            data = json.load(f)
            for _, photo_url in enumerate(data):
                sim_bar(_, data, bar_length=30)
                time.sleep(0.05)
                self.upload_ext_url(photo_url["file_name"], photo_url["url"])


def sim_bar(
    iteration: int, total: list, bar_length: int = 50, symbol: str = "🟦"
) -> None:
    """Функция для вывода прогресс-бара"""

    total = len(total)
    progress = (iteration + 1) / total
    arrow = symbol * int(round(bar_length * progress))
    spaces = " " * (bar_length - len(arrow))
    sys.stdout.write(f"\r[{arrow}{spaces}] {int(progress * 100)}%")
    sys.stdout.flush()


if __name__ == "__main__":
    ya = YA_disk()
    ya.request_confirm_code()
    ya.request_token_with_code()
    ya.create_upload_folder()
    ya.upload_from_json()
