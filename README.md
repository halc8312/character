# キャラクターデータベース

AIによるキャラクター演技のために設計された、Git管理型のストーリーキャラクターデータベースです。このリポジトリは、AIシステムがキャラクターを「演じる」ために読み取れる、フィクションキャラクターを定義するための構造化テンプレートを提供します。

> 🚀 **GitHub Pages セットアップ**: [QUICKSTART.md](QUICKSTART.md) で3ステップで完了！（docs フォルダは不要です）

## 概要

このリポジトリは、キャラクター定義の**唯一の信頼できる情報源**として機能し、以下を提供します：
- 全キャラクターに対する一貫したスキーマ
- 機械可読なYAML形式
- AI演技ガイドラインの組み込み
- データ整合性のためのCI検証

## リポジトリ構成

```
.
├── README.md                          # このファイル
├── schemas/
│   ├── character.schema.json          # キャラクター検証用JSONスキーマ
│   ├── location.schema.json           # ロケーション検証用JSONスキーマ
│   ├── map.schema.json                # 地図検証用JSONスキーマ
│   ├── links.schema.json              # キャラ⇄ロケーション紐付けスキーマ
│   └── vocab.yml                      # 制御語彙（タグ、関係性タイプ、ロケーションタイプ）
├── characters/
│   └── _TEMPLATE.character.yml        # 新規キャラクター用テンプレート
├── locations/
│   └── _TEMPLATE.location.yml         # 新規ロケーション用テンプレート
├── maps/
│   └── _TEMPLATE.map.yml              # 新規地図用テンプレート
├── links/
│   └── character_locations.yml        # キャラクター⇄ロケーション紐付け
├── relations/
│   └── graph.yml                      # 関係性グラフ（オプションの集中管理ビュー）
├── prompts/
│   ├── system_prompt.md               # AIシステムプロンプト
│   └── character_prompt_template.md   # キャラクター固有プロンプトテンプレート
├── scripts/
│   ├── validate_characters.py         # キャラクター検証スクリプト
│   ├── validate_locations.py          # ロケーション検証スクリプト
│   └── build_site_data.py             # サイトデータ生成スクリプト
├── site/                              # GitHub Pages 用静的サイト
│   ├── index.html                     # キャラクター一覧
│   ├── character.html                 # キャラクター詳細
│   ├── graph.html                     # 相関図
│   ├── locations.html                 # ロケーション一覧
│   ├── location.html                  # ロケーション詳細
│   ├── map.html                       # 地図ビュー
│   ├── data/                          # 生成されるJSONデータ
│   └── assets/                        # CSS/JavaScript
└── .github/
    ├── workflows/
    │   ├── validate.yml               # CI検証ワークフロー
    │   └── pages.yml                  # GitHub Pages デプロイ
    ├── ISSUE_TEMPLATE/
    │   └── new_character.yml          # 新規キャラクター提案テンプレート
    └── pull_request_template.md       # PRチェックリスト
```

## キャラクターID命名規則

キャラクターIDは以下の条件を満たす必要があります：
- **小文字**、**数字**、**アンダースコア**のみ使用
- パターン `^[a-z0-9_]+$` に一致
- ファイル名と完全に一致（例：`john_smith.yml` → `id: john_smith`）

**例：**
- ✅ `alice_wonder`, `hero_01`, `dark_lord`
- ❌ `Alice-Wonder`, `Hero 01`, `DarkLord`

## タグシステム

タグは `prefix/value` 形式でキャラクターを分類します：

```yaml
tags:
  - role/protagonist
  - trait/brave
  - species/human
  - status/alive
```

### 有効なタグプレフィックス

| プレフィックス | 説明 | 例 |
|--------|-------------|----------|
| `role` | ストーリーでの役割 | `protagonist`, `antagonist`, `supporting` |
| `trait` | 性格特性 | `brave`, `cunning`, `kind` |
| `species` | 種族 | `human`, `elf`, `android` |
| `origin` | 出身地・起源 | `kingdom_a`, `earth` |
| `faction` | 所属組織 | `rebels`, `empire` |
| `status` | 現在の状態 | `alive`, `deceased`, `missing` |
| `archetype` | キャラクター原型 | `hero`, `mentor`, `trickster` |
| `power` | 能力・魔法タイプ | `fire_magic`, `telepathy` |
| `era` | 時代 | `medieval`, `future` |
| `genre` | ジャンルタグ | `fantasy`, `scifi`, `modern` |

