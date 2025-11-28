#include <iostream>
using namespace std;

int main() {
    // 1. ЦИКЛ WHILE
    cout << "\n1. Цикл while (числа от 1 до 5):" << endl;
    int i = 1;
    while (i <= 5) {
        cout << i << " ";
        i++;
    }

    // 2. ЦИКЛ DO-WHILE
    cout << "\n\n2. Цикл do-while (гарантированное выполнение):" << endl;
    int j = 10;
    do {
        cout << "Это сообщение выведется, даже если условие ложно. j = " << j << endl;
    } while (j < 5);

    // 3. BREAK В ЦИКЛЕ
    cout << "\n3. Использование break (выход при i=7):" << endl;
    int k = 1;
    while (true) {
        if (k == 7) {
            break;
        }
        cout << k << " ";
        k++;
    }

    // 4. CONTINUE В ЦИКЛЕ
    cout << "\n\n4. Использование continue (только нечетные числа 1-10):" << endl;
    int m = 0;
    while (m < 10) {
        m++;
        if (m % 2 == 0) {
            continue; // пропускаем четные числа
        }
        cout << m << " ";
    }

    // 5. РАБОТА С МАССИВАМИ
    cout << "\n\n5. Работа с массивами:" << endl;

    // Объявление и инициализация массива
    int numbers[6] = {2, 8, 15, 7, 3, 10};

    // Вывод массива
    cout << "Массив: ";
    for (int idx = 0; idx < 6; idx++) {
        cout << numbers[idx] << " ";
    }

    // Поиск суммы элементов
    int sum = 0;
    int idx = 0;
    while (idx < 6) {
        sum += numbers[idx];
        idx++;
    }
    cout << "\nСумма элементов: " << sum;

    // Поиск максимального элемента
    int max = numbers[0];
    idx = 1;
    while (idx < 6) {
        if (numbers[idx] > max) {
            max = numbers[idx];
        }
        idx++;
    }
    cout << "\nМаксимальный элемент: " << max;

    // 6. КОМБИНАЦИЯ ВСЕГО ВМЕСТЕ
    cout << "\n\n6. Комбинированный пример (поиск первого четного числа):" << endl;
    int arr[5] = {3, 7, 9, 4, 11};
    int position = 0;
    bool found = false;

    do {
        if (arr[position] % 2 == 0) {
            cout << "Найдено четное число: " << arr[position] << " на позиции " << position << endl;
            found = true;
            break;
        }
        position++;
    } while (position < 5);

    if (!found) {
        cout << "Четные числа не найдены" << endl;
    }

    return 0;
}