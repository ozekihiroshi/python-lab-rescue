# Python LabとMoodleの接続

Labの実行・保存はこのリポジトリ、教材・受講者・評定はMoodleが管理します。両者はLTI 1.3登録情報JSONで接続します。Java Labも同じ「登録→出力→取り込み」の手順です。

## 管理者の初回接続（ローカルHTTP）

Moodle側の[登録アダプター](https://github.com/ozekihiroshi/moodle-rescue/blob/main/docs/lab-connection-setup.md)を使います。mainに含まれる共通手順です。MoodleとDockerネットワークを先に起動してください。

Moodleリポジトリで実行:

```sh
python3 scripts/register-lab.py --lab python --url http://localhost:8086 \
  --name "Python Lab" --output build/lab-connections/python.json --apply
```

未登録の場合だけ登録を作成します。既存登録の確認・出力だけなら`--apply`を省きます。コースや学生は作成しません。

Python Labリポジトリで実行:

```sh
python3 scripts/setup.py connect ../moodle-rescue/build/lab-connections/python.json
docker compose -f docker-compose.local.yml -f docker-compose.lti.yml config --quiet
sh scripts/start-local.sh
python3 scripts/verify-lti-config.py
```

新規LTI導入では`.env.example`をコピーする前に`connect`を実行します。必要な`.env`を生成し、ローカルログインを無効にします。Composeの必須項目であるローカルパスワードはランダム生成しますが、LTI認証では使用しません。初期管理者は空です。

既存LTI環境では保存先・ネットワーク・イメージ・直接提出設定を維持します。異なるClient ID、Moodle URL、ポート、利用者識別キーへの上書きを拒否し、元の設定を`runtime/env-before-connect`へ一度だけ保存します。JSONと設定はGit管理外です。既存の単独ログイン環境は利用者名の対応が異なるため、そのままLTIへ切り替えられません。別のチェックアウト、Composeプロジェクト、ポート、ネットワーク、利用者ボリューム接頭辞を用意してください。既存データを削除して回避しないでください。

**直接提出を有効にしている既存環境**は、上記`start-local.sh`の代わりに従来の`sh scripts/start-lti-submit-local.sh`を使います。取り込みは直接提出機能を有効化せず、秘密鍵や提出先も変更しません。設定・イメージ変更の反映で再起動する際は、学生へ保存を周知してください。

既定のMoodle内部接続はネットワーク`moodle-rescue-local_local_access`と`http://moodle-rescue-local/mod/lti/certs.php`です。異なる構成では`.env`の`MOODLE_DOCKER_NETWORK`と`MOODLE_JWKS_UPSTREAM`を設定します。`MOODLE_CANONICAL_HOST`はJSONから取り込みます。取り込みだけでDockerネットワークは作られません。HTTPS公開用は既存の本番導入手順を使用します。

## 教師の教材設定

Moodleのコースに外部ツール活動を追加し、登録済みPython Labを選びます。新しいウィンドウで開き、例えば`http://localhost:8086/hub/user-redirect/lab/tree/00_start_here.ipynb`を指定します。対象ノートブックがLabに含まれることを確認してください。学生はMoodleの受講アカウントで起動します。教材本文や提出課題は別に用意します。

## 確認と運用

`python3 scripts/test_setup.py`で新規設定・再取り込み・誤接続拒否を確認できます。サービス起動後はMoodleの学生アカウントで起動・実行・保存を確認してください。

基本LTI構成の状態・ログ・データを残した停止:

```sh
docker compose -f docker-compose.local.yml -f docker-compose.lti.yml ps
docker compose -f docker-compose.local.yml -f docker-compose.lti.yml logs --tail 100
docker compose -f docker-compose.local.yml -f docker-compose.lti.yml stop
```

直接提出構成では各コマンドに`-f docker-compose.submit-v4.yml`も加えます。Hubの停止は個別の学生コンテナの停止を意味しません。全体の停止にはMoodleリポジトリの共通環境操作入口を使うか、Hub管理画面で学生サーバーを停止してからComposeを停止します。保存領域を消す`down -v`は使用しません。

検証（2026-09-22）: 6件の自動テスト、新規設定のCompose検証、既存設定の再取り込みと直接提出を含む構成の完全一致を確認。ローカルMoodleの管理者アカウントで署名付きLTI起動・教材・Pythonライブラリを確認しました。試験コースは学生非公開のため、今回の起動試験は学生ロールでは実施していません。
