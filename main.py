from configuration import VK_TOKEN
import requests  # type: ignore
import pprint

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

    def user_info(self):
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
            return self.user_id
        try:
            self.screen_name = response.json()["response"][0]["screen_name"]
        except IndexError:
            print("Пользователя с таким screen_name не существует")
            return self.user_id

    def get_profile_photos(self):
        count_photos = input(
            "Сколько фото из профиля хотите сохранить?: (По умолчанию 5)"
        )
        try:
            if count_photos == "":
                count_photos = 5
            count_photos = int(count_photos)
        except ValueError:
            print("Некорректное значение")
            return self.get_profile_photos()
        params = self.common_params()
        params.update(
            {
                "owner_id": self.user_id,
                "album_id": "profile",
                "photo_sizes": "1",
                "extended": "1",
                "count": count_photos,
            }
        )
        response = requests.get(self._build_url("photos.get"), params=params)
        # with open("get_photos.json", "w") as f:
        #     json.dump(response.json(), f, indent=2)
        return response.json()

    def get_photos_info(self):
        response = self.get_profile_photos()
        items_response = response["response"]["items"]
        photos_info_lst = []
        info_dict = {}
        for item in items_response:
            likes = item["likes"]["count"]
            info_dict = {"size": item["sizes"][-5]["type"]}
            info_dict["file_name"] = f"{likes}.jpg"
            photos_info_lst.append(info_dict)
        pp.pprint(photos_info_lst)
        return photos_info_lst

    def get_photos_urls(self):
        profile_photos = self.get_profile_photos()
        target_photo_size = "z"
        photos_urls_lst = []
        for photo in profile_photos["response"]["items"]:
            for size in photo["sizes"]:
                if size["type"] == target_photo_size:
                    photos_urls_lst.append(size["url"])
        pp.pprint(photos_urls_lst)
        return photos_urls_lst


if __name__ == "__main__":
    vk_client = VKAPIclient(token, 827020295)
    vk_client.user_info()
    vk_client.get_photos_urls()
    vk_client.get_photos_info()
