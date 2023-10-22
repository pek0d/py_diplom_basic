from configuration import VK_TOKEN
import requests  # type: ignore
import pprint
import json
import time

pp = pprint.PrettyPrinter(indent=2)


token = VK_TOKEN


class VKAPIclient:
    api_base_url = "https://api.vk.com/method"

    def __init__(self, token):
        self.access_token = token
        # self.user_id = user_id

    def _build_url(self, api_method):
        return f"{self.api_base_url}/{api_method}"

    def common_params(self):
        return {"access_token": self.access_token, "v": "5.154"}

    def get_profile_info(self):
        user_url = f"{self.api_base_url}/users.get"
        user_id_input = input(
            "Введите id пользователя VK или его screen_name: ")
        if user_id_input == "":
            user_id_input = self.user_id
        params = self.common_params()
        params.update({"user_ids": user_id_input, "fields": "screen_name"})
        response = requests.get(user_url, params=params)
        if "error" in response.json().keys():
            error_message = response.json()["error"]["error_msg"]
            print(f"Произошла ошибка: {error_message}")
            self.user_id = None
            return self.user_id
        else:
            self.user_id = response.json()["response"][0]["id"]
            if "screen_name" in response.json()["response"][0].keys():
                self.screen_name = response.json(
                )["response"][0]["screen_name"]
            else:
                print(f'Короткого имени пользователя "{user_id_input}" нет.')
                return self.user_id

    def get_profile_photos_data(self):
        """Получить данные о фотографиях профиля"""

        # список для записи в json
        dump = []
        # список для загрузки в яндекс диск
        yadisk = []
        uniq_name = []

        profile_id = self.user_id
        count_photos = input(
            "Сколько фото из аватарок профиля Вы хотите сохранить?(По умолчанию 5): "
        )
        # проверка на корректность ввода
        try:
            if count_photos == "":
                count_photos = 5
            count_photos = int(count_photos)
        except ValueError:
            print("Некорректное значение, нужно ввести число. Попробуйте еще раз")
        params = self.common_params()
        params.update(
            {
                "owner_id": profile_id,
                "album_id": "profile",
                "photo_sizes": "1",
                "extended": "1",
                "count": count_photos,
            }
        )
        response = requests.get(self._build_url(
            "photos.get"), params=params).json()
        # проверка на доступ к альбому
        try:
            items_response = response["response"]["items"]
        except KeyError:
            print("Доступ к альбому данного пользователя закрыт")
        else:
            items_response = response["response"]["items"]

            for item in items_response:
                like = item["likes"]["count"]

                photo_upload_date = time.strftime(
                    "%Y-%m-%d", time.gmtime(item["date"]))

                if like in uniq_name:
                    name = f"{like}_{photo_upload_date}.jpg"
                else:
                    name = f"{like}.jpg"

                if like not in uniq_name:
                    uniq_name.append(like)

                max_photo_url, size = self.max_size_photo(item["sizes"])

                data_dump = {"file_name": name, "size": size}

                data_yadisk = {"file_name": name,
                               "size": size, "url": max_photo_url}

                dump.append(data_dump)
                yadisk.append(data_yadisk)

                with open("photos_info.json", "w") as f:
                    json.dump(dump, f, indent=2)
                # with open("photos_yadisk.json", "w") as f:
                #     json.dump(yadisk, f, indent=2)

        return dump, yadisk

    def max_size_photo(self, sizes):
        """Возвращает ссылку на фото с максимальным разрешением"""

        # список копий фото от максимального к минимальному размеру
        types = ["w", "z", "y", "r", "q", "p", "o", "x", "m", "s"]

        for type in types:
            for size in sizes:
                if size["type"] == type:
                    return size["url"], type


if __name__ == "__main__":
    vk_client = VKAPIclient(token)
    vk_client.get_profile_info()
    dump, yadisk = vk_client.get_profile_photos_data()
    print(dump)
    print("*" * 88)
    print(yadisk)
