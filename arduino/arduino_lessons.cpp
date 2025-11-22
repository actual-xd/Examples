// int number = 1;
// bool condition = false;
// float number_2 = 7.3;

// int my_array[3][4] = {
//   {1,2,3,4},
//   {5,6,7,8},
//   {9,10,11,12}
// };

// int list[4] = {1,2,3,4};

// char stroka[] = "String content";

// String str = "hello";

int sum(int a, int b) {
  return a + b;
}

float convert(float celcius) {
  return (celcius * 9 / 5) + 32;
}


void setup() {
  Serial.begin(9600);


  for (int i = 0; i < 3; i++){
    Serial.println(convert(17.5));
  }

  // for (int i = 0; i < 3; i++) {
  //   for (int j = 0; j < 4; j++) {
  //     Serial.print(my_array[i][j]);
  //     Serial.print(" ");
  //   }
  //   Serial.println();

  // }
  // Serial.println(str);


  // for (int k = 0; k < 4; k++)
  // {
  //   Serial.print(list[k]);
  // }


  // put your setup code here, to run once:

}

void loop() {

}
