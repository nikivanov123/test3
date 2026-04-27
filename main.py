import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog


class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "movies.json"

        # Список фильмов
        self.movies = []

        # Загрузка данных из JSON
        self.load_data()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

    def create_widgets(self):
        # === Фрейм для ввода данных ===
        input_frame = LabelFrame(self.root, text="Добавление фильма", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название
        Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Жанр
        Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.genre_entry = Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        # Год выпуска
        Label(input_frame, text="Год выпуска:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.year_entry = Entry(input_frame, width=30)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5)

        # Рейтинг
        Label(input_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.rating_entry = Entry(input_frame, width=30)
        self.rating_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавления
        self.add_btn = Button(input_frame, text="Добавить фильм", command=self.add_movie,
                              bg="green", fg="white", font=("Arial", 10, "bold"))
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # === Фрейм для фильтрации ===
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5, pady=5)
        self.genre_filter.bind("<KeyRelease>", lambda e: self.refresh_table())

        Label(filter_frame, text="Фильтр по году:").grid(row=1, column=0, padx=5, pady=5)
        self.year_filter = Entry(filter_frame, width=20)
        self.year_filter.grid(row=1, column=1, padx=5, pady=5)
        self.year_filter.bind("<KeyRelease>", lambda e: self.refresh_table())

        # Кнопка сброса фильтров
        self.reset_btn = Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters,
                                bg="orange")
        self.reset_btn.grid(row=2, column=0, columnspan=2, pady=5)

        # === Фрейм для таблицы ===
        table_frame = Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы (Treeview)
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Title", "Genre", "Year", "Rating"),
                                 show="headings", height=15)

        # Определение колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Year", text="Год")
        self.tree.heading("Rating", text="Рейтинг")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Title", width=250)
        self.tree.column("Genre", width=150)
        self.tree.column("Year", width=80, anchor="center")
        self.tree.column("Rating", width=80, anchor="center")

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.pack(side="left", fill="both", expand=True)

        # === Кнопки управления ===
        control_frame = Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.delete_btn = Button(control_frame, text="Удалить выбранный фильм", command=self.delete_movie,
                                 bg="red", fg="white")
        self.delete_btn.pack(side="left", padx=5)

        self.save_btn = Button(control_frame, text="Сохранить в JSON", command=self.save_to_json,
                               bg="blue", fg="white")
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = Button(control_frame, text="Загрузить из JSON", command=self.load_from_json,
                               bg="purple", fg="white")
        self.load_btn.pack(side="left", padx=5)

    def validate_input(self, title, genre, year, rating):
        """Проверка корректности ввода"""
        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не могут быть пустыми!")
            return False

        try:
            year_int = int(year)
            if year_int < 1888 or year_int > 2026:
                messagebox.showerror("Ошибка", "Год должен быть между 1888 и 2026!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return False

        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return False

        return True

    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()

        if self.validate_input(title, genre, year, rating):
            movie = {
                "id": len(self.movies) + 1,
                "title": title,
                "genre": genre,
                "year": int(year),
                "rating": float(rating)
            }
            self.movies.append(movie)
            self.save_to_json()  # Автосохранение
            self.clear_entries()
            self.refresh_table()
            messagebox.showinfo("Успех", f"Фильм \"{title}\" добавлен!")

    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return

        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?")
        if confirm:
            for item in selected:
                values = self.tree.item(item, "values")
                movie_id = int(values[0])
                self.movies = [m for m in self.movies if m["id"] != movie_id]

            # Перенумерация ID
            for i, movie in enumerate(self.movies, 1):
                movie["id"] = i

            self.save_to_json()
            self.refresh_table()
            messagebox.showinfo("Успех", "Фильм удалён!")

    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получение фильтров
        genre_filter = self.genre_filter.get().strip().lower()
        year_filter = self.year_filter.get().strip()

        # Фильтрация
        filtered_movies = self.movies.copy()

        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter in m["genre"].lower()]

        if year_filter:
            try:
                year_int = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m["year"] == year_int]
            except ValueError:
                pass  # Игнорируем нечисловой ввод

        # Заполнение таблицы
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))

    def reset_filters(self):
        """Сброс фильтров"""
        self.genre_filter.delete(0, END)
        self.year_filter.delete(0, END)
        self.refresh_table()

    def clear_entries(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.year_entry.delete(0, END)
        self.rating_entry.delete(0, END)

    def save_to_json(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False

    def load_from_json(self):
        """Загрузка данных из JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
                self.refresh_table()
                messagebox.showinfo("Успех", "Данные загружены из JSON!")
            else:
                messagebox.showwarning("Предупреждение", "Файл movies.json не найден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def load_data(self):
        """Автоматическая загрузка данных при запуске"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except:
                self.movies = []
        else:
            # Пример данных для демонстрации
            self.movies = [
                {"id": 1, "title": "Побег из Шоушенка", "genre": "Драма", "year": 1994, "rating": 9.3},
                {"id": 2, "title": "Крёстный отец", "genre": "Криминал", "year": 1972, "rating": 9.2},
                {"id": 3, "title": "Тёмный рыцарь", "genre": "Боевик", "year": 2008, "rating": 9.0},
                {"id": 4, "title": "Криминальное чтиво", "genre": "Криминал", "year": 1994, "rating": 8.9}
            ]
            self.save_to_json()


if __name__ == "__main__":
    root = Tk()
    app = MovieLibrary(root)
    root.mainloop()