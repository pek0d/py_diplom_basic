from configuration import VK_TOKEN
import requests  # type: ignore
import pprint
import json

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
            "Сколько фото из альбома аватарок профиля Вы хотите сохранить?\n(По умолчанию 5): "
        )
        try:
            if count_photos == "":
                count_photos = 5
            count_photos = int(count_photos)
        except ValueError:
            print("Некорректное значение, нужно ввести число. Попробуйте еще раз")
            return self.get_profile_photos_data()
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
            return self.get_profile_info()
        photos_info_lst = []
        photos_urls_lst = []
        info_dict = {}
        target_photo_size = "z"
        for item in items_response:
            likes = item["likes"]["count"]
            info_dict["size"] = item["sizes"][0]["type"]
            info_dict["file_name"] = f"{likes}.jpg"
            photos_info_lst.append(info_dict)
            for size in item["sizes"]:
                if size["type"] == target_photo_size:
                    photos_urls_lst.append(size["url"])

        pp.pprint(photos_info_lst)
        pp.pprint(photos_urls_lst)

        return photos_info_lst, photos_urls_lst


if __name__ == "__main__":
    vk_client = VKAPIclient(token, 827020295)
    vk_client.get_profile_info()
    vk_client.get_profile_photos_data()
