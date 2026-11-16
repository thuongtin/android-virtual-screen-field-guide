# Android 가상 화면 실험 가이드

[Tiếng Việt](README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md) · **한국어** · [日本語](README.ja.md)

실제 Android 기기에서 물리 화면을 끈 채 별도의 가상 디스플레이로 앱을 제어한 실험 기록입니다.
이 저장소는 **문서와 재현 가이드**이며, 완성된 Android agent나 APK 배포처가 아닙니다. 모든 앱과 잠금 상태의 호환성을 보장하지 않습니다.

**관찰 날짜: 2026-11-16.** 아래 버전은 시험한 버전이며 최신 버전이라는 뜻은 아닙니다.
결과는 작성자가 보고하고 비식별 처리한 요약입니다. 비공개 캡처와 원본 로그는 공개하지 않습니다.
따라서 공개 요약을 독립적으로 감사 가능한 원본 증거로 취급하지 말고 직접 재현해야 합니다.

## 핵심 결론

- **Root는 필요조건도 충분조건도 아닙니다.** Root가 있는 Samsung A32에서 Virtual Screen의 Root 백엔드는 package/UID 오류로 실패했습니다. ADB로 시작한 shell UID `2000`의 Shizuku 경로는 작동했습니다.
- **Root 없이도 가능한 경로가 있습니다.** Xiaomi Pad Mini의 Mika 자체 점검은 잠금 해제 상태에서 12/12를 통과했습니다. 보안 잠금 상태에서는 별도의 네이티브 백엔드 진단을 수행했습니다.
- **화면 꺼짐과 보안 잠금은 다릅니다.** A32는 `keyguard showing=false`였으므로 PIN/패턴 잠금 결과로 일반화할 수 없습니다.
- **백엔드 성공은 agent 전체 성공이 아닙니다.** Pad Mini 잠금 실험은 서비스 중인 helper RPC나 Mika 앱/AI E2E를 실행하지 않았습니다. 모델이나 API key도 설정하지 않았습니다.
- **복구에 제한된 성공 결과가 추가됐습니다.** Mika 직접 페어링 후 잠금 해제/`Awake` 상태에서 Wireless debugging을 켜 둔 채 신원을 확인한 shell helper에 `TERM`을 보냈습니다. 약 5초 후 앱이 만든 새 helper를 관찰했고 구조 작업이나 수동 시작 없이 자체 점검 12/12를 41초에 통과했습니다. 이전 잠금 상태의 전송 단절/수동 복구 실패는 원인 미상으로 보존하며, 무선 디버깅을 끈 잠금 상태, 재부팅, 장시간 유휴와 네트워크 로밍은 미시험입니다.

## 실제로 시험한 범위

| 기기와 경로 | 관찰 결과 | 증거의 범위 |
|---|---|---|
| Samsung A32, Android 13 / One UI 5.1, root; Virtual Screen 0.2.1 Root 백엔드 | `ROOT_OPERATION_FAILED`; `SecurityException: packageName must match the calling uid` | 이 ROM/백엔드 조합의 결과이며 모든 root 구현에 대한 결론은 아님 |
| 같은 A32; ADB로 시작한 Shizuku 13.6.0; Virtual Screen MCP | 도구 19개 나열, Settings 실행·노드 읽기·탭·입력 확인; 물리 화면 `DOZE_SUSPEND` | `keyguard showing=false`; 도구 19개를 모두 재시험한 것은 아님 |
| 같은 A32; 첫 앱 자체 점검 | 18/19, Tap 실패 | 나중의 제한된 탭/입력 성공이 최초 실패를 지우지 않음 |
| Xiaomi Pad Mini, Android 16, non-root; Mika 0.1.44, build `2b26f3f` | 자체 점검 모두 12 pass, 0 partial, 0 fail, 0 skipped: 기준 42초, 페어링 후 41초, 복구 후 41초 | 잠금 해제 상태; 복구는 `Awake` 및 Wireless debugging 활성 상태의 helper 종료만 시험 |
| 같은 Pad Mini; 보안 잠금 및 화면 꺼짐 | 설치된 APK의 `ShellService`를 별도 임시 shell 프로세스로 실행하여 디스플레이 생성·노드 읽기·탭 카운터·입력 회독 확인 | `Asleep`, 물리 `OFF`, `showing=true`; 서비스 중인 helper RPC 또는 앱/AI E2E가 아님 |
| 같은 Pad Mini; 보안 잠금; TikTok Studio 44.6.3 | 실제 앱 실행 및 1880×3008 프레임 캡처, 물리 화면은 꺼진 상태 유지 | 실행과 캡처만 수행, 게시나 계정 작업 없음 |

