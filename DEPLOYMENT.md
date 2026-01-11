# GitHub Pages デプロイメントガイド

## 結論：docs フォルダは不要です

このリポジトリは **GitHub Actions** を使用して自動的に GitHub Pages にデプロイされます。
**docs フォルダを作成する必要はありません。**

## 現在の設定

### ディレクトリ構造

```
character/
├── site/                    # ← GitHub Pages のソースフォルダ
│   ├── index.html
│   ├── character.html
│   ├── graph.html
│   ├── data/
│   │   ├── characters.json  # ← 自動生成
│   │   ├── graph.json       # ← 自動生成
│   │   └── layout.json
│   └── assets/
│       ├── app.css
│       ├── app.js
│       └── graph.js
├── characters/              # ← キャラクターYAMLファイル
├── scripts/
│   └── build_site_data.py   # ← データ生成スクリプト
└── .github/workflows/
    └── pages.yml            # ← 自動デプロイ設定
```

### デプロイの流れ

```
1. キャラクターYAMLを編集
   ↓
2. main ブランチに push
   ↓
3. GitHub Actions が自動実行
   ├─ build_site_data.py を実行
   │  └─ characters/*.yml → site/data/*.json
   ├─ site/ フォルダをアーティファクトとして保存
   └─ GitHub Pages にデプロイ
   ↓
4. サイトが更新される（数分以内）
```

## GitHub Pages の有効化手順

1. リポジトリの **Settings** タブを開く
2. 左サイドバーの **Pages** をクリック
3. **Source** セクションで **GitHub Actions** を選択
4. 保存（自動保存されます）

これだけです！以降、main ブランチに push すると自動的にデプロイされます。

## なぜ docs フォルダが不要なのか？

GitHub Pages には3つのデプロイ方法があります：

| デプロイ方法 | 必要なフォルダ | 特徴 |
|------------|--------------|------|
| **GitHub Actions** ⭐ | `site/` のみ | ・ビルドプロセスの自動化<br>・生成ファイルのみデプロイ<br>・柔軟なカスタマイズ |
| docs フォルダ | `docs/` | ・設定が簡単<br>・ビルドを手動実行が必要<br>・生成ファイルをコミットする必要がある |
| ルートディレクトリ | ルート直下 | ・リポジトリが散らかる<br>・推奨されない |

このリポジトリは **GitHub Actions** 方式を採用しているため：

- ✅ `site/` フォルダに静的ファイルを配置
- ✅ `build_site_data.py` で JSON を自動生成
- ✅ 生成されたファイルのみをデプロイ
- ❌ `docs/` フォルダは不要
- ❌ 手動ビルドは不要
- ❌ 生成ファイルのコミットは不要

## ローカルでの確認方法

GitHub Pages にデプロイする前に、ローカルで動作確認できます：

```bash
# 1. Python 依存関係のインストール
pip install pyyaml

# 2. データ生成
python scripts/build_site_data.py

# 3. ローカルサーバー起動
cd site
python -m http.server 8000

# 4. ブラウザで http://localhost:8000 を開く
```

## トラブルシューティング

### サイトが更新されない

1. **Actions** タブでワークフローの状態を確認
2. エラーがある場合は、ログを確認
3. `build_site_data.py` をローカルで実行してエラーがないか確認

```bash
python scripts/build_site_data.py
```

### 404 エラーが表示される

1. GitHub Pages が有効化されているか確認（Settings > Pages）
2. Source が **GitHub Actions** に設定されているか確認
3. ワークフローが成功しているか確認（Actions タブ）

### キャラクターが表示されない

1. `characters/` フォルダに YAML ファイルが存在するか確認
2. ローカルで `build_site_data.py` を実行してエラーがないか確認
3. `site/data/characters.json` が生成されているか確認

## よくある質問

**Q: docs フォルダを作成する必要がありますか？**

A: いいえ、不要です。GitHub Actions を使用しているため、`site/` フォルダから直接デプロイされます。

**Q: 生成された JSON ファイルをコミットする必要がありますか？**

A: いいえ、不要です。GitHub Actions が自動的に生成してデプロイします。ただし、ローカルで確認する場合は生成する必要があります。

**Q: site/ フォルダの名前を docs/ に変更できますか？**

A: できますが、推奨しません。以下の変更が必要になります：
- `.github/workflows/pages.yml` の `path: 'site'` を `path: 'docs'` に変更
- `scripts/build_site_data.py` の出力パスを変更
- README の記述を更新

現在の `site/` フォルダ名を維持することを推奨します。

**Q: なぜ GitHub Actions を使うのですか？**

A: 以下の理由から推奨されます：
- ビルドプロセスの自動化
- 生成ファイルをコミットしなくて良い
- リポジトリがきれいに保たれる
- 柔軟なカスタマイズが可能

## 参考リンク

- [GitHub Pages 公式ドキュメント](https://docs.github.com/ja/pages)
- [GitHub Actions でのデプロイ](https://docs.github.com/ja/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
