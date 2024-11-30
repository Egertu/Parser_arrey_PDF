import re
import pdfplumber


def parse_pdf_with_decimal_ranges(file_path, allowed_tags):
    """
    Парсер PDF для извлечения слов и диапазонов, включая дробные значения.

    :param file_path: Путь к PDF файлу.
    :param allowed_tags: Список тегов для фильтрации (например, ["ASS", "AMV"]).
    :return: Словарь с найденными тегами и их диапазонами.
    """
    # Константы для преобразования в пункты
    left_margin_mm = 43  # Отступ от левого края в миллиметрах
    left_margin_pts = left_margin_mm * 2.83465  # Переводим в пункты

    # Регулярные выражения для тегов и диапазонов
    single_tag_pattern = re.compile(r'\b([A-Z]+)(\d+\.\d+)\b')
    range_tag_pattern = re.compile(
        r'\b([A-Z]+)(\d+\.\d+)\s*-\s*\s*([A-Z]+)?(\d+\.\d+)\b'
    )
    unwanted_text_pattern = re.compile(r'\b(монитор|шт|DNS|27"|\d{6,})\b', re.IGNORECASE)

    found_tags = {tag: set() for tag in allowed_tags}

    try:
        with pdfplumber.open(file_path) as pdf:
            # Проходим по всем страницам
            for page in pdf.pages:
                # Чтение только области после левого отступа
                # Параметры: x0 = отступ слева, y0 = 0 (начало по высоте), x1 = 43 мм по горизонтали, y1 = вся высота
                cropped_page = page.within_bbox((0, 0, left_margin_pts, page.height))
                full_text = cropped_page.extract_text()

                if full_text:
                    # Очистка текста
                    cleaned_text = full_text.replace("\n", " ").replace("\r", " ")  # Заменяем переносы строк на пробелы
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Убираем множественные пробелы
                    cleaned_text = re.sub(r'-\s*-', ' ',
                                          cleaned_text)  # Убираем лишние тире "- -" (например, между тегами и описаниями)
                    cleaned_text = unwanted_text_pattern.sub("", cleaned_text)  # Убираем ненужные фрагменты

                    # Выводим очищенный текст для отладки
                    print("Очищенный текст из PDF:")
                    print(cleaned_text)
                    print("\n" + "=" * 50 + "\n")

                    # Ищем диапазоны
                    for match in range_tag_pattern.findall(cleaned_text):
                        tag_start, num_start, tag_end, num_end = match
                        num_start, num_end = float(num_start), float(num_end)

                        # Проверяем, что тег в списке разрешённых
                        if tag_start in allowed_tags and (not tag_end or tag_start == tag_end):
                            # Создаём дробный диапазон
                            current = num_start
                            while current <= num_end:
                                found_tags[tag_start].add(round(current, 1))
                                current += 0.1  # Увеличиваем на 0.1 для дробных чисел
                            print(f"Найден диапазон: {tag_start}{num_start} - {tag_start}{num_end}")

                    # Ищем одиночные теги
                    for tag, num in single_tag_pattern.findall(cleaned_text):
                        num = float(num)
                        if tag in allowed_tags:
                            found_tags[tag].add(num)
                            print(f"Найдено: {tag}{num}")

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

    # Сортируем результаты
    for tag in found_tags:
        found_tags[tag] = sorted(found_tags[tag])

    return found_tags





