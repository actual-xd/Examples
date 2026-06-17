#include <iostream>
#include <string>

using namespace std;

struct Fraction {
    long nominator;
    long denominator;
};

bool isGreater(Fraction a, Fraction b) {
    return a.nominator*b.denominator > b.nominator*a.denominator;
}

long GreaterCommonDivider(long n, long d){
    n = n<0  ? -n : n;
    d= d<0  ? -d : d;

    while(d!=0){
        long r=d;
        d = n % d;
        n = r;
    }
    return n;

}


Fraction reduce (Fraction fraction) {
    if (fraction.nominator==0){
        fraction.denominator=1;
        return fraction;
    }

    long divider = GreaterCommonDivider(fraction.nominator, fraction.denominator);
    fraction.nominator = fraction.nominator/divider;
    fraction.denominator = fraction.denominator/divider;

    if (fraction.denominator<0){
        fraction.nominator=-fraction.nominator;
        fraction.denominator=-fraction.denominator;
    }

    return fraction;

}

void sort(Fraction* fractions, int count) {
    for (int i=0; i<count-1; i++) {
        bool swapped = false;
        for (int j=0; j<count-1-i; j++) {
            if (isGreater(fractions[j], fractions[j+1])){
                Fraction meow = fractions[j];
                fractions[j] = fractions[j+1];
                fractions[j+1]=meow;
                swapped = true;
            }

        }
        if (!swapped) {
            break;
        }
    }
}

string display(Fraction fraction) {
    string display;

    display += to_string(fraction.nominator);
    if (fraction.denominator != 1) {
        display += "/";
        display += to_string(fraction.denominator);
    }
    return display;

}




int main () {
    int number_of_fractions;
    cin>>number_of_fractions;

    Fraction* fractions = new Fraction[number_of_fractions];
    for (int i =0; i < number_of_fractions; i++) {
        cin >> fractions[i].nominator >> fractions[i].denominator;
        fractions[i] = reduce(fractions[i]);
    }

    sort(fractions, number_of_fractions);

    for (int i =0; i < number_of_fractions; i++) {
        cout << display(fractions[i]) << endl;
    }



    delete[] fractions;
    return 0;


}
