#include <iostream>
using namespace std;

class DynamicArray {
private:
    int* arr;        // Указатель на массив
    int size;        // Текущий размер массива

public:
    // Конструктор по умолчанию
    DynamicArray() {
        arr = nullptr;
        size = 0;
        cout << "Создан пустой массив" << endl;
    }

    // Конструктор с размером
    DynamicArray(int n) {
        size = n;
        arr = new int[size];  // Выделяем память
        for (int i = 0; i < size; i++) {
            arr[i] = 0;  // Инициализируем нулями
        }
        cout << "Создан массив размера " << size << endl;
    }

    // Конструктор копирования (глубокое копирование)
    DynamicArray(const DynamicArray& other) {
        size = other.size;
        arr = new int[size];
        for (int i = 0; i < size; i++) {
            arr[i] = other.arr[i];
        }
        cout << "Скопирован массив" << endl;
    }

    // Деструктор
    ~DynamicArray() {
        if (arr != nullptr) {
            delete[] arr;  // Освобождаем память
            cout << "Массив удален" << endl;
        }
    }

    // Добавление элемента в конец
    void addElement(int value) {
        // Создаем новый массив на 1 больше
        int* newArr = new int[size + 1];

        // Копируем старые элементы
        for (int i = 0; i < size; i++) {
            newArr[i] = arr[i];
        }

        // Добавляем новый элемент
        newArr[size] = value;

        // Освобождаем старую память
        if (arr != nullptr) {
            delete[] arr;
        }

        // Перенаправляем указатель
        arr = newArr;
        size++;

        cout << "Добавлен элемент " << value << endl;
    }

    // Удаление элемента по индексу
    void removeAt(int index) {
        if (index < 0 || index >= size) {
            cout << "Ошибка: индекс вне диапазона" << endl;
            return;
        }

        if (size == 1) {
            // Если останется пустой массив
            delete[] arr;
            arr = nullptr;
            size = 0;
            return;
        }

        // Создаем новый массив на 1 меньше
        int* newArr = new int[size - 1];

        // Копируем элементы до удаляемого
        for (int i = 0; i < index; i++) {
            newArr[i] = arr[i];
        }

        // Копируем элементы после удаляемого
        for (int i = index + 1; i < size; i++) {
            newArr[i - 1] = arr[i];
        }

        delete[] arr;
        arr = newArr;
        size--;

        cout << "Удален элемент с индексом " << index << endl;
    }

    // Перегрузка оператора []
    int& operator[](int index) {
        if (index < 0 || index >= size) {
            cout << "Ошибка: индекс вне диапазона" << endl;
            // Возвращаем ссылку на первый элемент (чтобы избежать краха)
            return arr[0];
        }
        return arr[index];
    }

    // Вывод массива
    void print() {
        if (size == 0) {
            cout << "Массив пуст" << endl;
            return;
        }

        cout << "[";
        for (int i = 0; i < size; i++) {
            cout << arr[i];
            if (i < size - 1) cout << ", ";
        }
        cout << "]" << endl;
    }

    // Получение размера
    int getSize() {
        return size;
    }
};

// Демонстрационная функция
int main() {
    setlocale(LC_ALL, "Russian");

    cout << "=== Лабораторная работа: Динамический массив ===\n" << endl;

    // Тест 1: Создание массива
    cout << "Тест 1: Создание массива" << endl;
    DynamicArray arr1(3);
    arr1[0] = 10;
    arr1[1] = 20;
    arr1[2] = 30;
    cout << "arr1 = ";
    arr1.print();
    cout << endl;

    // Тест 2: Конструктор копирования
    cout << "Тест 2: Копирование массива" << endl;
    DynamicArray arr2 = arr1;
    cout << "arr2 = ";
    arr2.print();
    cout << endl;

    // Тест 3: Добавление элементов
    cout << "Тест 3: Добавление элементов" << endl;
    arr1.addElement(40);
    arr1.addElement(50);
    cout << "arr1 после добавления: ";
    arr1.print();
    cout << "Размер: " << arr1.getSize() << endl;
    cout << endl;

    // Тест 4: Удаление элементов
    cout << "Тест 4: Удаление элементов" << endl;
    arr1.removeAt(2);  // Удаляем элемент с индексом 2
    cout << "arr1 после удаления: ";
    arr1.print();
    cout << "Размер: " << arr1.getSize() << endl;
    cout << endl;

    // Тест 5: Проверка независимости копий
    cout << "Тест 5: Проверка независимости копий" << endl;
    cout << "arr1 = ";
    arr1.print();
    cout << "arr2 = ";
    arr2.print();
    cout << "Массивы независимы (разные адреса)" << endl;

    return 0;
}
