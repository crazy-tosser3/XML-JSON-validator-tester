import json
import re
import datetime
import time


def JSONloader(json_path: str):
    raw_data = dict()
    with open(json_path) as f:
        raw_data = json.load(f)
    return raw_data


def calculate_age(date_of_birth_str):
    date_of_birth = datetime.datetime.strptime(date_of_birth_str, "%Y-%m-%d")
    today = datetime.datetime.today()
    age = (
        today.year
        - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )
    return age


def JSONvalidate(json_path: str):
    """
    ФУНКЦИЯ ДЛЯ ВАЛИДАЦИИ email, address, date_of_birth, phone_number

    Аргументы:
        json_path (str): путь к JSON файлу

    Возвращает:
        dict: словарь с ошибками и временем валидации
    """
    start_time = time.time()

    raw_data = JSONloader(json_path)
    errors = []
    keys = [
        "name",
        "email",
        "address",
        "date_of_birth",
        "phone_number",
        "job",
        "company",
    ]

    for person in raw_data:
        person_name = person.get("name", "Unknown")

        for field in keys:
            if field not in person:
                errors.append(f"[{person_name}] Отсутствует поле: {field}")

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, person.get("email", "")):
            errors.append(f"[{person_name}] Email некорректен")

        try:
            dob = person.get("date_of_birth", "")
            datetime.datetime.strptime(dob, "%Y-%m-%d")
            age = calculate_age(dob)
            if age < 18:
                errors.append(
                    f"[{person_name}] Возраст меньше 18 лет — регистрация невозможна"
                )
            if age > 100:
                errors.append(
                    f"[{person_name}] Возраст вне допустимого диапазона (18-100)"
                )
        except ValueError:
            errors.append(
                f"[{person_name}] Дата рождения некорректна (формат YYYY-MM-DD)"
            )

        phone_regex = r"^\d{1,3}-\d{3}-\d{3}-\d{4}$"
        if not re.match(phone_regex, person.get("phone_number", "")):
            errors.append(f"[{person_name}] Телефон некорректен")

        if len(person.get("address", "")) < 5:
            errors.append(f"[{person_name}] Адрес некорректен")

    validation_time_ms = (time.time() - start_time) * 1000

    return {
        "status": "valid" if len(errors) == 0 else "invalid",
        "errors": errors,
        "validation_time_ms": round(validation_time_ms, 2),
    }


if __name__ == "__main__":
    result = JSONvalidate("data.json")
    print(f"Статус: {result['status']}")
    print(f"Ошибок: {len(result['errors'])}")
    print(f"Время валидации: {result['validation_time_ms']} мс")
    if result["errors"]:
        for error in result["errors"]:
            print(f"  - {error}")
