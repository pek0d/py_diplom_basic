import requests  # type: ignore
import pprint
import json
import time

from configuration import VK_TOKEN


pp = pprint.PrettyPrinter(indent=2)


token = VK_TOKEN


class VKAPIclient:
    api_base_url = "https://api.vk.com/method"

    def __init__(self, token):
        self.access_token = token

    def _build_url(self, api_method):
        return f"{self.api_base_url}/{api_method}"

    def common_params(self):
        """Подготовка параметров API"""

        return {"access_token": self.access_token, "v": "5.154"}

    def get_profile_info(self):
        """Получить данные о профиле пользователя"""

        user_url = f"{self.api_base_url}/users.get"
        user_id_input = input("Введите id пользователя VK или его screen_name: ")
        if user_id_input == "":
            user_id_input = self.user_id
        params = self.common_params()
        params.update({"user_ids": user_id_input, "fields": "screen_name"})
        response = requests.get(user_url, params=params)
        # проверка на ошибку
        if "error" in response.json().keys():
            error_message = response.json()["error"]["error_msg"]
            print(f"Произошла ошибка: {error_message}")
            self.user_id = None
            return self.user_id
        else:
            self.user_id = response.json()["response"][0]["id"]
            if "screen_name" in response.json()["response"][0].keys():
                self.screen_name = response.json()["response"][0]["screen_name"]
            else:
                print(f'Короткого имени пользователя "{user_id_input}" нет.')
                return self.user_id

    def get_profile_photos_data(self):
        """Получить данные о фотографиях профиля
        Можно раздробить на 4 функии:
            1. запрос в VK API
            2. подсчет количества фото
            3. проверка по лайкам
            4. запись в json

        """

        # получение id профиля
        profile_id = self.user_id
        # список данных для записи в output-json
        dump = []
        # список данных для загрузки в яндекс диск
        yadisk = []
        # список для выявления повторных количеств лайков
        uniq_name = []
        params = self.common_params()
        params.update(
            {
                "owner_id": profile_id,
                "album_id": "profile",
                "photo_sizes": "1",
                "extended": "1",
            }
        )
        response = requests.get(self._build_url("photos.get"), params=params).json()
        # проверка на доступ к альбому
        try:
            items_response = response["response"]["items"]
        except KeyError:
            print("Доступ к альбому данного пользователя закрыт")
            exit(0)
        # ввод количества фото
        count_photos = input(
            "Сколько (По умолчанию 5) фото из аватарок профиля Вы хотите сохранить?: "
        )
        # проверка на корректность ввода
        try:
            if count_photos == "":
                count_photos = 5
            count_photos = int(count_photos)
        except ValueError:
            print("Некорректное значение, нужно ввести число. Попробуйте еще раз")
            return self.get_profile_photos_data()
        else:
            params.update({"count": count_photos})
            # ответ на запрос по информации для итерации
            # items_response = response["response"]["items"]

        # пробежка по лайкам
        for item in items_response:
            like = item["likes"]["count"]

            # формирование даты загрузки
            photo_upload_date = time.strftime("%Y-%m-%d", time.gmtime(item["date"]))

            # реализация условия для создания имени фото
            if like in uniq_name:
                name = f"{like}_{photo_upload_date}.jpg"
            else:
                name = f"{like}.jpg"

            if like not in uniq_name:
                uniq_name.append(like)

            # формирование ссылки для запроса фото
            max_photo_url, size = self.max_size_photo(item["sizes"])

            # формирование словаря для записи в список копий фото
            data_dump = {"file_name": name, "size": size}

            # формирование словаря для загрузки в яндекс диск
            data_yadisk = {"file_name": name, "size": size, "url": max_photo_url}

            # наполнение списков
            dump.append(data_dump)
            yadisk.append(data_yadisk)

        # запись в файл для яндексДиска
        write_data_to_json("photos_info.json", dump)
        write_data_to_json("for_upload_to_yadisk.json", yadisk)

        return dump, yadisk

    def max_size_photo(self, sizes):
        """Возвращает ссылку на фото с максимальным разрешением"""

        # список копий фото от максимального к минимальному размеру
        types = ["w", "z", "y", "r", "q", "p", "o", "x", "m", "s"]

        # выбор максимального размера по типу, и получение ссылки на фото
        for type in types:
            for size in sizes:
                if size["type"] == type:
                    return size["url"], type


def write_data_to_json(file, data):
    """Запись данных в json"""
    with open(file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    vk_client = VKAPIclient(token)
    vk_client.get_profile_info()
    dump, yadisk = vk_client.get_profile_photos_data()
