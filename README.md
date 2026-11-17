# Android Virtual Screen Field Guide

**Tiếng Việt** · [English](README.en.md) · [简体中文](README.zh-CN.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Ghi chép thực nghiệm điều khiển ứng dụng Android trên **màn hình ảo riêng**, trong khi màn hình vật lý vẫn tắt. Đây là repo **tài liệu và hướng dẫn tái lập**, không phải một Android agent hoàn chỉnh hay nơi phân phối APK.

**Ngày kiểm chứng: 16 và 17/11/2026.** Các phiên bản nêu dưới đây là bản đã thử, không mặc định là bản mới nhất. Kết quả được tác giả tổng hợp từ phiên chạy thật; ảnh và log riêng tư không được công khai. Người đọc cần tự tái lập, không coi các bảng tổng hợp trong repo là raw evidence có thể audit độc lập.

## A32 Android 13: đường root mới

Đã kiểm controller riêng khởi động bằng root UID 0 rồi chạy helper system UID 1000, không dùng Shizuku cho thao tác. Đọc node, bấm, nhập Unicode, chụp, chờ 90 giây và cleanup sau worker treo đều pass khi panel thật ở DOZE/DOZE_SUSPEND. Root UID 0 thuần vẫn lỗi package/UID. Đây không phải sửa nút Root hay serving MCP của app gốc; chưa kiểm PIN/pattern, idle dài hoặc reboot.

[A32 root workflow and evidence boundaries (English)](docs/a32-root-android13.md)

## Pixel 10 Pro XL / Android 17: kết quả mới

Kết quả mới ngày 2026-11-17: controller tùy biến dùng CompanionDeviceManager (CDM) `APP_STREAMING` + `VirtualDeviceManager`, non-root với shell UID `2000`, không dùng cờ `OWN_DISPLAY_GROUP`, đã kiểm coordinate tap, native swipe, nhập Unicode và Calculator cho kết quả 56 khi máy khóa bảo mật, vật lý `OFF`. Sau 308,7 giây idle không gọi helper, coordinate tap vẫn đổi counter `1 → 2`; trạng thái vật lý được lấy mẫu, không giám sát liên tục. Đây không phải stock MCP/Shizuku; không tự bật Wireless debugging. Cleanup đã khôi phục association/role và settings, dọn tài nguyên của phiên.

Kết quả cũ vẫn được giữ: VirtualScreen + Shizuku shell qua workaround nguồn riêng cho display đã qua semantic click/set-text khi khóa/tắt, nhưng coordinate tap lúc đó FAIL. Phiên WhatsApp đọc/gửi theo yêu cầu chỉ được kiểm khi mở khóa, trên màn hình ảo trong khi TikTok vẫn foreground ở các lần lấy mẫu, rồi trả WhatsApp về nền. Không suy thành WhatsApp chạy khi khóa, mọi app đều hỗ trợ, không giành focus thoáng qua, hoặc tự phục hồi sau reboot/mất mạng.

[Pixel workflow and evidence boundaries (English)](docs/pixel-android17.md)

## Xiaomi Pad Mini / Android 16: tách rõ ba loại bằng chứng

Ngày 17/11/2026, Mika 0.1.44 non-root đã chạy **self-check của chính app qua serving helper hiện có** khi khóa bảo mật, màn hình vật lý `OFF`: 12 pass, 0 partial, 0 fail, 0 skipped trong 42 giây. Host UI riêng chỉ tạm đưa task Mika lên màn hình ảo và thao tác UI, không thay serving helper; tiến trình app/helper gốc giữ nguyên. Task được trả về nền trước khi đóng display, APK/settings không đổi. Đây là kết quả mới, khác các self-check mở khóa và probe native độc lập trước đó, không phải model-AI E2E.

Một phiên riêng đã gửi **đúng một** tin thử được yêu cầu tới Telegram Saved Messages của chính người dùng khi khóa/tắt, bằng host native độc lập từ APK Mika đang cài + UIAutomation, không qua serving RPC hay AI. Đã đọc lại đích và draft trước Send, xác nhận UI `Sent`/`Seen`, composer trống rồi trả task về nền; `Seen` trong Saved Messages không chứng minh người khác đã đọc. Trạng thái vật lý và main task chỉ được kiểm tại các mẫu, không phải trace liên tục. Chi tiết tiếng Anh: [Xiaomi workflow](docs/xiaomi-pad-mini-android16.md) và [ma trận nghiệm thu](docs/acceptance-matrix.md).

## Kết luận ngắn

1. **Có root chưa chắc chạy được; không root vẫn có thể chạy.** A32 đã root nhưng Root backend của Virtual Screen bị lỗi package/UID. Đổi sang Shizuku chạy bằng ADB, UID `2000(shell)`, thì luồng kiểm tra hoạt động.
2. **Tắt màn hình khác với khóa PIN/pattern.** A32 được kiểm ở trạng thái màn hình tắt nhưng `keyguard showing=false`. Không dùng kết quả đó để khẳng định đã kiểm khóa bảo mật.
3. **Pad Mini non-root đạt 12/12 cả khi khóa bảo mật.** Self-check mới của app qua serving helper đạt 12/12 trong 42 giây khi vật lý `OFF`. Probe cũ và Telegram dùng host native độc lập là đường khác; chưa kiểm model-AI E2E.
4. **Khôi phục helper đã có bằng chứng giới hạn mới.** Sau khi Mika pair trực tiếp qua UI, thử khi mở khóa/`Awake`, giữ Wireless debugging bật: dừng đúng shell helper bằng `TERM`, app tự tạo helper mới trong khoảng 5 giây, không rescue hay start thủ công; self-check sau đó đạt 12/12 trong 41 giây. Lỗi mất kết nối khi khóa trước đó vẫn được giữ, nguyên nhân chưa rõ; chưa kiểm tắt Wireless debugging khi khóa, reboot, long idle hoặc roaming.

## Ma trận đã kiểm

| Thiết bị / cách chạy | Kết quả quan sát | Giới hạn |
|---|---|---|
| Samsung A32, Android 13 / One UI 5.1, đã root; Virtual Screen 0.2.1 Root backend | `ROOT_OPERATION_FAILED`, chi tiết `SecurityException: packageName must match the calling uid` | Kết quả của ROM/backend này, không khái quát mọi máy root |
| A32, Shizuku 13.6.0 khởi động qua ADB | MCP liệt kê 19 tools; mở Settings, đọc node, chạm và gõ đã kiểm khi màn hình vật lý `DOZE_SUSPEND` | Không có keyguard bảo mật đang hiển thị; không phải toàn bộ 19 tools đều được chạy lại |
| Self-check UI của Virtual Screen trên A32 | Lượt đầu 18/19, Tap lỗi | Lượt tap/type riêng sau đó thành công không xóa kết quả lỗi ban đầu |
| Lịch sử mở khóa: Xiaomi Pad Mini, Android 16, non-root, Mika 0.1.44 build `2b26f3f` | Self-check trong app đều 12 pass, 0 partial, 0 fail, 0 skipped: baseline 42 giây, sau pairing 41 giây, sau recovery 41 giây | Kiểm khi mở khóa; recovery chỉ thử helper chết khi `Awake`, Wireless debugging bật |
| Probe cũ: Pad Mini, khóa thật và màn hình tắt | Backend native của APK đang cài: tạo display, đọc node, tap tăng bộ đếm, gõ có readback; `Asleep`, `OFF`, `showing=true` | Tiến trình shell chẩn đoán riêng, không gọi RPC helper đang phục vụ Mika, không phải app/AI E2E |
| Pad Mini khóa thật, TikTok Studio 44.6.3 | Mở app và chụp frame thật 1880×3008 trên virtual display | Chỉ mở/chụp; không đăng bài hoặc thao tác tài khoản |
| Pad Mini, khóa bảo mật, vật lý `OFF`, 17/11 | Self-check UI Mika qua serving helper hiện có: 12 pass, 0 partial, 0 fail, 0 skipped, 42 giây | Host UI riêng; app/helper gốc giữ nguyên; không phải model-AI E2E |
| Pad Mini, Telegram Saved Messages, khóa/tắt, 17/11 | Đúng một tin được yêu cầu; đích/draft kiểm trước Send; UI `Sent`/`Seen`, composer trống | Host native độc lập + UIAutomation, không serving RPC/AI; `Seen` chỉ trong Saved Messages; task trả về nền |

Chi tiết lịch sử pass/fail và cách nghiệm thu: [Observed results](docs/observed-results.md). [Dữ liệu tổng hợp](examples/observations.json) không phải log gốc.

## Chọn hướng nào?

| Tình huống | Hướng thực tế | Điểm dễ hiểu nhầm |
|---|---|---|
| Máy đã root, `su` hoạt động | Thử Root backend chính thức với grant riêng cho đúng app | Root không tự vượt được kiểm tra package attribution hoặc chính sách display của ROM |
| Root backend lỗi, ADB đang dùng được | Chạy **Shizuku bằng ADB**, cấp quyền cho đúng app | Shizuku chạy bằng root và chạy bằng shell là hai identity khác nhau |
| Non-root, dùng Mika | Cài app; chọn script computer-start hoặc pair trực tiếp trong Mika | Mac đã paired ADB không có nghĩa Mika đã paired riêng; lần mới UI Mika đã hiện `Paired`/`Connected` |
| Không root và không ADB/helper | Xem API thông thường hoặc MediaProjection với sự đồng ý của user | Không tự có quyền nhập liệu xuyên app hay mở app khác trên màn hình nền riêng |
| App có xác thực hoặc nội dung được bảo vệ | Kiểm riêng app, theo luồng xác thực/chụp màn hình bình thường | Không vô hiệu hóa bảo vệ để biến ảnh đen thành ảnh chụp |

Xem hướng dẫn đầy đủ: [Giải pháp root/non-root](docs/solutions.md), [Chẩn đoán lỗi](docs/troubleshooting.md), [Tái lập từng bước](docs/reproduce.md).

## Ba tầng cần phân biệt

```mermaid
flowchart TD
    A[Máy điều khiển] -->|MCP qua ADB forward loopback| B[Virtual Screen]
    B --> C[Root backend hoặc Shizuku]
    A -->|ADB đã xác thực| D[Mika và helper]
    C --> E[Virtual display]
    D --> E
    E --> F[Task của app đích]
    F --> G[Frame ảnh và cây accessibility]
    H[Màn hình vật lý và keyguard] -. kiểm trạng thái riêng .-> E
```

- **Virtual Screen + MCP:** quản lý session, lease điều khiển, observation hiện hành, input, readback, khôi phục task về nền theo thỏa thuận trước khi close display, rồi giải phóng lease/session và tài nguyên của phiên.
- **Mika trong app:** self-check mới chạy UI của app qua serving helper hiện có khi khóa/tắt, 12/12 trong 42 giây; host UI chỉ di chuyển/chụp/bấm task. Không nhập model/API key hoặc chạy model-AI E2E.
- **Native độc lập:** probe cũ và phiên Telegram dùng backend từ APK Mika đang cài; Telegram thêm UIAutomation, không gọi serving RPC. Không nhập nhằng với self-check mới hoặc toàn bộ agent. Harness thử nghiệm phụ thuộc phiên bản không được đóng gói ở đây thành SDK hỗ trợ chung.

## A32: lịch sử stock Root lỗi, fallback Shizuku shell

Đoạn này ghi lại lỗi stock Root backend và fallback cũ, không phải controller root mới chạy helper system UID `1000` đã tóm tắt ở đầu và hướng dẫn trong [A32 root](docs/a32-root-android13.md).

Root đã tồn tại trước phiên thử; hướng dẫn này không flash máy, unlock bootloader hay cài root. Shell `su` vẫn hoạt động nhưng việc tạo display bằng Root backend bị ROM từ chối do package không khớp calling UID.

Cách đã chạy được là cài Shizuku chính thức, dùng **lệnh start qua ADB**, kiểm tiến trình server thuộc shell, rồi đổi backend của Virtual Screen sang Shizuku. Không thêm grant root cho Shizuku và không cấp quyền toàn cục cho app khác.

MCP chỉ nghe loopback; `adb forward` nối máy điều khiển tới cổng đó. Không bật tunnel public. Token lấy bằng UI/config chính thức, giữ ngoài repository và lịch sử lệnh. Luồng đúng là initialize, initialized, tools/list, acquire, create, launch/observe/action, restore task về nền theo thỏa thuận, close display, release lease và DELETE session; chỉ dọn tài nguyên thuộc phiên. Xem ví dụ và điều kiện từng bước trong tài liệu liên kết.

## Non-root: kinh nghiệm từ Pad Mini

Ban đầu Mika 0.1.44 dùng helper start từ máy tính qua kết nối ADB đã có, bằng script chính thức `usb-start.sh`. Lần mới đã pair trực tiếp trong UI Mika và quan sát `Paired`/`Connected`. Mac đã paired ADB vẫn không tương đương Mika đã paired.

Các thiết lập đã có sẵn gồm Accessibility bound, thông báo được phép, pin không hạn chế, autostart, khóa app trong Recent apps, `WRITE_SECURE_SETTINGS` và Wi-Fi trust. Hai tùy chọn recovery vốn đã bật; pairing trực tiếp nay đáp ứng prerequisite còn thiếu, không phải vừa bật các quyền hay tùy chọn đó. Không suy thành bảo đảm helper sống mãi hoặc tự phục hồi sau reboot.

Self-check đầu tiên đạt 11 pass và 1 partial do thông báo tắt. Sau khi bật thông báo, chạy lại được 12/12. Không hạ tiêu chí hoặc bỏ qua mục lỗi.

Khi khóa, đã kiểm riêng backend native và chụp được TikTok Studio trong khi panel vẫn `OFF`. Không nhập PIN/pattern, không bỏ keyguard. Ở phiên cũ, Wireless ADB mất và phải start lại helper thủ công; nguyên nhân chưa rõ, kết quả mới không xóa failure đó.

Lần thử recovery trước chỉ thử helper chết khi mở khóa/`Awake` và Wireless debugging vẫn bật: kiểm identity shell helper trước `TERM`, quan sát helper mới sau khoảng 5 giây, không rescue/manual start; self-check của chính Mika đạt 12 pass, 0 partial, 0 fail, 0 skipped trong 41 giây. Baseline 42 giây và sau pairing 41 giây cũng đều 12/12. Chưa kiểm Wireless debugging tắt khi khóa, reboot, long idle hoặc roaming. Xem [Wireless debugging và recovery](docs/wireless-debugging.md).

## Quy tắc tái lập

- Luôn dùng `adb -s "$SERIAL"` sau khi đối chiếu model và serial live; serial mDNS có thể đổi.
- Phân biệt ADB shell root, app `su`, quyền Shizuku và Accessibility. Giữ nguyên grant/service ngoài phạm vi.
- Kiểm màn hình vật lý theo display, không chỉ đọc `mWakefulness`: virtual display ON có thể làm giá trị tổng là `Awake` dù panel vẫn `DOZE_SUSPEND`.
- Mỗi thao tác cần observation mới và đúng display. Nếu không rõ thao tác đã gửi hay chưa, đọc lại trạng thái trước khi gửi lần nữa.
- Không tự force-stop app có task trên màn hình khác: có thể mất draft. Tôn trọng luồng xác nhận restart của công cụ.
- Nếu thử chuyển task thay vì restart, ghi lại task/display/focus ban đầu và xác minh khôi phục sau chụp; đây là cách chẩn đoán phụ thuộc ROM, không phải lệnh dùng mù cho mọi máy.
- Trước khi close display, khôi phục task về nền theo thỏa thuận; sau đó release lease/session, dọn tài nguyên thuộc phiên và đọc lại trạng thái. Rollback source không hoàn tác trạng thái điện thoại hay thu hồi tin đã gửi.

## Bản public không chứa raw evidence riêng tư

Các bảng trên là bản tổng hợp do tác giả báo cáo. Để tự xác nhận, chạy checklist trên thiết bị của bạn và ghi rõ backend, identity, trạng thái từng display, keyguard và state delta sau input. Không suy từ một ảnh chụp hoặc mã trả về thành thành công của toàn bộ luồng.

## Đọc tiếp

- [Kết quả thực nghiệm và giới hạn](docs/observed-results.md)
- [Giải pháp root/non-root](docs/solutions.md)
- [Hướng dẫn tái lập và cleanup](docs/reproduce.md)
- [Chẩn đoán theo triệu chứng](docs/troubleshooting.md)
- [Bảo vệ dữ liệu khi chia sẻ](docs/privacy.md)
- [Nguồn chính thức](docs/sources.md)

## Giấy phép

Tài liệu và ví dụ tự viết dùng [MIT](LICENSE). Mỗi dự án upstream giữ giấy phép riêng. Repo không phân phối APK, source tree upstream, token, serial cá nhân hay ảnh tài khoản thật; không đại diện cho các tác giả ứng dụng.