### 新規タグプレフィックスの追加

新しいプレフィックスを追加するには：
1. `schemas/vocab.yml` を編集
2. `tag_prefixes` リストにプレフィックスを追加
3. 必要に応じて `recommended_tags` に推奨タグを追加
4. PRを提出

**検証動作：** 無効なプレフィックスを持つタグは検証エラーを引き起こします。

## 関係性システム

関係性は各キャラクターの `relationships` 配列で定義されます：

```yaml
relationships:
  - target_id: alice_wonder    # 既存のキャラクターIDである必要があります
    type: friend               # vocab.yml に存在する必要があります
    description: "幼なじみ"
    intensity: 4               # -5（敵対的）〜 5（親密）
    mutual: true
```

### 有効な関係性タイプ

| カテゴリ | タイプ |
|----------|-------|
| 家族 | `parent`, `child`, `sibling`, `spouse`, `relative` |
| 社会的 | `friend`, `rival`, `enemy`, `ally`, `mentor`, `student`, `colleague`, `acquaintance` |
| 恋愛 | `lover`, `ex_lover`, `crush` |
| 職業的 | `employer`, `employee`, `partner`, `subordinate`, `superior` |
| その他 | `unknown`, `other` |

### 新規関係性タイプの追加

1. `schemas/vocab.yml` を編集
2. `relationship_types` リストにタイプを追加
3. PRを提出

### Graph.yml（オプション）

`relations/graph.yml` は関係性のオプションの集中管理ビューを提供します。信頼できる情報源は各キャラクターの `relationships` 配列です。`graph.yml` は以下の用途に使用できます：
- 可視化ツール
- クロスリファレンス
- ネットワーク分析

## 新規キャラクターの追加

### ステップ1：Issueを作成（オプション）
[新規キャラクターテンプレート](.github/ISSUE_TEMPLATE/new_character.yml)を使用してキャラクターを提案します。

### ステップ2：キャラクターファイルの作成
1. `characters/_TEMPLATE.character.yml` を `characters/<your_id>.yml` にコピー
2. プレースホルダーの値を実際のキャラクターデータに置き換え
3. `id` がファイル名と一致していることを確認

### ステップ3：ローカルで検証
```bash
# 依存関係のインストール
pip install pyyaml jsonschema

# 検証の実行
python scripts/validate_characters.py
```

### ステップ4：PRを提出
1. ブランチを作成して変更をコミット
2. プルリクエストを開く
3. CIが自動的に検証を実行
4. 検証が失敗した場合は問題を修正

## AIでの使用方法

### ステップ1：システムプロンプトの設定

`prompts/system_prompt.md` の内容をAIのシステムプロンプトとしてコピーします。これにより以下が確立されます：
- キャラクター演技ガイドライン
- 境界ルール
- メタコメンタリーの制限
- 安全ガイドライン

### ステップ2：キャラクタープロンプトの作成

1. `prompts/character_prompt_template.md` をコピー
2. `{{CHARACTER_YAML}}` をキャラクターのYAMLファイルの全内容に置き換え
3. これをAIのキャラクター固有プロンプトとして使用

### 設定例

```
[システムプロンプト]
<prompts/system_prompt.md の内容>

[ユーザー/キャラクタープロンプト]
<{{CHARACTER_YAML}} を置き換えた prompts/character_prompt_template.md の内容>

[ユーザーメッセージ]
こんにちは！今日の調子はどうですか？
```

AIは、定義された声、性格、知識を使用してキャラクターとして応答します。

## CI検証

GitHub Actionsワークフローは、すべてのPRとメインブランチへのプッシュで検証を実行します。

### 検証内容

