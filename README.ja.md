# Android 仮想画面 実機検証ガイド

[Tiếng Việt](README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md) · [한국어](README.ko.md) · **日本語**

物理画面を消したまま、独立した仮想ディスプレイ上で Android アプリを操作した実機検証の記録です。
本リポジトリは**ドキュメントと再現手順**であり、完成済みの Android agent や APK 配布サイトではありません。すべてのアプリやロック状態での動作は保証しません。

**観察日：2026-11-16。** 以下は検証したバージョンであり、最新版を示すものではありません。
公開内容は著者が報告し、機密情報を除去した要約です。非公開の画面キャプチャや生ログは含みません。
そのため、公開要約を独立監査可能な生の証拠とは扱わず、読者自身で再現してください。

## 要点

- **Root は必要条件でも十分条件でもありません。** Root 済みの Samsung A32 では Virtual Screen の Root バックエンドが package/UID エラーで失敗しました。ADB から起動した shell UID `2000` の Shizuku では限定テストに成功しました。
- **非 root でも動作する経路があります。** Xiaomi Pad Mini の Mika 自己診断はロック解除中に 12/12 を通過しました。セキュアロック中は別途ネイティブバックエンドを診断しました。
- **画面オフとセキュアロックは別です。** A32 は `keyguard showing=false` でした。PIN/パターンでロックされた状態への一般化はできません。
- **バックエンドの成功は agent 全体の成功ではありません。** Pad Mini のロック中テストは稼働中 helper の RPC や Mika アプリ/AI の E2E を実行していません。モデルや API key も設定していません。
- **復旧には新たな限定的成功があります。** Mika で直接ペアリング後、ロック解除/`Awake` で Wireless debugging を有効のまま、実行主体を確認した shell helper に `TERM` を送りました。約 5 秒でアプリによる新 helper の生成を観察し、救済操作や手動起動なしで自己診断 12/12、41 秒を達成しました。以前のロック中の接続消失・手動復旧の失敗は原因不明のまま残し、無線デバッグを無効にしたロック状態、再起動、長時間アイドル、ネットワークローミングは未試験です。

## 実際に検証した範囲

| 端末と経路 | 観察結果 | 証拠の範囲 |
|---|---|---|
| Samsung A32、Android 13 / One UI 5.1、root 済み；Virtual Screen 0.2.1 Root バックエンド | `ROOT_OPERATION_FAILED`；`SecurityException: packageName must match the calling uid` | この ROM/バックエンドの組み合わせの結果であり、すべての root 実装の結果ではない |
| 同じ A32；ADB 起動の Shizuku 13.6.0；Virtual Screen MCP | 19 ツールを列挙；Settings 起動、ノード読取、タップ、文字入力を確認；物理画面は `DOZE_SUSPEND` | `keyguard showing=false`；19 ツールすべてを再試験したわけではない |
| 同じ A32；アプリ初回自己診断 | 18/19、Tap が失敗 | 後続の限定タップ/入力成功で初回の失敗を上書きしない |
| Xiaomi Pad Mini、Android 16、非 root；Mika 0.1.44、build `2b26f3f` | 自己診断はいずれも 12 pass、0 partial、0 fail、0 skipped：ベースライン 42 秒、ペアリング後 41 秒、復旧後 41 秒 | ロック解除中；復旧は `Awake`、Wireless debugging 有効時の helper 終了のみ検証 |
| 同じ Pad Mini；セキュアロック中かつ画面オフ | インストール済み APK の `ShellService` を独立した一時 shell プロセスで使用；表示作成、ノード読取、タップカウンター、入力読戻しに成功 | `Asleep`、物理 `OFF`、`showing=true`；稼働中 helper の RPC やアプリ/AI E2E ではない |
| 同じ Pad Mini；セキュアロック中；TikTok Studio 44.6.3 | 実アプリの起動と 1880×3008 フレームの取得に成功；物理画面はオフを維持 | 起動と取得のみ。投稿やアカウント操作は未実施 |

