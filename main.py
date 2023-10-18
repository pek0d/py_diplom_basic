import requests  # type: ignore
import pprint
import os
from urllib.parse import urlencode
import json
from configuration import TOKEN

# Запрос id пользователя (827020295)
vk_user_id_input = input("Введите id пользователя VK: ")
try:
    vk_user_id = int(vk_user_id_input)
except TypeError:
    print("нужно ввести только цифры")


token = TOKEN


class VKAPIclient:
    api_base_url = "https://api.vk.com/method"

    def __init__(self, token, user_id):
        self.access_token = token
        self.user_id = user_id

    def _build_url(self, api_method):
        return f"{self.api_base_url}/{api_method}"

    def common_params(self):
        return {"access_token": self.access_token, "v": "5.154"}

    def get_status(self):
        params = self.common_params()
        params.update({"user_id": self.user_id})
        r = requests.get(self._build_url("status.get"), params=params)
        return r.json().get("response", {}).get("text")

    def set_status(self, new_status):
        params = self.common_params()
        params.update({"user_id": self.user_id, "text": new_status})
        r = requests.get(self._build_url("status.set"), params=params)
        r.raise_for_status()

    def replace_status(self, target, replace_string):
        status = self.get_status()
        new_status = status.replace(target, replace_string)
        self.set_status(new_status)

    def get_profile_photos(self):
        params = self.common_params()
        params.update(
            {"owner_id": self.user_id, "album_id": "profile", "photo_sizes": "1"}
        )
        r = requests.get(self._build_url("photos.get"), params=params)
        return r.json()

    def get_max_photo_size_url(self):
        profile_photos = self.get_profile_photos()
        target_size = "o"
        for photo in profile_photos["response"]["items"]:
            for photo_size in photo["sizes"]:
                if photo_size["type"] == target_size:
                    photo_size["url"]
                return photo_size


if __name__ == "__main__":
    vk_client = VKAPIclient(token, 827020295)
    # pprint.pprint(vk_client.get_status())
    # vk_client.replace_status("Hello", "World")
    # photos_info = vk_client.get_profile_photos()
    photo_size = vk_client.get_max_photo_size_url()
    pprint.pprint(photo_size)
