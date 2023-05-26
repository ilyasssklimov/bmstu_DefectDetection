#include <iostream>


void foo() {
    int a = 1;
    int b = 2;
    int c = a + b;
    c *= 2;

    if (c > 2) {
        std::cout << "c more than 2" << std::endl
        return;
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
    foo();
    int result = boo();

    if (result > 0)
        return 0;
    else
        return -1;
}