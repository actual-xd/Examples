import struct
import os


def compress_lzw(data, max_dict_size=4096):
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}


    codes = []
    current = b""

    for byte in data:
        symbol = bytes([byte])
        combined = current + symbol
        if combined in dictionary:
            current = combined
        else:
            codes.append(dictionary[current])
            if dict_size < max_dict_size:
                dictionary[combined] = dict_size
                dict_size += 1
            current = symbol

    if current:
        codes.append(dictionary[current])

    return codes


def decompress_lzw(codes, max_dict_size=4096):
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}


    result = bytearray()

    prev_code = codes[0]
    prev_string = dictionary[prev_code]
    result.extend(prev_string)

    for code in codes[1:]:
        if code in dictionary:
            current_string = dictionary[code]
        elif code == dict_size:
            current_string = prev_string + bytes([prev_string[0]])
        else:
            raise ValueError(f"Invalid code: {code}")

        result.extend(current_string)

        if dict_size < max_dict_size:
            dictionary[dict_size] = prev_string + bytes([current_string[0]])
            dict_size += 1

        prev_string = current_string

    return bytes(result)


def save_compressed_lzw(codes, filename):
    with open(filename, 'wb') as file:
        file.write(struct.pack('I', len(codes)))
        for code in codes:
            file.write(struct.pack('H', code))


def load_compressed_lzw(filename):
    with open(filename, 'rb') as file:
        data = file.read(4)
        if len(data) < 4:
            return []
        count = struct.unpack('I', data)[0]
        codes = []
        for _ in range(count):
            data = file.read(2)
            codes.append(struct.unpack('H', data)[0])
        return codes


def main():
    with open('input.txt', 'rb') as file:
        orig_data = file.read()

    orig_size = len(orig_data)

    codes = compress_lzw(orig_data, 2000)
    save_compressed_lzw(codes, 'output.bin')

    compressed_size = os.path.getsize('output.bin')

    loaded_codes = load_compressed_lzw('output.bin')
    decompressed_data = decompress_lzw(loaded_codes, 2000)



    if orig_data == decompressed_data:
        print("Данные совпадают")
    print(f"Оргинальный размер: {orig_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Всего кодов: {len(codes)}")

    print(f"Процент сжатия: {compressed_size / orig_size * 100:.2f}%")




if __name__ == "__main__":
    main()