| チェック | 説明 |
|-------|-------------|
| **スキーマ検証** | 全必須キーの存在、正しい型 |
| **ID/ファイル名の一致** | キャラクターの `id` がファイル名と一致 |
| **関係性ターゲット** | 全 `target_id` 値が既存のキャラクターを参照 |
| **関係性タイプ** | 全 `type` 値が `vocab.yml` に存在 |
| **タグプレフィックス** | 全タグプレフィックスが `vocab.yml` に存在（エラー） |
| **日付形式** | `meta.created` と `meta.updated` が有効な YYYY-MM-DD |
| **Graph.yml** | 入力されている場合、有効なキャラクターIDとタイプを参照 |

### ローカルでの検証実行

```bash
pip install pyyaml jsonschema
python scripts/validate_characters.py
```

## キャラクターファイルリファレンス

### 必須キー

すべてのキャラクターファイルには以下を含める必要があります：

| キー | 説明 |
|-----|-------------|
| `version` | スキーマバージョン（例：「1.0」） |
| `id` | 一意の識別子 |
| `profile` | 名前、年齢、性別、役割など |
| `tags` | 分類タグ |
| `appearance` | 外見の説明 |
| `personality` | 性格特性、長所、短所 |
| `background` | 経歴と背景 |
| `goals` | 目的と願望 |
| `motivations` | キャラクターを動かすもの |
| `conflicts` | 内的・外的な葛藤 |
| `abilities` | スキルと能力 |
| `behavior` | 話し方、癖 |
| `secrets` | 隠された情報（空の `[]` も可） |
| `relationships` | 他のキャラクターとの関係（空の `[]` も可） |
| `story` | 物語での役割 |
| `ai_portrayal` | AIのためのガイドラインと境界 |
| `meta` | 作成日/更新日、作者 |

完全な構造と例については `characters/_TEMPLATE.character.yml` を参照してください。

## ロケーションデータベース

キャラクターが住む街や場所を管理するためのシステムです。階層構造で場所を定義し、キャラクターとの関連付けが可能です。

### ディレクトリ構成

- `locations/` - 場所の定義（SSOT）
- `maps/` - 地図ビューの定義
- `links/` - キャラクター⇄ロケーションの紐付け

### ロケーションID命名規則

ロケーションIDは以下の条件を満たす必要があります：
- **小文字**、**数字**、**アンダースコア**のみ使用
- パターン `^[a-z0-9_]+$` に一致
- ファイル名と一致（例：`nishigaoka_city.location.yml` → `id: nishigaoka_city`）
- 推奨形式: `親ID_場所名`（例：`nishigaoka_downtown`, `downtown_central_plaza`）

### ロケーションタイプ

`vocab.yml` で定義されている有効なタイプ：

| カテゴリ | タイプ |
|----------|--------|
| 大規模 | `world`, `continent`, `country`, `region`, `city` |
| 中規模 | `district`, `neighborhood`, `street` |
| 施設・建物 | `building`, `house`, `shop`, `school`, `temple`, `guild`, `office`, `hospital`, `station` |
| 建物内部 | `room`, `floor` |
| ランドマーク・自然 | `landmark`, `park`, `plaza`, `forest`, `mountain`, `river`, `lake` |

### ロケーションYAMLリファレンス

```yaml
version: "1.0"
id: nishigaoka_central_plaza

profile:
  name: "中央広場"
  short: "広場"
  type: landmark               # vocab.yml の location_types から
  parent_id: nishigaoka_downtown  # 親ロケーション（階層構造）
  description: "噴水と露店が並ぶ待ち合わせの定番。"

tags:
  - location/landmark
  - district/downtown

lore:
  history: "50年前に整備された市民の憩いの場"
  rumors:
    - "満月の夜、噴水が青く光るという噂"
  rules:
    - "大声での演説は禁止"
  notable_features:
    - "大噴水"
    - "露店街"

meta:
  created: "2026-01-12"
  updated: "2026-01-12"
  author: "your_name"
```

### 地図（Map）YAMLリファレンス

地図は「特定の範囲のロケーションを可視化するビュー」です。

```yaml
version: "1.0"
id: nishigaoka_city

profile:
  name: "西ヶ丘市 全体図"
  description: "主要地区とランドマークの俯瞰図"

root_location_id: nishigaoka_city    # この配下を地図に表示
include:
  depth: 3                           # 何階層下まで含めるか
  types:                             # 表示対象タイプ（空 = 全て）
    - district
    - landmark
    - building

display:
  layout: auto                       # auto または saved
  show_labels: true

meta:
  created: "2026-01-12"
  updated: "2026-01-12"
  author: "your_name"
```

