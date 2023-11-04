from vkapiclient import VKAPIclient
from yadiskapi import YA_disk

from configuration import VK_TOKEN


def user_interactive() -> None:
    """Взаимодействие с пользователем"""

    print(
        """
        Добро пожаловать в программу по сбору и передаче копий фото из VK в Яндекс Диск!\n
        **** Для доступа к Вашему ЯндексДиску потребуется ввести код из браузера ****\n"""
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

        # вызов методов класса YA_disk
        ya = YA_disk()
        ya.request_confirm_code()
        ya.request_token_with_code()
        ya.create_upload_folder()
        ya.upload_from_json()

        print("\nЗагрузка завершена! Все фото загружены в ЯндексДиск")
        print("\nСписок загруженных копий фото содержится в файле\nphotos_info.json")
        # предлагаем продолжить работу
        ask_user = input("Продолжить работу с программой? (y/n)")
        if ask_user == "y":
            user_interactive()
        else:
            print("До свидания!")
            exit(0)

    elif menu_item == "2":
        print("До свидания!")
        exit(0)
    else:
        print("Некорректный ввод")
        user_interactive()


if __name__ == "__main__":
    user_interactive()
