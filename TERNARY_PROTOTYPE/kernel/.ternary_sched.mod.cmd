savedcmd_ternary_sched.mod := printf '%s\n'   ternary_sched.o | awk '!x[$$0]++ { print("./"$$0) }' > ternary_sched.mod