### キャラクター⇄ロケーション紐付け

既存のキャラクターYAMLを編集せずに、`links/character_locations.yml` で紐付けを管理します。

```yaml
version: "1.0"
links:
  - character_id: haruto_tanaka
    kind: home                       # vocab.yml の link_kinds から
    location_id: nishigaoka_residential
    note: "実家がある住宅街"
  - character_id: haruto_tanaka
    kind: school
    location_id: nishigaoka_high_school
  - character_id: haruto_tanaka
    kind: hangout
    location_id: nishigaoka_central_plaza
    intensity: 4                     # 0-5: 訪問頻度
```

### 有効なリンクタイプ（link_kinds）

| タイプ | 説明 |
|--------|------|
| `home` | 自宅・住居 |
| `birthplace` | 出生地 |
| `current` | 現在地 |
| `workplace` | 勤務先 |
| `school` | 通学先 |
| `hangout` | よく訪れる場所 |
| `hideout` | 隠れ家 |
| `owned` | 所有物件 |
| `frequented` | 頻繁に訪れる |
| `avoided` | 避けている場所 |
| `memorable` | 思い出の場所 |

### 新規ロケーションの追加手順

1. `locations/_TEMPLATE.location.yml` を `locations/<id>.location.yml` にコピー
2. プレースホルダーを実際のデータに置き換え
3. 必要に応じて `links/character_locations.yml` にキャラクターとの紐付けを追加
4. ローカルで検証: `python scripts/validate_locations.py`
5. PRを提出

### 地図の作成手順

1. `maps/_TEMPLATE.map.yml` を `maps/<id>.map.yml` にコピー
2. `root_location_id` に表示したいロケーションのIDを指定
3. `include.depth` と `include.types` で表示範囲を調整
4. PRを提出
5. デプロイ後、`map.html?map=<id>` で地図を閲覧
6. 「レイアウトを書き出し」で位置を保存可能

## 貢献方法

1. **キャラクター**：Issueテンプレートを使用して提案し、PRを提出
2. **スキーマ/語彙の変更**：まずIssueで議論
3. **すべてのPR**：CI検証に合格する必要があります

## GitHub Pages（Webビューア）

このリポジトリは GitHub Pages を使用してキャラクター一覧・詳細・相関図・ロケーション情報を Web 上で閲覧できます。