자세한 성공·실패 이력은 [실험 결과](docs/observed-results.md)를 참고하세요. [비식별 데이터](examples/observations.json)는 원본 trace가 아닙니다.

## 어떤 경로를 선택할까

| 상황 | 시작점 | 주의할 한계 |
|---|---|---|
| 이미 root가 있고 `su`가 동작함 | 앱이 지원하는 Root 백엔드에 앱별 권한 부여 | Root만으로 package attribution, 디스플레이 정책, ROM 차이가 사라지지 않음 |
| Root 백엔드 실패, 승인된 ADB 사용 가능 | **ADB로 Shizuku 시작**, 대상 앱만 승인 | UID `2000` 확인; root로 시작한 서비스는 다른 실행 주체 |
| Mika 지원 조건을 만족하는 non-root 기기 | Mika 설치 후 선택한 기기의 ADB로 공식 helper 시작 | Mac의 ADB 페어링은 Mika 자체 페어링과 다름 |
| Root도 ADB/helper도 없음 | 일반 앱 API 또는 사용자 동의 기반 MediaProjection 검토 | 임의의 앱 간 입력이나 독립 백그라운드 앱 화면을 자동 제공하지 않음 |
| 보호된 앱 또는 콘텐츠 | 해당 앱의 정상 인증·캡처 규칙으로 개별 시험 | 일반 캡처 성공은 `FLAG_SECURE`나 DRM 캡처의 증거가 아님 |

구체적인 절차는 [Root/non-root 솔루션](docs/solutions.md)과 [문제 해결](docs/troubleshooting.md)에 있습니다.

## 서로 다른 세 가지 제어 경로

1. **Virtual Screen + MCP**: 앱 승인, session, 제어 lease, 최신 observation, 동작, 회독, 정리로 구성됩니다.
2. **Mika의 정상 앱 흐름**: 자체 helper, Accessibility 서비스, 앱 오케스트레이션과 선택적 모델 설정을 사용합니다.
3. **독립 네이티브 진단**: 임시 shell 프로세스가 설치된 Mika APK의 `ShellService`를 로드하여 기기와 백엔드 능력을 시험합니다.

세 번째 경로는 Mika 앱 오케스트레이션이나 서비스 중인 helper RPC를 검증하지 않았습니다.
프로덕션 원격 제어 엔드포인트를 제공한 것도 아닙니다. 버전 의존적인 실험 harness는 지원 SDK로 배포하지 않습니다.
물리 디스플레이, 가상 디스플레이와 keyguard 상태를 각각 기록해야 합니다.
가상 화면 때문에 기기 전체가 `Awake`여도 물리 패널은 `DOZE_SUSPEND`일 수 있습니다.

## A32: root 여부보다 실행 주체가 중요

기기는 실험 전부터 root 상태였습니다. 이 가이드는 플래싱, bootloader 잠금 해제 또는 root 설치를 다루지 않습니다.
`su`는 동작했지만 Root 백엔드의 디스플레이 생성은 package/UID 검사에서 거부됐습니다. 정확한 상위 프로젝트 결함은 특정하지 않았습니다.
성공한 경로는 공식 ADB 방식으로 Shizuku를 시작하고 shell 주체를 확인한 뒤 Virtual Screen에서 해당 백엔드를 선택하는 방식입니다.
Shizuku에 root 권한을 추가하거나 무관한 앱에 전역 권한을 줄 필요는 없습니다.
MCP는 인증을 유지하고 loopback에서만 제공하며, 선택한 기기의 ADB forward로 연결합니다.
도구 인자는 설치된 서버의 schema를 기준으로 하고 최신 observation 확인 후 입력하고 다시 읽어 결과를 확인합니다.

## Pad Mini: 호환성과 복구를 분리

