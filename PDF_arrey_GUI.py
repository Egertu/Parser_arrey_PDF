import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from Parser_pdf_RD import process_two_pdfs  # Импортируем парсер из кода №1
from Parser_pdf_CO import parse_pdf_with_decimal_ranges  # Импортируем парсер из кода №3

# Настройка темы
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Функции для интерфейса
def browse_file1():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    entry_file1.delete(0, ctk.END)
    entry_file1.insert(0, file_path)

def browse_file2():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    entry_file2.delete(0, ctk.END)
    entry_file2.insert(0, file_path)

def browse_output_dir():
    output_dir = filedialog.askdirectory()
    entry_output_dir.delete(0, ctk.END)
    entry_output_dir.insert(0, output_dir)

def start_process():
    file_path1 = entry_file1.get()
    file_path2 = entry_file2.get()
    tags_input = entry_tags.get().strip()
    remove_duplicates_1 = var_remove_duplicates_1.get()
    remove_duplicates_2 = var_remove_duplicates_2.get()
    output_dir = entry_output_dir.get().strip()

    if not (file_path1 and file_path2 and tags_input):
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля.")
        return

    # Преобразуем теги из строки в список
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    if not tags:
        messagebox.showerror("Ошибка", "Введите хотя бы один тег.")
        return

    # Генерация пути для выходной папки, если пользователь не указал папку
    if not output_dir:
        timestamp = datetime.now().strftime("%d%m%Y_%H_%M_%S")
        output_dir = os.path.join(os.path.dirname(file_path1), f"output_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Извлечение имен файлов (без пути и расширения)
        pdf1_name = os.path.basename(file_path1)
        pdf2_name = os.path.basename(file_path2)

        # Обрабатываем первый PDF с парсингом из кода №1
        unique_to_pdf1, unique_to_pdf2 = process_two_pdfs(
            file_path1, file_path2, tags,
            remove_duplicates_for_pdf1=remove_duplicates_1,
            remove_duplicates_for_pdf2=remove_duplicates_2
        )

        # Обрабатываем второй PDF с парсингом из кода №3
        allowed_tags = tags  # Используем те же теги для второго PDF
        result_pdf2 = parse_pdf_with_decimal_ranges(file_path2, allowed_tags)

        # Оставляем только уникальные слова, которые есть в одном документе, но отсутствуют в другом
        unique_words_pdf1_only = set(unique_to_pdf1) - set(unique_to_pdf2)
        unique_words_pdf2_only = set(unique_to_pdf2) - set(unique_to_pdf1)

        # Исключаем из уникальных слов те, которые находятся в диапазонах второго документа
        for tag, numbers in result_pdf2.items():
            for num in numbers:
                # Убираем из уникальных слов те теги, которые совпадают с диапазонами
                # Попробуем преобразовать слово в число и проверить, является ли оно в диапазоне
                for word in list(unique_words_pdf1_only):  # Проходим по копии, чтобы избежать изменений во время итерации
                    try:
                        # Проверяем, если строка начинается с тега, и является ли остаток числом
                        if word.startswith(tag):
                            word_number = float(word.replace(tag, ''))
                            if round(word_number, 1) == round(num, 1):
                                unique_words_pdf1_only.discard(word)
                    except ValueError:
                        # Если не удается преобразовать строку в число, продолжаем без изменений
                        continue

        # Путь к итоговому файлу
        output_file = os.path.join(output_dir, "output_unique_words.txt")

        # Запись уникальных слов
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Уникальные слова в '{pdf1_name}':\n")
            for word in sorted(unique_words_pdf1_only):
                f.write(f"{word}\n")
            f.write("\n")

            f.write(f"Уникальные слова в '{pdf2_name}':\n")
            for word in sorted(unique_words_pdf2_only):
                f.write(f"{word}\n")

            # Запись результатов из парсинга для второго документа
            f.write("\nРезультаты для второго документа:\n")
            for tag, numbers in result_pdf2.items():
                f.write(f"Тег: {tag}, Диапазон: {numbers}\n")

        messagebox.showinfo("Завершено", f"Обработка завершена.\nРезультаты сохранены в папке:\n{output_dir}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


# Настройка основного окна
root = ctk.CTk()
root.title("Сравнение PDF файлов по тегам")
root.geometry("800x500")

# Заголовок
label_header = ctk.CTkLabel(root, text="Сравнение PDF файлов по тегам", font=ctk.CTkFont(size=20, weight="bold"))
label_header.pack(pady=20)

# Поле для ввода тегов
frame_tags = ctk.CTkFrame(root)
frame_tags.pack(fill="x", padx=20, pady=5)

label_tags = ctk.CTkLabel(frame_tags, text="Теги для поиска (через запятую):")
label_tags.pack(side="left", padx=5)

entry_tags = ctk.CTkEntry(frame_tags, width=400)
entry_tags.pack(side="left", padx=5)

# Поле для первого файла
frame_file1 = ctk.CTkFrame(root)
frame_file1.pack(fill="x", padx=20, pady=5)

label_file1 = ctk.CTkLabel(frame_file1, text="РД:")
label_file1.pack(side="left", padx=5)

entry_file1 = ctk.CTkEntry(frame_file1, width=400)
entry_file1.pack(side="left", padx=5)

button_browse_file1 = ctk.CTkButton(frame_file1, text="Обзор", command=browse_file1)
button_browse_file1.pack(side="right", padx=5)

# Поле для второго файла
frame_file2 = ctk.CTkFrame(root)
frame_file2.pack(fill="x", padx=20, pady=5)

label_file2 = ctk.CTkLabel(frame_file2, text="СО:")
label_file2.pack(side="left", padx=5)

entry_file2 = ctk.CTkEntry(frame_file2, width=400)
entry_file2.pack(side="left", padx=5)

button_browse_file2 = ctk.CTkButton(frame_file2, text="Обзор", command=browse_file2)
button_browse_file2.pack(side="right", padx=5)

# Поле для папки сохранения
frame_output = ctk.CTkFrame(root)
frame_output.pack(fill="x", padx=20, pady=5)

label_output_dir = ctk.CTkLabel(frame_output, text="Папка для сохранения:")
label_output_dir.pack(side="left", padx=5)

entry_output_dir = ctk.CTkEntry(frame_output, width=400)
entry_output_dir.pack(side="left", padx=5)

button_browse_output_dir = ctk.CTkButton(frame_output, text="Обзор", command=browse_output_dir)
button_browse_output_dir.pack(side="right", padx=5)

# Чекбоксы для удаления дублей
var_remove_duplicates_1 = ctk.BooleanVar(value=True)
check_duplicates_1 = ctk.CTkCheckBox(root, text="Удалять дубли в первом PDF", variable=var_remove_duplicates_1)
check_duplicates_1.pack(pady=5)

var_remove_duplicates_2 = ctk.BooleanVar(value=False)
check_duplicates_2 = ctk.CTkCheckBox(root, text="Удалять дубли во втором PDF", variable=var_remove_duplicates_2)
check_duplicates_2.pack(pady=5)

# Кнопка запуска
button_start = ctk.CTkButton(root, text="Запустить", command=start_process)
button_start.pack(pady=20)

root.mainloop()
