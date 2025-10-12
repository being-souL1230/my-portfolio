# Array Fundamentals: Contiguous Storage Explained

- **Author:** Rishab Dixit
- **Published on:** September 27, 2025
- **Read time:** 6 min

> Build structured storage from a single variable onward and let loops handle the repetition for you.

## Highlights
- Arrays reserve contiguous memory so related values remain side-by-side for fast access.
- Indexing begins at 0, which means the fifth value lives at `arr[4]`.
- Loops turn repetitive assignments and prints into compact, scalable code.

## From a Single Value to Structured Storage
An array is a data structure that keeps values next to each other in memory, which makes access predictable and fast. Start with a single value: when you declare a variable such as `number`, you ask the program for a labeled memory block that currently holds one integer value.

```cpp
int number = 10;
```

## Declaring an Array
Arrays let you reserve multiple labeled slots in one go. Each slot is accessible with an index. The general syntax uses the type, a name, and the number of elements you want to store.

```cpp
int variable_name[size];
```

Here is a simple declaration that reserves five integer slots:

```cpp
int arr[5]; // declaration of an array with 5 integers
```

> **Warning:** Requesting 5 slots gives you indices 0 through 4 (that’s `n - 1`). Accessing `arr[5]` is out of bounds and leads to undefined behavior.

## Populating the Array
Manual assignments work for a few values, but they become tedious as the array grows.

```cpp
arr[0] = 10;
arr[1] = 20;
arr[2] = 30;
arr[3] = 40;
arr[4] = 50;
```

Loops excel at repetitive work: use them to generate patterns or handle user input.

```cpp
for (int i = 0; i < 5; i++) {
    arr[i] = (i + 1) * 10;
}
```

> **Tip:** Replace the assignment inside the loop with `cin >> arr[i];` when you want to accept user input.

## Iterating to Print Values
When you iterate over the indices and print each element, adding a space keeps the output readable.

```cpp
for (int i = 0; i < 5; i++) {
    cout << arr[i] << " ";
}
```

## Complete Example: Hardcoded Values
The following C program stores values manually and prints them one by one.

```c
#include <stdio.h>

int main() {
    int arr[5];

    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    arr[3] = 40;
    arr[4] = 50;

    printf("%d ", arr[0]);
    printf("%d ", arr[1]);
    printf("%d ", arr[2]);
    printf("%d ", arr[3]);
    printf("%d ", arr[4]);

    return 0;
}
```

## Complete Example: User Input + Output
Here’s the streamlined version that reads values dynamically and prints them with a loop.

```c
#include <stdio.h>

int main() {
    int arr[5];

    for (int i = 0; i < 5; i++) {
        scanf("%d", &arr[i]);
    }

    for (int i = 0; i < 5; i++) {
        printf("%d ", arr[i]);
    }

    return 0;
}
```