Mika 0.1.44는 처음에 기존 승인된 ADB 채널에서 공식 컴퓨터 시작 스크립트 `usb-start.sh`를 사용했습니다.
이후 Mika 자체 UI에서 직접 페어링하여 `Paired`/`Connected`를 관찰했습니다. Mac의 ADB 페어링과 Mika 자체 페어링은 여전히 별개입니다.
`WRITE_SECURE_SETTINGS`와 Wi-Fi trust는 이미 있었고 두 복구 토글도 원래 켜져 있었습니다. 이번 직접 페어링은 누락된 전제 조건을 충족했으며 해당 권한이나 토글을 새로 켠 것이 아닙니다.
첫 자체 점검은 알림 비활성화로 11 pass, 1 partial이었습니다. 알림을 켠 뒤 재실행하여 12/12를 얻었습니다.
Accessibility, 알림, 배터리 제한 해제, 자동 시작, 최근 앱 고정은 환경 준비이지 helper 영구 실행 보장이 아닙니다.
잠금 진단은 PIN/패턴을 입력하거나 물리 keyguard를 해제하지 않고 별도 화면의 네이티브 기능만 시험했습니다.
이전 잠금 세션에서 Wireless ADB가 사라지고 재연결 후에도 helper 수동 시작이 필요했던 실패는 보존하며, 원인은 아직 확인되지 않았습니다.
이번에는 잠금 해제/`Awake` 상태와 Wireless debugging 활성 상태를 유지하고 신원을 확인한 shell helper에 `TERM`을 보냈습니다. 약 5초 후 앱이 만든 새 helper를 관찰했으며 구조 작업이나 수동 시작은 없었습니다.
Mika 자체 복구 후 점검은 12 pass, 0 partial, 0 fail, 0 skipped, 41초였습니다. 기준 42초와 페어링 후 41초도 모두 12/12였습니다.
무선 디버깅을 끈 잠금 상태, 재부팅, 장시간 유휴와 네트워크 로밍은 미시험이며 helper 단독 복구는 AI E2E 성공이 아닙니다. [Wireless debugging과 복구](docs/wireless-debugging.md)를 참고하세요.

## 권한과 수명 주기 규칙

- 현재 모델과 serial을 확인하고 모든 ADB 명령에 `adb -s "$SERIAL"`을 명시합니다. 공개 자료에는 식별자 대신 자리표시자를 씁니다.
- ADB shell, 앱 `su`, Shizuku와 Accessibility 승인을 구분하고 다른 승인과 서비스를 보존합니다.
- 인증 정보는 앱이 지원하는 UI/설정으로만 확인하며 명령 기록, 로그, 캡처 또는 저장소에 남기지 않습니다.
- bearer 인증 제어기를 공개 tunnel에 노출하지 않습니다. loopback forward는 해당 시험에만 사용합니다.
- 입력 전에 display, task, focus와 최신 observation을 확인합니다. 전달 여부가 불확실하면 재입력 전에 상태를 읽습니다.
- 다른 화면에 기존 task가 있다는 이유만으로 앱을 강제 종료하거나 재시작하지 않습니다. 초안이 사라질 수 있으므로 도구 승인 흐름을 따릅니다.
- 동의된 시험에서 task를 이동한다면 원래 위치와 focus를 기록하고 복원 후 검증합니다. ROM별 명령을 범용 절차로 취급하지 않습니다.
- 시험용 디스플레이를 닫고 lease/session과 해당 forward를 해제한 뒤 물리 화면과 앱 상태를 다시 확인합니다.

## 재현 권장 순서

1. 기기와 공식 APK의 출처, 버전 및 hash를 확인합니다.
2. 백엔드 실행 주체를 확인하고 대상 앱에 필요한 권한만 부여합니다.
3. 잠금 해제 상태에서 자체 점검을 실행합니다. 전제 조건을 수정한 뒤 관련 항목을 재시험하고 초기 실패도 보존합니다.
4. Settings 또는 무해한 테스트 페이지에서 실행, 관찰, 한 번의 제한된 입력과 회독을 확인합니다.
5. 사용자가 잠금 상태를 직접 정한 뒤 화면 꺼짐과 보안 keyguard를 별도로 기록하며 제한된 시험을 반복합니다.
6. 전송 단절, helper 종료, 유휴 상태와 재부팅을 별도 시험합니다. 미실행 항목은 미검증으로 표시합니다.
7. 버전, 실행 주체, 상태와 결과만 비식별 공개하고 계정, 네트워크 식별자, 원본 캡처와 개인 경로는 제외합니다.

## 상세 문서

다음 상세 문서는 영어로 제공됩니다.

- [관찰 결과와 한계](docs/observed-results.md), [솔루션](docs/solutions.md)
- [재현 및 정리](docs/reproduce.md), [실패 진단](docs/troubleshooting.md)
- [공개 자료의 개인정보 처리](docs/privacy.md), [공식 출처와 고정 버전](docs/sources.md)
- [English README](README.en.md)

## 라이선스와 출처 표기

이 가이드와 직접 작성한 예제는 [MIT 라이선스](LICENSE)를 따릅니다. 상위 프로젝트의 앱에는 각자의 라이선스가 적용됩니다.
이 저장소는 상위 APK, 소스 트리, 인증 정보나 개인 캡처를 재배포하지 않으며 해당 유지관리자를 대변하지 않습니다.
설치 방법과 버전 변경은 [android-virtual-screen, Shizuku, Mika 공식 출처](docs/sources.md)를 확인하세요.
