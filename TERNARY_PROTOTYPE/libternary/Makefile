CC = gcc
CFLAGS = -Wall -Wextra -O2

all: libternary.a test_ternary

libternary.a: ternary.o
ar rcs $@ $^

ternary.o: ternary.c ternary.h
$(CC) $(CFLAGS) -c $<

test_ternary: test_ternary.c libternary.a
$(CC) $(CFLAGS) -o $@ $< -L. -lternary

clean:
rm -f *.o libternary.a test_ternary
