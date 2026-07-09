/*
 * Лабораторная работа: Генератор RSA ключей
 *
 * Алгоритм RSA:
 *   1. Выбрать два различных простых числа prime1 и prime2
 *   2. Вычислить modulus = prime1 * prime2
 *   3. Вычислить функцию Эйлера: totient = (prime1-1)(prime2-1)
 *   4. Выбрать encryptExp: 1 < encryptExp < totient,  НОД(encryptExp, totient) = 1
 *   5. Найти decryptExp: decryptExp * encryptExp ≡ 1 (mod totient)
 *
 * Открытый ключ:  (encryptExp, modulus) — используется для шифрования
 * Закрытый ключ: (decryptExp, modulus) — используется для расшифровки
 *
 * Шифрование:  ciphertext = message^encryptExp mod modulus
 * Дешифровка:  message    = ciphertext^decryptExp mod modulus
 *
 * Безопасность основана на трудности разложения modulus на множители prime1 и prime2.
 * В реальных системах используются числа длиной 2048+ бит.
 * Данная реализация использует малые числа в учебных целях.
 */

#include <iostream>
#include <cstdlib>
#include <ctime>
#include <string>
#include <algorithm>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#endif

typedef long long ll;

// ── Вспомогательные функции ──────────────────────────────────────────────────

// НОД (алгоритм Евклида)
ll gcd(ll left, ll right) {
    while (right) { ll temp = right; right = left % right; left = temp; }
    return left;
}

// Расширенный алгоритм Евклида: left*coeffLeft + right*coeffRight = НОД(left,right)
ll extgcd(ll left, ll right, ll &coeffLeft, ll &coeffRight) {
    if (right == 0) { coeffLeft = 1; coeffRight = 0; return left; }
    ll subCoeffLeft, subCoeffRight;
    ll gcdResult = extgcd(right, left % right, subCoeffLeft, subCoeffRight);
    coeffLeft  = subCoeffRight;
    coeffRight = subCoeffLeft - (left / right) * subCoeffRight;
    return gcdResult;
}

// Обратный элемент по модулю: value^-1 mod modulus
// Решает уравнение value * inverse ≡ 1 (mod modulus)
ll modularInverse(ll value, ll modulus) {
    ll coeffLeft, coeffRight;
    if (extgcd(value, modulus, coeffLeft, coeffRight) != 1) return -1;
    return (coeffLeft % modulus + modulus) % modulus;
}

// Быстрое возведение в степень по модулю: base^exponent mod modulus
// Используется метод "двоичного возведения в степень"
ll modpow(ll base, ll exponent, ll modulus) {
    ll result = 1;
    base %= modulus;
    while (exponent > 0) {
        if (exponent & 1) result = result * base % modulus;
        base = base * base % modulus;
        exponent >>= 1;
    }
    return result;
}

// Проверка простоты (пробное деление, достаточно для учебных чисел)
bool isPrime(ll candidate) {
    if (candidate < 2) return false;
    if (candidate == 2) return true;
    if (candidate % 2 == 0) return false;
    for (ll divisor = 3; divisor * divisor <= candidate; divisor += 2)
        if (candidate % divisor == 0) return false;
    return true;
}

// Случайное простое число в диапазоне [rangeMin, rangeMax]
ll randomPrime(ll rangeMin, ll rangeMax) {
    ll candidate;
    do {
        candidate = rangeMin + rand() % (rangeMax - rangeMin + 1);
    } while (!isPrime(candidate));
    return candidate;
}

// ── Генерация ключей ─────────────────────────────────────────────────────────

struct PublicKey  { ll encryptExp, modulus; };
struct PrivateKey { ll decryptExp, modulus; };

struct KeyPair { PublicKey publicKey; PrivateKey privateKey; };

KeyPair generateKeys(ll rangeMin, ll rangeMax) {
    // Шаг 1: два различных простых prime1 и prime2
    ll prime1 = randomPrime(rangeMin, rangeMax);
    ll prime2;
    do { prime2 = randomPrime(rangeMin, rangeMax); } while (prime2 == prime1);

    std::cout << "prime1 = " << prime1 << ",  prime2 = " << prime2 << "\n";

    // Шаг 2: модуль
    ll modulus = prime1 * prime2;
    std::cout << "modulus = prime1 * prime2 = " << modulus << "\n";

    // Шаг 3: функция Эйлера
    ll totient = (prime1 - 1) * (prime2 - 1);
    std::cout << "totient = (prime1-1)(prime2-1) = " << totient << "\n";

    // Шаг 4: открытая экспонента — наименьшее нечётное > 1, взаимно простое с totient
    ll encryptExp = 3;
    while (encryptExp < totient && gcd(encryptExp, totient) != 1) encryptExp += 2;
    std::cout << "encryptExp = " << encryptExp
              << "  (НОД(encryptExp, totient) = " << gcd(encryptExp, totient) << ")\n";

    // Шаг 5: закрытая экспонента = encryptExp^-1 mod totient
    ll decryptExp = modularInverse(encryptExp, totient);
    std::cout << "decryptExp = " << decryptExp
              << "  (encryptExp * decryptExp mod totient = "
              << (encryptExp * decryptExp % totient) << ")\n";

    return { {encryptExp, modulus}, {decryptExp, modulus} };
}

