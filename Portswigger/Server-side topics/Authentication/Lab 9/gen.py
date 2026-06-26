password_dir = "./password.txt"
output_user_dir = "./user_payload.txt"
output_pass_dir = "./pass_payload.txt"

with open(password_dir, "r", encoding="utf-8") as pf:
    passwords = [line.strip() for line in pf if line.strip()]

cnt = 0
with open(output_user_dir, "w", encoding="utf-8") as out:
    for _ in passwords:    
        if cnt % 2 == 0: out.write("wiener\n")
        out.write("carlos\n")
        cnt += 1

cnt = 0
with open(output_pass_dir, "w", encoding="utf-8") as out:
    for pssd in passwords:
        if cnt % 2 == 0: out.write("peter\n")
        out.write(f"{pssd}\n")
        cnt += 1