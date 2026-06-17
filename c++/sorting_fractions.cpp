#include <iostream>
#include <string>

using namespace std;

struct Fraction {
  long long numerator;
  long long denominator;
};

long long GreatestCommonDivisor(long long first, long long second) {
  first = first < 0 ? -first : first;
  second = second < 0 ? -second : second;
  while (second != 0) {
    long long remainder = second;
    second = first % second;
    first = remainder;
  }
  return first;
}

Fraction ReduceFraction(Fraction fraction) {
  if (fraction.numerator == 0) {
    fraction.denominator = 1;
    return fraction;
  }
  long long divisor = GreatestCommonDivisor(fraction.numerator, fraction.denominator);
  fraction.numerator /= divisor;
  fraction.denominator /= divisor;
  if (fraction.denominator < 0) {
    fraction.numerator = -fraction.numerator;
    fraction.denominator = -fraction.denominator;
  }
  return fraction;
}

bool IsLessThan(Fraction left, Fraction right) {
  return left.numerator * right.denominator < right.numerator * left.denominator;
}

void SwapFractions(Fraction& first, Fraction& second) {
  Fraction temporary = first;
  first = second;
  second = temporary;
}

void BubbleSortFractions(Fraction* fractions, int count) {
  for (int pass = 0; pass < count - 1; ++pass) {
    bool swapped = false;
    for (int current = 0; current < count - pass - 1; ++current) {
      if (IsLessThan(fractions[current + 1], fractions[current])) {
        SwapFractions(fractions[current], fractions[current + 1]);
        swapped = true;
      }
    }
    if (!swapped) {
      break;
    }
  }
}

string FractionToDisplayString(Fraction fraction) {
  string display;
  if (fraction.numerator < 0) {
    display += '-';
    fraction.numerator = -fraction.numerator;
  }
  display += to_string(fraction.numerator);
  if (fraction.denominator != 1) {
    display += '/';
    display += to_string(fraction.denominator);
  }
  return display;
}

int main() {
  int fraction_count;
  cin >> fraction_count;

  Fraction* fractions = new Fraction[fraction_count];

  for (int index = 0; index < fraction_count; ++index) {
    cin >> fractions[index].numerator >> fractions[index].denominator;
    fractions[index] = ReduceFraction(fractions[index]);
  }

  BubbleSortFractions(fractions, fraction_count);

  for (int index = 0; index < fraction_count; ++index) {
    cout << FractionToDisplayString(fractions[index]) << endl;
  }

  delete[] fractions;
  return 0;
}
