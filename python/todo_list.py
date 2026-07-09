import sys

# ponytail: force utf-8 so русские буквы работают на Windows
sys.stdout.reconfigure(encoding="utf-8")

"""
Лабораторная работа: Классы в Python — Список дел
Цель: познакомиться с классами, объектами и методами

Задания (сделай после запуска):
1. Добавь в класс Task поле "deadline" (срок выполнения)
2. Добавь метод show_tasks_by_status(status) — показывает только выполненные
   или только невыполненные задачи
3. Добавь возможность редактировать название задачи
"""

class Task:
    """Одна задача."""

    def __init__(self, title: str):
        self.title = title          # название задачи
        self.done = False           # выполнена или нет

    def mark_done(self):
        """Отметить задачу как выполненную."""
        self.done = True


class TodoList:
    """Список задач."""

    def __init__(self):
        self.tasks: list[Task] = []  # храним задачи в обычном списке

    def add(self, title: str):
        """Добавить новую задачу."""
        self.tasks.append(Task(title))

    def complete(self, index: int):
        """Отметить задачу под номером index как выполненную."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_done()
        else:
            print("  Ошибка: задачи с таким номером нет")

    def remove(self, index: int):
        """Удалить задачу."""
        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            print(f'  Удалено: "{removed.title}"')
        else:
            print("  Ошибка: задачи с таким номером нет")

    def show(self):
        """Показать все задачи."""
        if not self.tasks:
            print("  Список дел пуст")
            return
        print(f"  Всего задач: {len(self.tasks)}")
        for i, t in enumerate(self.tasks):
            status = "+" if t.done else "-"
            print(f"  {i}. [{status}] {t.title}")


def main():
    """Точка входа — простой текстовый интерфейс."""
    todo = TodoList()
    commands = {
        "1": ("Добавить задачу", todo.add),
        "2": ("Отметить выполненной", todo.complete),
        "3": ("Удалить задачу", todo.remove),
        "4": ("Показать список", lambda: todo.show()),
    }

    print("\n=== СПИСОК ДЕЛ ===")

    while True:
        import os
        os.system("cls" if os.name == "nt" else "clear")
        print("\nКоманды:")
        for key, (desc, _) in commands.items():
            print(f"  {key}. {desc}")
        print("  0. Выход")

        choice = input("> ").strip()

        if choice == "0":
            print("  Пока!")
            break

        if choice not in commands:
            print("  Неизвестная команда")
            continue

        if choice == "1":
            title = input("  Название задачи: ").strip()
            if title:
                todo.add(title)
            else:
                print("  Название не может быть пустым")
        elif choice == "2":
            try:
                idx = int(input("  Номер задачи: "))
                todo.complete(idx)
            except ValueError:
                print("  Введи число")
        elif choice == "3":
            try:
                idx = int(input("  Номер задачи: "))
                todo.remove(idx)
            except ValueError:
                print("  Введи число")
        todo.show()
        input("  Нажми Enter...")


if __name__ == "__main__":
    main()