// ── Шифрование / Дешифровка ──────────────────────────────────────────────────

ll encrypt(ll message, PublicKey publicKey) {
    return modpow(message, publicKey.encryptExp, publicKey.modulus);
}

ll decrypt(ll ciphertext, PrivateKey privateKey) {
    return modpow(ciphertext, privateKey.decryptExp, privateKey.modulus);
}

// ── Шифрование строк (разбиение на блоки) ─────────────────────

// Результат шифрования строки: зашифрованные блоки + длина исходного текста
struct EncryptedMessage {
    std::vector<ll> blocks;
    int charCount;
};

// Максимальное число бит, которое гарантированно < modulus
ll blockBits(ll modulus) {
    ll bits = 0;
    while (modulus > 0) { modulus >>= 1; bits++; }
    return bits - 1;
}

// Строка → двоичная строка (8 бит на символ)
std::string toBinary(const std::string &msg) {
    std::string binary;
    for (unsigned char c : msg)
        for (int i = 7; i >= 0; --i)
            binary += (c >> i) & 1 ? '1' : '0';
    return binary;
}

// Двоичная строка → исходная строка
std::string fromBinary(const std::string &binary) {
    std::string result;
    for (size_t i = 0; i < binary.length(); i += 8) {
        char c = 0;
        for (size_t j = 0; j < 8; ++j)
            c = (c << 1) | (binary[i + j] - '0');
        result += c;
    }
    return result;
}

// Шифрование строки: разбить двоичное представление на блоки, каждый зашифровать RSA
EncryptedMessage encryptString(const std::string &msg, PublicKey key) {
    EncryptedMessage result;
    result.charCount = msg.size();

    std::string binary = toBinary(msg);
    ll bitsPerBlock = blockBits(key.modulus);

    for (size_t i = 0; i < binary.length(); i += bitsPerBlock) {
        std::string chunk = binary.substr(i, bitsPerBlock);
        ll num = 0;
        for (char bit : chunk)
            num = num * 2 + (bit - '0');
        result.blocks.push_back(encrypt(num, key));
    }
    return result;
}

// Расшифровка: каждый блок → число → двоичная строка → конкатенация → строка
std::string decryptString(const EncryptedMessage &ct, PrivateKey key) {
    ll bitsPerBlock = blockBits(key.modulus);
    size_t totalBits = (size_t)ct.charCount * 8;

    std::string binary;
    for (size_t idx = 0; idx < ct.blocks.size(); ++idx) {
        ll num = decrypt(ct.blocks[idx], key);
        std::string bits;
        while (num > 0) {
            bits += (num & 1) ? '1' : '0';
            num >>= 1;
        }
        std::reverse(bits.begin(), bits.end());

        // Последний блок дополняем ровно до оставшихся бит, а не до bitsPerBlock
        ll padTo = (idx == ct.blocks.size() - 1)
            ? (totalBits - (ct.blocks.size() - 1) * bitsPerBlock)
            : bitsPerBlock;
        while ((ll)bits.length() < padTo)
            bits = '0' + bits;
        binary += bits;
    }

    return fromBinary(binary);
}

// ── main ─────────────────────────────────────────────────────────────────────

int main() {
    srand((unsigned)time(nullptr));
#ifdef _WIN32
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
#endif

    std::cout << "=== Генератор RSA ключей ===\n\n";

    // Простые числа в диапазоне [50, 300] — учебный размер
    // В реальных системах: числа длиной 1024+ бит
    KeyPair keys = generateKeys(50, 300);

    std::cout << "\nОТКРЫТЫЙ ключ:  (encryptExp=" << keys.publicKey.encryptExp
              << ", modulus=" << keys.publicKey.modulus << ")\n";
    std::cout << "ЗАКРЫТЫЙ ключ: (decryptExp=" << keys.privateKey.decryptExp
              << ", modulus=" << keys.privateKey.modulus << ")\n";

    // Демонстрация шифрования строк (блочный режим)
    std::cout << "\n--- Демонстрация шифрования строк (блочный режим) ---\n";
    std::cout << "Введите строку для шифрования: ";
    std::string input;
    std::getline(std::cin, input);

    if (input.empty()) {
        std::cout << "Ошибка: строка не может быть пустой\n";
        return 1;
    }

    EncryptedMessage encrypted = encryptString(input, keys.publicKey);

    std::cout << "Исходная строка:   \"" << input << "\"\n";
    std::cout << "Длина: " << input.length() << " символов, "
              << "блоков: " << encrypted.blocks.size() << "\n";
    std::cout << "Зашифрованные блоки: ";
    for (ll block : encrypted.blocks)
        std::cout << block << " ";
    std::cout << "\n";

    std::string decrypted = decryptString(encrypted, keys.privateKey);

    std::cout << "Расшифрованная строка: \"" << decrypted << "\"\n";
    std::cout << (input == decrypted ? "OK: совпадает\n" : "ОШИБКА: не совпадает\n");

    return 0;
}
