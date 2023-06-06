#include <iostream>


void foo() {
    /*
    Низкая вероятность дефектов
    Количество дефектов: 0
    */
    int c = 1, d = 2, e = 3;
    int sum = c + d + e;
    std::cout << "Sum = " << sum << std::endl;

    for (int i = 0; i < 5; i++)
        std::cout << "i = " << i << std::endl;

    int a = sum * 2;
    if (a > 10)
        a /= 5;
    std::cout << a;
}


void boo() {
    /*
    Средняя вероятность дефектов
    Количество дефектов: 1
    */

    double a = 1 / 33;
    std::cout << "Count sum..." << std::endl;
    for (double b = 0; b < 1; b += a) {}
    std::cout << "b = " << b << std::endl;  // Ожидается 1, результат отличается

    int c = 10;
    while (c > 1) {
        std::cout << "c = " << c << std::endl;
        c /= 2;
    }

    float d = 0.5;
    a = d * 20;
    a += 23;
    a /= 2;
    if (a > 5)
        a /= 5;
    std::cout << "a = " << a << std::endl;
}


void zoo() {
    /*
    Высокая вероятность дефектов
    Количество дефектов: 2
    */
    int sum = 0;
    int i = 0, j = 0;  // Неверное место инициализации
    for (; i < 10; i++) {
        for (; j < n, j++) {
            sum += i + j;
        }
    }

    int array[5] = {-1, -2, -3, -4, -5};
    int max = 0;  // Неверная инициализация
    for (int i = 0; i < 5; i++) {
        if (array[i] > max)
            max = array[i];
    }

    float d = 0.5;
    a = d * 20;
    a += 23;
    a /= 2;
    if (d > 0.5)
        a *= 2;
    std::cout << "a = " << a << std::endl;
}


int* koo(int idx, std::string filename) {
    /*
    Очень высокая вероятность дефектов
    Количество дефектов: 4
    */
    std::string name = "file";
    // Отсутствует обработка else, что может привести к неверному расширению
    if (idx == 0)
        name += ".txt";
    else if (idx == 1)
        name += ".cpp"

    create_file(name);

    // Неизвестно, присутствует ли формат в названии
    open_file(filename + ".txt");

    int array[3] = { 0, 1, 2 };
    for (int i = 0; i < 3; i++) {
        if (i % 2 != 0) {
            // Необходимо дополнительно аллоцировать память
            array[i * 2] = i;
        }
    }

    int a = 5;
    if (name == "file" || a > 4)
        a = 10;
    return &a;  // указатель на локальную переменную
}


int main() {
    std::cout << "Start program" << std::endl;
    foo();
    boo();
    std::cout << "End program" << std::endl;

   return 0;
}