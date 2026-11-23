# Folio 繁體中文 Fork（台灣）

這是 [McCal-Codes/folio](https://github.com/McCal-Codes/folio) 的非官方繁體中文 Fork。保留官方程式，另外維護 `translation/zh-TW.json`，每天自動檢查官方 `main` 分支並嘗試合併。任何合併衝突都會使 GitHub Actions 停止，不會強制覆蓋翻譯。

## 已加入的檔案
- `translation/zh-TW.json`：繁體中文翻譯（目前 104 條）
- `tools/generate_locale.py`：驗證資源鍵值、格式參數並產生 `app/src/main/res/values-zh-rTW/strings.xml`
- `.github/workflows/folio-zh-tw.yml`：每日自動同步、建立已簽章 APK、發布 GitHub Release

其他尚未翻譯的字串會由 Android 回退為英文。官方新功能如有新增英文文字，需要繼續補翻。建置會使用 **官方 main 分支**，可能含測試中功能，不等同正式穩定版。

## 首次使用前：建立固定簽章

簽章用來保證以後每次安裝更新可以直接覆蓋繁中版本，絕對不要提交私鑰到公開 Repository。

在自己的電腦終端機執行：

```sh
keytool -genkeypair -v -keystore folio-zh-tw.jks -alias foliozh -keyalg RSA -keysize 3072 -validity 10000
```

請將 `folio-zh-tw.jks` 與密碼保存在安全位置，並額外離線備份；金鑰遺失後，新的金鑰無法直接更新已安裝版本。

產生 Base64 字串（macOS）：

```sh
base64 -i folio-zh-tw.jks | tr -d '\n'
```

到 [Actions Secrets](https://github.com/jack31016/folio/settings/secrets/actions) 新增四個 **Repository secrets**：

| 名稱 | 值 |
| --- | --- |
| `FOLIO_KEYSTORE_BASE64` | 上面 Base64 輸出的整串 |
| `FOLIO_STORE_PASSWORD` | 金鑰庫密碼 |
| `FOLIO_KEY_ALIAS` | `foliozh` |
| `FOLIO_KEY_PASSWORD` | 金鑰密碼（通常等同金鑰庫密碼） |

接著到 [Actions 設定](https://github.com/jack31016/folio/settings/actions) 確保 Actions 已啟用，Workflow permissions 能寫入內容（Read and write permissions）。如第一次需要啟用排程，請到 [Actions](https://github.com/jack31016/folio/actions) 選取 **Folio zh-TW automatic build** 後按 **Run workflow**。

完成成功建置後，會在 [Releases](https://github.com/jack31016/folio/releases) 出現 `Folio-zh-TW.apk`，之後可在 Android 的 Obtainium 加入此 Fork 的 Releases 來檢查更新。

## 安裝與更新注意事項

- 目前 Fork 的 release package name 與官方 Folio 相同（`com.mccal.folio`），但簽章不同，因此**無法覆蓋官方原版**。
- 第一次安裝繁中版前，請務必先備份官方 Folio 桌面配置到 App 之外，並確認備份檔可取回。移除官方版可能同時刪除原始 App 資料。
- 之後只要簽章私鑰保持一致、versionCode 持續增加，就能用 Obtainium 更新繁中版本。不要用 Folio 官方內建更新器安裝不同簽章的 APK。
- 若上游發生合併衝突、Android 編譯失敗、簽章缺失或發行失敗，Actions 會顯示失敗，**不代表已成功發行更新**。
- 發布流程已加入遞增的繁中版 versionCode / versionName，以避免官方相同版本號下的多次提交無法更新。

## 狀態

本 Fork 已部署原始碼、翻譯及自動化設定，但目前**尚未驗證完成第一個已簽章 APK 編譯**，也尚未於手機實測。先完成簽章 secrets 才能正式發布。

翻譯與自動化皆非官方專案的一部分，請勿在公開儲存庫留下任何帳號密碼、金鑰、手機設定備份或個人資料。