> 📘 **詳細なデプロイメントガイド**: [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください

### URL構造

- `/index.html` - キャラクター一覧（検索・タグ絞り込み）
- `/character.html?id=<id>` - キャラクター詳細ページ
- `/graph.html` - 相関図（インタラクティブ）
- `/graph.html?focus=<id>` - 特定キャラクターにフォーカスした相関図
- `/locations.html` - ロケーション一覧（階層ツリー表示）
- `/location.html?id=<id>` - ロケーション詳細ページ
- `/map.html?map=<id>` - 地図ビュー（Cytoscapeによる可視化）

### GitHub Pages の有効化

**重要：docsフォルダは必要ありません！**

このリポジトリは GitHub Actions を使用して自動デプロイされるため、`docs` フォルダを作成する必要はありません。

#### セットアップ手順

1. リポジトリの **Settings** > **Pages** を開く
2. **Source** を **GitHub Actions** に設定
3. main ブランチに push すると自動的にデプロイされます

#### GitHub Pages デプロイ方法の比較

| 方法 | 必要なフォルダ | メリット | デメリット |
|------|---------------|---------|----------|
| **GitHub Actions** (推奨・現在の設定) | `site/` のみ | ・ビルドプロセスの自動化<br>・柔軟なカスタマイズ<br>・生成されたファイルのみデプロイ | ・Actions の設定が必要 |
| docs フォルダ | `docs/` | ・設定が簡単<br>・Actions 不要 | ・ビルドを手動実行<br>・生成ファイルをコミット |
| ルートディレクトリ | ルート直下 | ・設定が簡単 | ・リポジトリが散らかる |

**現在の設定（GitHub Actions）を使用することを強く推奨します。**

### 生成の流れ

```
characters/*.yml     ─┐
locations/*.yml      ─┼→  scripts/build_site_data.py  →  site/data/*.json  →  GitHub Pages
maps/*.yml           ─┤
links/*.yml          ─┘
```

1. YAML ファイル（キャラクター、ロケーション、地図、紐付け）を追加・編集
2. main ブランチに push
3. GitHub Actions (`pages.yml`) が自動実行：
   - `build_site_data.py` が YAML から JSON を生成
   - `site/` ディレクトリを GitHub Pages にデプロイ

### 生成されるファイル

| ファイル | 内容 |
|----------|------|
| `characters.json` | キャラクター一覧データ |
| `graph.json` | キャラクター相関図データ |
| `layout.json` | 相関図レイアウト |
| `locations.json` | ロケーション一覧データ |
| `maps.json` | 地図定義一覧 |
| `character_locations.json` | キャラ⇄ロケーション紐付け |
| `location_graph_<map_id>.json` | 地図用グラフデータ |
| `location_layout_<map_id>.json` | 地図レイアウト |

### ローカルでの確認

```bash
# 依存関係のインストール
pip install pyyaml

# データ生成
python scripts/build_site_data.py

# ローカルサーバー起動（例）
cd site && python -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

### レイアウト永続化（相関図）

相関図のノード位置はカスタマイズして保存できます：

1. `graph.html` を開く
2. ノードをドラッグして位置を調整
3. 「レイアウトを書き出し」ボタンをクリック
4. ダウンロードした `layout.json` を `site/data/layout.json` として上書きコミット
5. 次回デプロイ以降、ノード位置が保持されます

**新規ノードの扱い：**
- `layout.json` に座標がないノードは「新規ノード」として緑色で表示
- 新規ノードは既存ノードの近くに自動配置され、レイアウトを馴染ませます
- 「自動整列（全体）」ボタンで全ノードを再配置することもできます

### データ生成時の検証

`build_site_data.py` は以下をチェックします：

| チェック | 動作 |
|---------|------|
| edges の source/target が存在しない | **エラー**（ビルド停止） |
| edges.type が vocab.yml にない | **エラー**（ビルド停止） |
| tags の prefix が vocab.yml にない | **警告**（ビルド続行） |

### ディレクトリ構成（site/）

```
site/
├── index.html            # キャラクター一覧
├── character.html        # キャラクター詳細
├── graph.html            # 相関図
├── data/
│   ├── characters.json   # 生成物
│   ├── graph.json        # 生成物
│   └── layout.json       # レイアウト永続化用
└── assets/
    ├── app.css           # スタイル
    ├── app.js            # 共通JavaScript
    └── graph.js          # Cytoscape.js 連携
```

## よくある質問（FAQ）

### Q: GitHub Pages で公開するには docs フォルダが必要ですか？

**A: いいえ、必要ありません。**

このリポジトリは GitHub Actions を使用して自動的にデプロイされるため、`docs` フォルダを作成する必要はありません。

**現在の設定：**
- `site/` フォルダに HTML/CSS/JavaScript ファイルを配置
- `.github/workflows/pages.yml` が自動的にビルドとデプロイを実行
- `docs` フォルダの作成や手動コピーは不要

**有効化方法：**
1. リポジトリの **Settings** > **Pages** を開く
2. **Source** を **GitHub Actions** に設定
3. main ブランチに push すると自動的にデプロイされます

詳細は「[GitHub Pages（Webビューア）](#github-pageswebビューア)」セクションを参照してください。

### Q: ローカルでサイトを確認するには？

**A:** 以下のコマンドを実行します：

```bash
# データ生成
python scripts/build_site_data.py

# ローカルサーバー起動
cd site && python -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

### Q: キャラクターを追加したら自動的にサイトに反映されますか？

**A:** はい。main ブランチに push すると、GitHub Actions が自動的に：
1. `build_site_data.py` を実行してデータを生成
2. `site/` フォルダを GitHub Pages にデプロイ

変更は数分以内にサイトに反映されます。

## ライセンス

[ここにライセンスを追加]