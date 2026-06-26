username_dir = "./username.txt"
password_dir = "./password.txt"
output_dir = "./payload.txt"

with open(username_dir, "r", encoding="utf-8") as uf:
    usernames = [line.strip() for line in uf if line.strip()]

with open(password_dir, "r", encoding="utf-8") as pf:
    passwords = [line.strip() for line in pf if line.strip()]

with open(output_dir, "w", encoding="utf-8") as out:
    for user in usernames:
        for password in passwords:
            out.write(f"username={user}&password={password}\n")