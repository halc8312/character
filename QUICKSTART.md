# GitHub Pages 設定ガイド - クイックスタート

## ⚠️ 重要な結論

### ❌ docs フォルダは必要ありません
### ✅ 現在の設定をそのまま使用してください

---

## 🚀 GitHub Pages を有効化する3ステップ

### ステップ 1: Settings を開く

リポジトリのトップページで **Settings** タブをクリック

```
[Code] [Issues] [Pull requests] [Actions] → [Settings] ← ここをクリック
```

### ステップ 2: Pages 設定を開く

左サイドバーで **Pages** をクリック

```
General
├─ Access
├─ Moderation
├─ Code and automation
│  ├─ Actions
│  ├─ Webhooks
│  └─ Pages  ← ここをクリック
```

### ステップ 3: Source を設定

**Source** セクションで **GitHub Actions** を選択

```
Build and deployment
┌─────────────────────────────────┐
│ Source: [GitHub Actions ▼]     │  ← これを選択
└─────────────────────────────────┘
```

### 完了！ 🎉

以降、main ブランチに push すると自動的に GitHub Pages にデプロイされます。

---

## 📊 デプロイの流れ（自動）

```
キャラクターYAMLを編集
         ↓
   main に push
         ↓
  GitHub Actions 起動
         ↓
  データ自動生成
         ↓
 GitHub Pages デプロイ
         ↓
   サイト公開 ✨
```

**所要時間**: 約 1-3 分

---

## 🔍 デプロイ状況の確認方法

### 1. Actions タブで確認

```
[Actions] タブ → [Deploy to GitHub Pages] ワークフロー
```

- ✅ 緑色のチェックマーク = デプロイ成功
- ❌ 赤色の × マーク = デプロイ失敗（ログを確認）
- 🟡 黄色の点 = デプロイ中

### 2. サイト URL を確認

Settings > Pages で URL が表示されます：

```
Your site is live at https://<username>.github.io/<repository>/
```

---

## 📁 現在のディレクトリ構成

```
character/
├── site/                ← デプロイされるフォルダ
│   ├── index.html
│   ├── character.html
│   ├── graph.html
│   ├── data/           ← 自動生成
│   └── assets/
├── characters/         ← キャラクターデータ（YAML）
├── scripts/
│   └── build_site_data.py
└── .github/workflows/
    └── pages.yml       ← デプロイ設定（すでに完了）

❌ docs/ フォルダは作成しない
```

---

## ❓ よくある質問

### Q: docs フォルダを作る必要はありますか？

**A: いいえ、不要です。**

GitHub Actions を使用しているため、`site/` フォルダから直接デプロイされます。

### Q: site フォルダを docs にリネームする必要は？

**A: いいえ、不要です。**

現在の設定のまま使用してください。変更すると他のファイルも修正が必要になります。

### Q: データファイル（JSON）をコミットする必要は？

**A: いいえ、不要です。**

GitHub Actions が自動的に生成してデプロイします。

### Q: ローカルでサイトを確認するには？

**A: 以下のコマンドを実行します：**

```bash
# データ生成
python scripts/build_site_data.py

# サーバー起動
cd site && python -m http.server 8000

# ブラウザで http://localhost:8000 を開く
```

---

## 📚 詳細情報

より詳しい情報は以下を参照してください：

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 詳細なデプロイメントガイド
- **[README.md](README.md)** - リポジトリ全体のドキュメント
- **GitHub Actions ログ** - [Actions タブ](../../actions)

---

## 🎯 まとめ

1. ✅ **docs フォルダは作成しない**
2. ✅ **Settings > Pages で GitHub Actions を選択**
3. ✅ **main ブランチに push すると自動デプロイ**
4. ✅ **それだけ！**

何も難しいことはありません。すでに設定は完了しています！
