# Bản Đồ Nguồn Tham Chiếu và Mức Độ Bao Phủ

## Nguồn Tài Liệu Đã Sử Dụng

Tài liệu được dùng làm nền để tái cấu trúc knowledge base:

1. `reference/owasp.txt`
2. `reference/burpsuite.txt`
3. `reference/hacktricks.txt`
4. `reference/payloadsallthethings.md`

## Ma Trận Bao Phủ

| Nguồn                | Chủ đề chính đã khai thác vào KB                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| OWASP                | Định nghĩa XXE, risk factors, impact classes, ví dụ file read/SSRF/DoS                         |
| Burp Suite           | Taxonomy attack types, blind XXE (OOB/error), local DTD repurposing, hidden surfaces           |
| HackTricks           | Payload variants, protocol abuse (`jar`, wrappers), local/system DTD paths, Office/XML formats |
| PayloadsAllTheThings | Payload library, bypass ideas, OOB recipes, practical test snippets                            |

## Mapping Chủ Đề -> File

| Chủ đề                          | File đích                                 |
| ------------------------------- | ----------------------------------------- |
| XXE overview và impact          | `00-overview.md`                          |
| XML/DTD/parser fundamentals     | `01-xml-dtd-parser-fundamentals.md`       |
| Root causes và conditions       | `02-root-causes-and-attack-conditions.md` |
| Detection methodology           | `03-detection.md`                         |
| Exploitation process model      | `04-exploitation-workflow.md`             |
| File read techniques            | `05-file-read-and-local-disclosure.md`    |
| SSRF pivot                      | `06-ssrf-and-internal-recon.md`           |
| Blind/OOB/error-based/local DTD | `07-blind-xxe-and-oob-exfiltration.md`    |
| Hidden attack surface           | `08-hidden-attack-surface.md`             |
| Bypass/advanced methods         | `09-bypass-and-advanced-techniques.md`    |
| Payload quick use               | `10-payloads-cheatsheet.md`               |
| Defense/mitigation              | `11-defense-mitigation.md`                |
| Lab + agent training            | `12-lab-design-and-agent-training.md`     |

## Nguyên Tắc Chuẩn Hóa Đã Áp Dụng

- Chuyển từ dạng tham khảo rời rạc sang hệ thống theo workflow học tập.
- Tách rõ khâu phần: nền tảng -> detection -> exploitation -> defense -> lab.
- Loại bỏ trùng lặp payload, giữ lại pattern cốt lõi và điều kiện áp dụng.
- Đồng bộ naming convention theo style folder SQLi (đánh số, theo chủ đề, dễ mở rộng).

## Ghi Chú

- Bộ tài liệu này ưu tiên dùng cho học tập bảo mật, pentest hợp pháp và xây dựng lab.
- Không sử dụng trên hệ thống không có ủy quyền.