成功と失敗の詳細は[検証結果](docs/observed-results.md)を参照してください。[機密情報除去済みデータ](examples/observations.json)は生の trace ではありません。

## 経路の選び方

| 条件 | 最初に試す経路 | 留意点 |
|---|---|---|
| すでに root 済みで `su` が動く | アプリが対応する Root バックエンドに個別許可を付与 | Root だけで package attribution、表示ポリシー、ROM 差異が解消されるわけではない |
| Root バックエンドが失敗し、承認済み ADB が使える | **ADB で Shizuku を起動**し、対象アプリのみ承認 | UID `2000` を確認。root 起動とは実行主体が異なる |
| Mika の要件を満たす非 root 端末 | Mika をインストールし、選択した端末の ADB から公式 helper を起動 | Mac の ADB ペアリングは Mika 自身のペアリングとは別 |
| Root も ADB/helper もない | 通常のアプリ API やユーザー同意に基づく MediaProjection を検討 | 任意のアプリ間入力や独立したバックグラウンド画面を自動で得られるわけではない |
| 保護されたアプリやコンテンツ | アプリごとの通常の認証・キャプチャ規則で確認 | 通常の取得成功は `FLAG_SECURE` や DRM の取得を証明しない |

詳細は [Root / 非 root の方式](docs/solutions.md)と[トラブルシューティング](docs/troubleshooting.md)にあります。

## 混同してはいけない三つの制御経路

1. **Virtual Screen + MCP**：アプリ承認、session、制御 lease、最新 observation、操作、読戻し、後片付けを扱います。
2. **Mika の通常のアプリ経路**：専用 helper、Accessibility サービス、アプリ側の処理と任意のモデル設定を利用します。
3. **独立したネイティブ診断**：一時 shell プロセスがインストール済み Mika APK の `ShellService` を読み込み、端末とバックエンドの能力を確認します。

三番目は Mika アプリ側の処理や、稼働中 helper の RPC を検証したものではありません。
本番用リモート制御エンドポイントでもありません。バージョン依存の実験 harness は汎用 SDK として配布しません。
物理画面、仮想画面、keyguard の状態は別々に記録します。
仮想画面が有効なために端末全体が `Awake` でも、物理パネルは `DOZE_SUSPEND` の場合があります。

## A32：root の有無だけで判断しない

端末は実験開始前から root 済みでした。本ガイドに ROM 書込み、bootloader 解除、root 導入手順は含みません。
`su` は動作しましたが、Root バックエンドの表示作成は package/UID 検査で拒否されました。上流の具体的な不具合箇所は特定していません。
成功した経路では、公式の ADB 方式で Shizuku を起動し、shell の実行主体を確認してから Virtual Screen で選択しました。
Shizuku に root 許可を追加したり、無関係なアプリへ広範な許可を与えたりする必要はありません。
MCP は認証を維持して loopback のみに置き、選択した端末の ADB forward 経由で接続します。
ツール引数はインストール済みサーバーの schema を基準にし、最新 observation を確認してから入力し、読戻しで確かめます。

## Pad Mini：互換性と復旧を分ける

