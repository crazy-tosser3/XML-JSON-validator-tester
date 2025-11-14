from My_modules.mocdatacreator import CreateMOCDATA
from My_modules.txtfocumentparser import data_parser
from typing import Any, Dict
from lxml import etree as ET
import json
import os


def createJSONfile(data: dict, file_name: str = "data.json") -> None:
    """
    Сохраняет переданные данные в JSON-файл.

    Функция принимает Python-объект (Словарь),
    и записывает его содержимое в файл `data.json`
    в текущей директории в читаемом (форматированном) виде.

    Пример структуры данных, которую функция может сохранять:
    {
        "name": "Katelyn Galloway",
        "email": "lauragarcia@example.com",
        "address": "1632 Fred Ville Mikaylaview, AL 84257",
        "date_of_birth": "1984-10-13",
        "phone_number": "531.789.5243x89872",
        "job": "Scientist",
        "company": "research (physical sciences), Moore and Sons"
    }

    Параметры:
        data (dict): Словарь с данными, которые нужно записать в JSON-файл.

    Возвращает:
        None
    """
    with open(file_name, "w") as j:
        json.dump(data, j, indent=3)


def createXMLfile(
    data: Dict[str, Any],
    file_name: str = "data.xml",
    root_tag: str = "user_data",
    pretty: bool = True,
) -> None:
    """
    Создаёт XML-файл из вложенного словаря.
    Поддерживает dict, list и скалярные значения.
    Использует lxml для красивого отступа, если установлен.
    """

    def build_xml(parent, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                el = ET.SubElement(parent, k)
                build_xml(el, v)
        elif isinstance(obj, list):
            for item in obj:
                item_el = ET.SubElement(parent, "item")
                build_xml(item_el, item)
        else:
            parent.text = "" if obj is None else str(obj)

    root = ET.Element(root_tag)
    build_xml(root, data)

    try:
        tree = ET.ElementTree(root)
        tree.write(
            file_name, pretty_print=bool(pretty), xml_declaration=True, encoding="utf-8"
        )

    except OSError as e:
        print(f"Ошибка при записи в XML: {e}")


def createFiles():
    """В КОДЕ БУДУ ВЫЗЫВАИТЬ ИММЕННО ЭТОТ МЕТОД, Т.К ОН СРАЗУ СОБЕРЁТ ВСЕ НУЖНЫЕ ФАЙЛЫ"""
    path = "Raw_Data"
    file_list = os.listdir(path)
    print(file_list)

    all_raw_data = list()

    for f in file_list:
        raw_data_person = data_parser.data_parse(os.path.join(path, f))
        all_raw_data += raw_data_person

    createJSONfile(all_raw_data)
    createXMLfile(all_raw_data)


if __name__ == "__main__":
    if not os.path.exists("Raw_Data"):
        os.mkdir("Raw_Data")
    count = int(input("Введите кол-во данных для генерации\n-> "))
    CreateMOCDATA.create_moc(count, "Raw_Data")
    createFiles()
