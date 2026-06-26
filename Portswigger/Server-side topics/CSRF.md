# CSRF - Bao Cao Tong Hop

## 1. CSRF la gi va vi sao nguy hiem

CSRF (Cross-Site Request Forgery) la lo hong cho phep attacker ep trinh duyet cua nan nhan gui request ngoai y muon toi ung dung ma nan nhan dang dang nhap.

Ban chat cua CSRF:

- Browser tu dong gui credential (dac biet la session cookie).
- Server thuong dong nhat "co credential hop le" voi "co chu dich nguoi dung".
- Attacker loi dung khoang cach giua xac thuc danh tinh va xac thuc y dinh.

## 2. Dieu kien hinh thanh tan cong

Mot cuoc tan cong CSRF thuong can:

1. Co action gia tri cao (doi email, doi mat khau, cap quyen, chuyen tien).
2. Action dua vao credential tu dong gui (cookie/basic auth/client cert).
3. Attacker tai tao duoc request hop le.
4. Co che anti-CSRF thieu, sai, hoac bi bypass.

## 3. Nguyen nhan goc re

1. Khong co anti-CSRF token hoac bao ve khong dong deu giua cac endpoint.
2. Token co nhung validate sai:
   - chi check theo method,
   - bo qua khi thieu token,
   - chap nhan token rong,
   - token khong bind session.
3. Origin/Referer check yeu, fail-open, substring match de bypass.
4. Qua phu thuoc SameSite va hieu sai hanh vi trinh duyet.
5. Server chap nhan request-shape linh hoat qua muc (method override, content-type confusion).

## 4. Workflow khai thac

```text
1. Mapping action nhay cam
2. Bat request hop le goc
3. Danh gia token/SameSite/Origin-Referer
4. Chon bypass pattern phu hop
5. Tao payload (GET tag, form POST, auto-submit, iframe, js)
6. Danh nan nhan kich hoat trong trang thai dang nhap
7. Xac nhan state change va danh gia impact
```

## 5. Cac pattern tan cong chinh

1. Direct CSRF khong phong ve.
2. Token validation bypass.
3. SameSite behavior abuse.
4. Referer/Origin validation bypass.
5. Request-shape bypass (method override, content-type).
6. Login CSRF va stored CSRF chains.
7. CSRF ket hop XSS de nang tac dong.

## 6. Tac dong bao mat

1. Account takeover gian tiep (doi email -> reset password).
2. Thay doi cau hinh bao mat (tat MFA, doi recovery channels).
3. Tac dong tai chinh (payment/account transfer actions).
4. Anh huong quan tri (tao admin, doi role, xoa du lieu).
5. Chuoi tan cong phuc hop khi ket hop voi XSS/stored content.

## 7. Phong thu dung ban chat

1. Bat buoc token manh, bi mat, kho doan, bind session/action.
2. Fail-closed khi thieu token hoac thieu Origin/Referer o action nhay cam.
3. Khong cho state-changing actions qua GET.
4. Chuan hoa effective method, kiem soat method override.
5. SameSite la lop bo tro, khong thay token.
6. Step-up auth cho action high-risk (re-auth, MFA, transaction confirmation).
7. Kiem thu hoi quy CSRF theo ma tran endpoint va bypass patterns.

## 8. To chuc tai lieu trong knowledge base

Bo module chi tiet duoc dat tai:

- [00-overview](../Web/CSRF/00-overview.md)
- [01-browser-auth-and-trust-model](../Web/CSRF/01-browser-auth-and-trust-model.md)
- [02-root-causes-and-conditions](../Web/CSRF/02-root-causes-and-conditions.md)
- [03-discovery-and-detection](../Web/CSRF/03-discovery-and-detection.md)
- [04-exploitation-workflow](../Web/CSRF/04-exploitation-workflow.md)
- [05-token-validation-bypasses](../Web/CSRF/05-token-validation-bypasses.md)
- [06-samesite-and-browser-behavior](../Web/CSRF/06-samesite-and-browser-behavior.md)
- [07-origin-referer-and-request-shape-bypass](../Web/CSRF/07-origin-referer-and-request-shape-bypass.md)
- [08-advanced-csrf-patterns](../Web/CSRF/08-advanced-csrf-patterns.md)
- [09-payloads-cheatsheet](../Web/CSRF/09-payloads-cheatsheet.md)
- [10-defense-mitigation](../Web/CSRF/10-defense-mitigation.md)
- [11-lab-design-and-agent-training](../Web/CSRF/11-lab-design-and-agent-training.md)
- [12-testing-checklist-and-playbook](../Web/CSRF/12-testing-checklist-and-playbook.md)
- [13-reference-mapping](../Web/CSRF/13-reference-mapping.md)

## 9. Ket luan

CSRF la bai toan xac thuc y dinh nguoi dung, khong chi la bai toan session cookie. Khi he thong chi tin credential ma khong xac minh intent, attacker co the loi dung trust relationship giua user, browser va server de tao state-changing requests trai phep.
