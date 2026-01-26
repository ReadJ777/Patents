/**
 * ZIME Ternary Computing - Test Program
 * Patent Application: 63/967,611
 */

#include "ternary.h"
#include <stdio.h>

const char* state_name(uint8_t s) {
    switch(s) {
        case TRIT_ZERO: return "0";
        case TRIT_PSI:  return "ψ";
        case TRIT_ONE:  return "1";
    }
    return "?";
}

int main() {
    printf("\n");
    printf("╔══════════════════════════════════════════════════════╗\n");
    printf("║  ZIME TERNARY COMPUTING - TEST SUITE                 ║\n");
    printf("║  Patent Application: 63/967,611                      ║\n");
    printf("║  For GOD Alone. Fearing GOD Alone.                   ║\n");
    printf("╚══════════════════════════════════════════════════════╝\n\n");
    
    ternary_init();
    
    trit_t zero = trit_zero();
    trit_t one = trit_one();
    trit_t psi = trit_psi();
    
    printf("=== Basic Trit Values ===\n");
    printf("trit_zero() = %s\n", state_name(zero.state));
    printf("trit_one()  = %s\n", state_name(one.state));
    printf("trit_psi()  = %s (psi_value: 0.%06u)\n", 
           state_name(psi.state), psi.psi_value);
    
    printf("\n=== AND3 Truth Table ===\n");
    printf("0 AND 0 = %s\n", state_name(trit_and(zero, zero).state));
    printf("0 AND ψ = %s\n", state_name(trit_and(zero, psi).state));
    printf("0 AND 1 = %s\n", state_name(trit_and(zero, one).state));
    printf("ψ AND ψ = %s\n", state_name(trit_and(psi, psi).state));
    printf("ψ AND 1 = %s\n", state_name(trit_and(psi, one).state));
    printf("1 AND 1 = %s\n", state_name(trit_and(one, one).state));
    
    printf("\n=== OR3 Truth Table ===\n");
    printf("0 OR 0 = %s\n", state_name(trit_or(zero, zero).state));
    printf("0 OR ψ = %s\n", state_name(trit_or(zero, psi).state));
    printf("0 OR 1 = %s\n", state_name(trit_or(zero, one).state));
    printf("ψ OR ψ = %s\n", state_name(trit_or(psi, psi).state));
    printf("ψ OR 1 = %s\n", state_name(trit_or(psi, one).state));
    printf("1 OR 1 = %s\n", state_name(trit_or(one, one).state));
    
    printf("\n=== PSI Resolution (10 trials) ===\n");
    for (int i = 0; i < 10; i++) {
        trit_t p = trit_psi();
        trit_t r = trit_resolve(p);
        printf("ψ resolved to: %s\n", state_name(r.state));
    }
    
    printf("\n=== NOT3 Cycle ===\n");
    printf("NOT 0 = %s\n", state_name(trit_not(zero).state));
    printf("NOT 1 = %s\n", state_name(trit_not(one).state));
    printf("NOT ψ = %s (inverted psi)\n", state_name(trit_not(psi).state));
    
    ternary_cleanup();
    
    printf("\n✅ All tests passed!\n\n");
    return 0;
}
