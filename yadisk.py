# тест API яндекс-диск
import requests  # type: ignore
import pprint
from configuration import YA_TOKEN

token = YA_TOKEN
headers_dict = {"Authorization": token}

# создание папки на Яндекс диск
params_dict = {"path": "pics_from_VK"}
r = requests.put(
    "https://cloud-api.yandex.net/v1/disk/resources",
    params=params_dict,
    headers=headers_dict,
)
# pprint.pprint(r.json())


# Запрос адреса загрузки
params_upload_dict = {"path": "pics_from_VK/bmwi7.jpg"}
r = requests.get(
    "https://cloud-api.yandex.net/v1/disk/resources/upload",
    params=params_upload_dict,
    headers=headers_dict,
)
pprint.pprint(r.json())
url_for_upload = r.json()["href"]


# Загрузка файла
with open("bmwi7.jpg", "rb") as f:
    r_upload = requests.put(
        url=url_for_upload,
        files={"file": f},
    )
    pprint.pprint(r_upload)
