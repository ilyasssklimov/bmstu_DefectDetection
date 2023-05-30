#include <iostream>


void foo(int c) {
    if (c > 2) {
        std::cout << "c more than 2" << std::endl
    } else {
        std::cout<< "c less than 2" << std::endl;
    }
}

int boo() {
    int numbers_sum = 0;

    for (int i = 0; i < 10; i++)
        numbers_sum += i;

    return numbers_sum;
}


int main() {
    foo(c);
    int result = boo();
    std::cout << result;

    return 0;
}