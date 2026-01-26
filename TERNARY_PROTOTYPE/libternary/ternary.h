/**
 * ZIME Ternary Computing System - libternary API
 * Patent Application: 63/967,611
 * Copyright (c) 2026 JaKaiser Smith
 */

#ifndef _LIBTERNARY_H
#define _LIBTERNARY_H

#include <stdint.h>
#include <stdbool.h>

/* Trit - Ternary digit */
typedef struct {
    uint8_t state;      /* 0=ZERO, 1=PSI, 2=ONE */
    uint32_t psi_value; /* Probability * 1000000 */
} trit_t;

#define TRIT_ZERO   0
#define TRIT_PSI    1
#define TRIT_ONE    2

trit_t trit_zero(void);
trit_t trit_one(void);
trit_t trit_psi(void);
trit_t trit_resolve(trit_t t);
trit_t trit_and(trit_t a, trit_t b);
trit_t trit_or(trit_t a, trit_t b);
trit_t trit_xor(trit_t a, trit_t b);
trit_t trit_not(trit_t t);
int ternary_init(void);
void ternary_cleanup(void);

#endif