Mika 0.1.44 は当初、既存の承認済み ADB 経路で公式のコンピューター起動スクリプト `usb-start.sh` を使用しました。
その後、Mika 自身の UI で直接ペアリングし、`Paired`/`Connected` を観察しました。Mac の ADB ペアリングと Mika 自身のペアリングは別です。
`WRITE_SECURE_SETTINGS` と Wi-Fi trust はすでにあり、二つの復旧トグルも以前から有効でした。直接ペアリングで不足していた前提条件を満たしたのであり、これらの許可やトグルを新たに有効にしたわけではありません。
最初の自己診断は通知無効により 11 pass、1 partial でした。通知を有効にして再実行し、12/12 になりました。
Accessibility、通知、電池制限解除、自動起動、履歴画面での固定は準備であり、helper の永続稼働を保証しません。
ロック中の診断では PIN/パターンを入力せず、物理 keyguard も解除せず、独立画面のネイティブ機能のみ確認しました。
以前のロック中セッションで Wireless ADB が消失し、再接続後も helper の手動起動が必要だった失敗は残します。原因はまだ特定されていません。
今回はロック解除/`Awake` かつ Wireless debugging を有効のまま、実行主体を確認した shell helper に `TERM` を送り、約 5 秒後にアプリが作成した新 helper を観察しました。救済操作や手動起動は行いませんでした。
Mika 自身の復旧後診断は 12 pass、0 partial、0 fail、0 skipped、41 秒でした。ベースライン 42 秒とペアリング後 41 秒も 12/12 でした。
無線デバッグを無効にしたロック状態、端末再起動、長時間アイドル、ネットワークローミングは未試験です。helper 単体の復旧を AI E2E 成功と解釈しないでください。[Wireless debugging と復旧](docs/wireless-debugging.md)を参照してください。

## 許可・入力・ライフサイクルの注意

- 現在のモデルと serial を照合し、全 ADB コマンドに `adb -s "$SERIAL"` を明記します。公開資料では識別子をプレースホルダーに置き換えます。
- ADB shell、アプリ `su`、Shizuku、Accessibility の許可を区別し、無関係な許可やサービスを維持します。
- 認証情報はアプリが対応する UI/設定のみで扱い、コマンド履歴、ログ、画像、リポジトリへ保存しません。
- bearer 認証付きコントローラーを公開 tunnel に露出させず、loopback の転送を当該テストのみに使います。
- 入力前に display、task、focus と新しい observation を確認します。送達が不明なら再入力より先に状態を読みます。
- 別画面に既存 task があるという理由だけで強制停止や再起動をしません。下書き消失を避け、ツールの確認フローを守ります。
- 合意した試験で task を移動する場合は元の位置と focus を記録し、復元後に検証します。ROM 固有コマンドを汎用手順にしません。
- 試験用画面を閉じ、lease/session と当該 forward を解放し、物理画面とアプリ状態を再確認します。

## 再現の推奨順序

1. 端末と公式 APK の入手元、バージョン、hash を確認します。
2. バックエンドの実行主体を確かめ、対象アプリに必要な許可だけを付与します。
3. ロック解除中に自己診断を実行し、前提条件を修正して関連項目を再試験します。初回失敗も残します。
4. Settings や無害なテストページで起動、観察、一回の限定入力、読戻しを確認します。
5. ユーザーがロック状態を明示的に管理し、画面オフとセキュア keyguard を別々に記録して限定試験を繰り返します。
6. 接続断、helper 終了、アイドル、端末再起動を別項目で試験し、未実施なら未検証と記載します。
7. バージョン、実行主体、状態、結果のみを機密情報除去後に公開し、アカウント、ネットワーク識別子、生画像、個人パスを除きます。

## 詳細ドキュメント

以下の詳細文書は英語です。

- [結果と検証範囲](docs/observed-results.md)、[方式の説明](docs/solutions.md)
- [再現と後片付け](docs/reproduce.md)、[症状別診断](docs/troubleshooting.md)
- [公開時のプライバシー](docs/privacy.md)、[公式資料と固定バージョン](docs/sources.md)
- [English README](README.en.md)

## ライセンスと上流プロジェクト

本ガイドと独自の例は [MIT ライセンス](LICENSE)です。上流アプリにはそれぞれのライセンスが適用されます。
上流 APK、ソースツリー、認証情報、非公開キャプチャは再配布せず、上流の保守担当者を代表するものではありません。
導入方法やバージョン変更は [android-virtual-screen、Shizuku、Mika の公式資料](docs/sources.md)を確認してください。
