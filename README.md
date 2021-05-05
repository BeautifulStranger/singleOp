# singleOp

Single Operation Processor Emulator

This started as a simple single instruction processor emulator written in Python

This is based in this article by Oleg Mazonka http://mazonka.com/subleq/

The basic principle of operation:
Let A,B and C be consecutive memory addresses. Denote by [A] the value stored at address A.
The processor follow these steps:
1: Read the value of A, ie [A]
2: Read the value of B, ie [B]
3: Perform the arithmetic operation [B] - [A]
4: Store the result of (3) at address B
5: Read C
6: If the result of (3) is less than or equal to 0 ((3 <= 0)) it will jump to address [C]
-repeat
