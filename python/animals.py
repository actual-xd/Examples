import sys

sys.stdout.reconfigure(encoding="utf-8")

"""
Лабораторная работа: Наследование классов — Зоопарк
Цель: понять как один класс может расширять другой

Новые понятия: наследование, переопределение методов, super()

Задания (сделай после запуска):
1. Добавь класс Cow(Animal) — выводит "My-y-y!"
2. Добавь поле age каждому животному
3. Сделай список животных в зоопарке (как в первой работе)
   и команду "показать всех"
"""


class Animal:
    """Животное — базовый класс для всех."""

    def __init__(self, name: str):
        self.name = name

    def make_sound(self) -> str:
        return "..."

    def __str__(self) -> str:
        return f"{self.name}: {self.make_sound()}"


class Dog(Animal):
    def make_sound(self) -> str:
        return "Гав!"


class Cat(Animal):
    def make_sound(self) -> str:
        return "Мяу!"


class Bird(Animal):
    def __init__(self, name: str):
        super().__init__(name)

    def make_sound(self) -> str:
        return "Чирик!"


# ponytail: список animals и зоопарк в main() — хватит для демо
def main():
    print("\n=== ЗООПАРК ===")
    animals = [
        Dog("Шарик"),
        Cat("Мурка"),
        Bird("Кеша"),
    ]

    while True:
        import os
        os.system("cls" if os.name == "nt" else "clear")

        print("\nКто говорит?")
        for i, a in enumerate(animals):
            print(f"  {i}. {a}")

        print("\nКоманды:")
        print("  animal. Создать животное (1 — Dog, 2 — Cat, 3 — Bird)")
        print("  номер. Услышать звук")
        print("  0. Выход")

        choice = input("> ").strip()

        if choice == "0":
            print("  Пока!")
            break
        elif choice == "1":
            name = input("  Имя собаки: ").strip()
            animals.append(Dog(name))
        elif choice == "2":
            name = input("  Имя кошки: ").strip()
            animals.append(Cat(name))
        elif choice == "3":
            name = input("  Имя птицы: ").strip()
            animals.append(Bird(name))
        else:
            try:
                idx = int(choice)
                if 0 <= idx < len(animals):
                    a = animals[idx]
                    print(f"  {a.name}: {a.make_sound()}")
                else:
                    print("  Нет такого животного")
            except ValueError:
                print("  Неизвестная команда")

        input("  Нажми Enter...")


if __name__ == "__main__":
    main()
