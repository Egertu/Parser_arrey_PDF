import pdfplumber
import re


def extract_unique_words_with_tags(pdf_path, tags, remove_duplicates=False):
    """
    Извлечение слов с несколькими тегами из PDF с возможностью удаления дублей.

    Args:
        pdf_path (str): Путь к PDF файлу.
        tags (list): Список тегов, по которым фильтруются слова (например, ['BGB', 'TAG2']).
        remove_duplicates (bool): Если True, удаляет дубли на всех страницах.

    Returns:
        list: Список слов с тегами.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_words = []  # Список для всех слов с тегами

            for i, page in enumerate(pdf.pages):
                print(f"[DEBUG] Обработка страницы {i + 1}...")
                text = page.extract_text()
                if text:
                    # Разделяем текст на строки и затем на слова
                    lines = text.split("\n")
                    page_words = []  # Список для слов на текущей странице

                    for line in lines:
                        words = line.split()
                        # Фильтруем слова с указанными тегами
                        for tag in tags:
                            tagged_words = [
                                re.sub(r'[^a-zA-Z0-9\.\-]', '', word)  # Убираем только ненужные символы
                                for word in words
                                if re.search(rf'\b\w*{tag}\w*\b', word)
                            ]
                            page_words.extend(tagged_words)

                    # Если нужно удалить дубли, то делаем это на уровне всей страницы
                    if remove_duplicates:
                        page_words = list(set(page_words))  # Удаляем дубли на этой странице

                    # Добавляем слова страницы в общий список
                    all_words.extend(page_words)  # Добавляем без использования множества, чтобы сохранить порядок
                    print(f"[DEBUG] Найдено слов с тегами {tags} на странице {i + 1}: {len(page_words)}")

                else:
                    print(f"[DEBUG] Текст на странице {i + 1} отсутствует.")

            # Если дубли должны быть удалены по всему документу, делаем это здесь
            if remove_duplicates:
                all_words = list(set(all_words))  # Удаляем дубли в документе

            unique_words = sorted(all_words)  # Сортируем для удобства
            print("[DEBUG] Извлечение слов завершено. Всего уникальных слов с тегами:", len(unique_words))
            return unique_words

    except FileNotFoundError:
        print("[ERROR] Файл не найден:", pdf_path)
        return []
    except Exception as e:
        print("[ERROR] Произошла ошибка:", e)
        return []


def process_two_pdfs(pdf_path1, pdf_path2, tags, remove_duplicates_for_pdf1=False, remove_duplicates_for_pdf2=False):
    """
    Обработка двух PDF файлов с разной логикой удаления дублей.

    Args:
        pdf_path1 (str): Путь к первому PDF файлу.
        pdf_path2 (str): Путь ко второму PDF файлу.
        tags (list): Список тегов для поиска в обоих файлах.
        remove_duplicates_for_pdf1 (bool): Если True, удаляет дубли для первого PDF.
        remove_duplicates_for_pdf2 (bool): Если True, удаляет дубли для второго PDF.

    Returns:
        tuple: Два списка с уникальными словами для каждого PDF файла.
    """
    # Обрабатываем первый PDF с указанным флагом для удаления дублей
    print(f"[INFO] Обработка первого PDF: {pdf_path1}")
    unique_words_pdf1 = extract_unique_words_with_tags(pdf_path1, tags, remove_duplicates=remove_duplicates_for_pdf1)

    # Обрабатываем второй PDF с указанным флагом для удаления дублей
    print(f"[INFO] Обработка второго PDF: {pdf_path2}")
    unique_words_pdf2 = extract_unique_words_with_tags(pdf_path2, tags, remove_duplicates=remove_duplicates_for_pdf2)

    return unique_words_pdf1, unique_words_pdf2