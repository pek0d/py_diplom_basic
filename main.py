from configuration import VK_TOKEN
import requests  # type: ignore
import pprint
import json
import time

pp = pprint.PrettyPrinter(indent=2)


token = VK_TOKEN


class VKAPIclient:
    api_base_url = "https://api.vk.com/method"

    def __init__(self, token, user_id):
        self.access_token = token
        self.user_id = user_id

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
        profile_id = self.user_id
        count_photos = input(
            "Сколько фото из аватарок профиля Вы хотите сохранить?(По умолчанию 5): "
        )
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
        # with open("get_photos.json", "w") as f:
        #     json.dump(response.json(), f, indent=2)
        try:
            items_response = response["response"]["items"]
        except KeyError:
            print("Доступ к альбому данного пользователя закрыт")
        else:
            photos_info_lst = []
            photos_urls_lst = []
            info_dict = {}
            target_photo_size = "z"
            likes_count_lst = []
            repeated_likes_count_lst = []
            items_response = response["response"]["items"]

            for like in items_response:
                likes_count_lst.append(like["likes"]["count"])
            for like in likes_count_lst:
                if likes_count_lst.count(like) > 1:
                    repeated_likes_count_lst.append(like)

            for item in items_response:
                like = item["likes"]["count"]
                photo_upload_date = time.strftime(
                    "%Y-%m-%d", time.gmtime(item["date"]))

                if like in repeated_likes_count_lst:
                    info_dict["file_name"] = f"{like}_{photo_upload_date}.jpg"
                    photos_info_lst.append(info_dict)
                else:
                    info_dict["file_name"] = f"{like}.jpg"
                    photos_info_lst.append(info_dict)

                info_dict["size"] = item["sizes"][-1]["type"]
                photos_info_lst.append(info_dict)
                # pp.pprint(info_dict)
                pp.pprint(photos_info_lst)

                # Сохранение полученных данных в файл
                with open("photos_info.json", "w") as f:
                    json.dump(photos_info_lst, f, indent=2)

            # получение ссылок на фотографии
            for item in items_response:
                for photo_size in item["sizes"]:
                    if photo_size["type"] == target_photo_size:
                        photos_urls_lst.append(photo_size["url"])

            return photos_urls_lst


if __name__ == "__main__":
    vk_client = VKAPIclient(token, 827020295)
    vk_client.get_profile_info()
    vk_client.get_profile_photos_data()
