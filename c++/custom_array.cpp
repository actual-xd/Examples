#include <iostream>
using namespace std;


class DynamicArray {
private:
    int *arr;
    int size;
public:
    DynamicArray() {
        arr = nullptr;
        size = 0;
    };

    ~DynamicArray() {
        if (arr != nullptr){
            delete[] arr;
        }
    };

    void add(int value){
        int * newArray = new int[size + 1];

        for (int i = 0; i < size; i++)
        {
            newArray[i] = arr[i];
        }
        newArray[size] = value;

        if (arr != nullptr){
            delete[] arr;
        }

        arr = newArray;
        size++;
    };

    void print() {
        if (size == 0) {
            cout << "Массив пустой!" << endl;
            return;
        }
        cout << "[";
        for (int i = 0; i < size; i++){
            cout << arr[i];
            if (i < size - 1) cout << ", ";
        }
        cout << "]" << endl;
    };

    void remove(int index){
        if (index < 0 || index > size) {
            cout << "Неверный индекс!" << endl;
            return;
        }
        if (size == 1) {
            delete[] arr;
            arr = nullptr;
            size = 0;
            return;

        }

        int *newArray =  new int[size - 1];
        for (int i = 0; i < index; i++) {
            newArray[i] = arr[i];
        }

        for (int i = index + 1; i < size; i++) {
            newArray[i - 1] = arr[i];
        }

        delete[] arr;
        arr = newArray;
        size--;
    };

    void remove_value(int value) {

        for (int i = 0; i < size; i++) {
            if (value == arr[i]) {
                remove(i);
            }
        }
    };

    int getSize () {
      return size;
    };
    int setSize (int value) {
        size = value;
    };

};

int main() {
    DynamicArray array = DynamicArray();
    array.add(5);
    array.add(6);
    array.add(7);
    array.add(8);


    array.print();

    array.remove(2);
    array.print();
    array.remove(-2);
    array.remove_value(6);
    array.print();

    cout << array.getSize();

    return 0;
};
