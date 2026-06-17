#include <chrono>
#include <iostream>
#include <string>
#include <ctime>

using namespace std;

string expressions [] = {"7 + 8","5 * 6", "36 - 25", "28 + 14", "0 + 0"};
int answer [] = {15, 30, 11, 42, 0};
int genius=0;
double value=0;
int allanswer=0;
char replay = 'n';

const int expressions_size = sizeof(expressions) / sizeof (expressions[0]);


int main() {
    while(replay == 'n' || replay == 'N') {

        int index = rand() % expressions_size;
        cout << expressions[index] << " = ";


        chrono::steady_clock::time_point start = chrono::steady_clock::now();
        int t;
        cin >> t;

        chrono::steady_clock::time_point finish = chrono::steady_clock::now();

        double time = chrono::duration<double>(finish - start).count();


        if (t==answer[index]) {
            genius++;
        }
        allanswer++;
        value += time;
        cout << "сдаешься? (y/n) : ";

        cin >> replay;

    }

    cout << "количество примеров : " << allanswer << endl;

    cout << "количество правильных ответов : " << genius << endl;

    cout << "общее время: " << value << " с." <<endl;

    cout << "среднее время решения : " << value/allanswer << " c." << endl;


    return 0;
}
