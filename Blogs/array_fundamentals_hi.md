# Array Fundamentals: Hinglish Breakdown

- **Author:** Rishab Dixit
- **Published on:** September 27, 2025
- **Read time:** 6 min

> Single value se lekar structured shelf tak ka safar array ke bina mushkil hai.

## Highlights
- Array contiguous memory deta hai jisse related values ek saath rahte hain.
- Index hamesha 0 se start hota hai, fifth element `arr[4]` hota hai.
- Loop se repetitive assignments aur output ekdum compact ho jaata hai.

## Single Value se Structured Shelf tak
Array ek aisa data structure hai jo values ko memory mein side-by-side rakhta hai, access simple ho jaata hai. Ek single value store karne ke liye `number` jaise variable declare karte ho jo ek labeled memory block provide karta hai.

```cpp
int number = 10;
```

## Array Declare Karna
Array declare karte waqt tum ek saath multiple slots reserve kar lete ho, har slot ko index se access kar sakte ho. Syntax mein data type, naam aur kitne elements chahiye wo specify karte ho.

```cpp
int variable_name[size];
```

Example ke liye five slots reserve karne hain toh:

```cpp
int arr[5]; // ye sirf declaration hai, initialization nahi
```

> **Warning:** 5 slots maango aur tumhe index 0 se 4 tak milenge. `arr[5]` access karoge toh undefined behavior ho sakta hai.

## Array mein Value Store Karna
Har index pe manually value daal sakte ho lekin array bada ho toh ye kaam tedious ho jaata hai.

```cpp
arr[0] = 10;
arr[1] = 20;
arr[2] = 30;
arr[3] = 40;
arr[4] = 50;
```

Loop repeat hone wale kaam ko handle karta hai—pattern generate karo ya user input lo.

```cpp
for (int i = 0; i < 5; i++) {
    arr[i] = (i + 1) * 10;
}
```

> **Tip:** User input lena hai toh loop ke andar `cin >> arr[i];` likh do aur same structure reuse karo.

## Array Print Karna
Indices pe iterate karke jab values print karte ho toh space add karne se output readable dikhta hai.

```cpp
for (int i = 0; i < 5; i++) {
    cout << arr[i] << " ";
}
```

## Complete Example: Hardcoded Values
Neeche wala C program har value manually store karta hai aur fir print karta hai.

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
Optimized version loop ka use karke pehle values leta hai aur phir unhe print karta hai.

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
