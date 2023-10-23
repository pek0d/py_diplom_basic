from configuration import VK_TOKEN  # YA_TOKEN

from vkapiclient import VKAPIclient
from yadiskapi import YA_disk


def user_interactive():
    """Взаимодействие с пользователем"""

    print(
        "Добро пожаловать в программу по сбору и передаче копий фото из VK в Яндекс Диск!\n"
    )
    print("Выберите действие: ")

    menu_item = input(
        """-*- Для продолжения - нажмите 1\n-*- Для выхода - нажмите 2\n"""
    )
    vk = VKAPIclient(VK_TOKEN)
    if menu_item == "1":
        # вызов методов класса VKAPIclient
        vk.get_profile_info()
        vk.get_profile_photos_data()

        # запрос пользовательского токена
        user_ya_token = input("Введите Ваш токен Яндекс Диска: ")
        ya = YA_disk(user_ya_token)

        ya.create_upload_folder()
        ya.upload_from_json()

    elif menu_item == "2":
        print("До свидания!")
        exit(0)
    else:
        print("Некорректный ввод")
        user_interactive()


if __name__ == "__main__":
    user_interactive()
