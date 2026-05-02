# LDX hub for Dify

> Dify ワークフローのためのドキュメント AI — 統合ゲートウェイ経由で、主要 LLM を使った構造化データ抽出と翻訳品質改善。

![Hero: Dify ワークフロー上の LDX hub StructFlow ノード](https://raw.githubusercontent.com/ldxhub-io/dify-nodes-ldxhub/main/_assets/screenshots/hero.png)

> ✅ **無料で試せる** — 月25,000クレジット、クレジットカード不要
> ✅ **キー1本で全モデル** — OpenAI、Anthropic、Google、AWS、Azure、xAI
> ✅ **30秒で登録完了** — GitHub・Google・メールでサインアップ可、登録直後に API キー表示

---

## このプラグインでできること

LDX hub は [LDX Lab](https://ldxlab.io) が提供するドキュメント AI ゲートウェイです。本プラグインはその中から 2 つの機能を Dify に持ち込みます。

- **StructFlow** — 主要 LLM を使って非構造テキストから構造化 JSON を抽出。本プラグインの主役機能。
- **RefineLoop** — XLIFF 翻訳ファイルに StructFlow の反復改善エンジンを適用。同じエンジンを翻訳品質レビュー向けに特化。

両ツールとも OpenAI、Microsoft Azure OpenAI、Google、Anthropic、Amazon Bedrock、xAI を、単一の API と単一の課金体系で利用できます。API キーは 1 本だけで OK です。

## StructFlow: 構造化データ抽出

StructFlow は非構造テキストを構造化 JSON に変換します。システムプロンプトと出力例で抽出スキーマを定義し、JSONL の入力レコード群を選んだモデルで処理します。

### 使い方

1. JSONL ファイル（1 行 1 レコード）をアップロード
2. システムプロンプトと出力例で抽出スキーマを定義
3. AI モデルを選択
4. レコードごとに構造化 JSON が並んだ JSONL ファイルを取得

![StructFlow ノードの設定画面](https://raw.githubusercontent.com/ldxhub-io/dify-nodes-ldxhub/main/_assets/screenshots/structflow_node.png)

### ユースケース

特許、医療、金融、法務、カスタマーサポート、人事、不動産、EC の 8 業界にわたる実例を整理しています。

プロンプトとサンプル入出力を含む全リストは [examples/USE_CASES.md](https://github.com/ldxhub-io/dify-nodes-ldxhub/blob/main/examples/USE_CASES.md) を参照してください。

### 簡単な例: 医療カルテ

**入力**（JSONL ファイルの 1 レコード）:

```json
{"note":"30代男性。主訴：発熱、咽頭痛、嚥下困難。現病歴：3日前から38度台の発熱があり、市販の解熱鎮痛剤を内服するも改善せず。昨日から唾液を飲み込むのも辛いほどの強い咽頭痛が出現したため当院を受診。身体所見：体温38.5度、血圧120/80、口蓋扁桃に著明な発赤と白苔の付着を認める。前頸部リンパ節の圧痛伴う腫脹あり。迅速検査：インフルエンザ抗原陰性、新型コロナウイルス抗原陰性、A群β溶血性連鎖球菌（溶連菌）迅速抗原検査陽性。アセスメント：急性化膿性扁桃炎（溶連菌感染症）。プラン：ペニシリン系抗菌薬（アモキシシリンカプセル250mg 1日3回 10日分）を処方。疼痛時頓服としてロキソプロフェンナトリウム錠60mgを処方。"}
```

**出力**（StructFlow による実機の抽出結果）:

```json
{
  "symptoms": [
    "発熱",
    "38度台の発熱",
    "咽頭痛",
    "嚥下困難",
    "唾液を飲み込むのも辛いほどの強い咽頭痛",
    "口蓋扁桃の著明な発赤",
    "口蓋扁桃の白苔の付着",
    "前頸部リンパ節の圧痛伴う腫脹"
  ],
  "diagnosis": "急性化膿性扁桃炎（溶連菌感染症）",
  "treatment": [
    "アモキシシリンカプセル250mg 1日3回 10日分",
    "ロキソプロフェンナトリウム錠60mg"
  ]
}
```

自由記述の臨床ノートが、構造化された検索可能なデータに変わります。身体所見（"口蓋扁桃の著明な発赤"、"前頸部リンパ節の圧痛伴う腫脹" など 8 項目）、診断アセスメント、用法用量を含む処方内容まで、それぞれの文脈を保ったまま抽出されています。

## RefineLoop: XLIFF 翻訳品質改善

RefineLoop は StructFlow の反復改善エンジンを XLIFF ファイル向けに特化したものです。各セグメントが複数のリビジョンを経て、AI が訳文を批評・改善し、構造化されたリビジョンノートを残します。

### 使い方

1. CAT ツールから出力した XLIFF ファイルをアップロード
2. AI モデルを選択
3. 複数のリビジョンを通じて訳文が反復的にレビュー・改善される
4. 改善された XLIFF を取得し、CAT ツールに戻す

![RefineLoop ノードの設定画面](https://raw.githubusercontent.com/ldxhub-io/dify-nodes-ldxhub/main/_assets/screenshots/refineloop_node.png)

### スケールに対応した設計

RefineLoop は StructFlow と同じ反復改善エンジンの上に作られています。XLIFF を渡すと、その中の全 `<file>` 要素を横断して `trans-unit` セグメントをソース/ターゲット言語ペアでグルーピングし、言語ペアごとに 1 バッチでエンジンに投入します。

つまりエンジン呼び出し回数は `(言語ペア数 × リビジョン数)` で抑えられ、`<file>` 要素の数には依存しません。前回のリビジョンと同じ訳文に収束したセグメントは次のリビジョンから除外されるので、実際の処理回数は最悪値より少なくなります。

XLIFF のタグ整合性（`<ph>`, `<bpt>`, `<ept>`, `<it>` など）は各リビジョン後に検証されます。リビジョンがタグ構造を壊した場合、そのリビジョンは失敗扱いになり、次のリビジョンで再挑戦します。最終的な XLIFF は CAT ツールにそのまま取り込める状態を保ちます。

**実測ベンチマーク:** BERT 論文の翻訳（原文約 65,000 文字、XLIFF タグ込みで約 145,000 文字）を Gemini 3 Flash Preview と `max_revisions=6` で改善した結果、Dify Cloud 上でアップロード・ダウンロードを含めて **3 分 46 秒** で完走しました。精度の高いモデルを使えば収束が早く、より短時間で完了します。

![RefineLoop が 3 m 45.912 s で完走したテスト実行のトレース](https://raw.githubusercontent.com/ldxhub-io/dify-nodes-ldxhub/main/_assets/screenshots/run.png)

### 出力モード

- `full` — 全リビジョン + ノート（レビュー・監査向け）
- `translations` — 全リビジョンの訳文のみ、ノートなし
- `none` — 最終結果のみ（本番投入向けのクリーンな出力）

## セットアップ

### 1. API キーを取得

[https://gw.portal.ldxhub.io](https://gw.portal.ldxhub.io) でサインアップして API キーを取得します（無料、クレジットカード不要、GitHub・Google・メールで OK、登録直後にキー表示）。

### 2. Dify で認証情報を設定

LDX hub プラグインの認証設定画面を開いて、以下を入力します。

- **Base URL**: `https://gw.ldxhub.io`（デフォルト）
- **API キー**: ステップ 1 で取得したキーを貼り付け

![API キー認証設定画面](https://raw.githubusercontent.com/ldxhub-io/dify-nodes-ldxhub/main/_assets/screenshots/credential.png)

API キーは Dify によって暗号化（PKCS1_OAEP）されてワークスペース内に保存されます。

## サポートしている AI モデル

両ツールとも以下のプロバイダーのモデルに対応しています。

- OpenAI GPT シリーズ（フラッグシップ／mini 系、Azure 経由含む）
- Google Gemini シリーズ（Pro と Flash）
- Anthropic Claude シリーズ（Opus と Sonnet）
- Amazon Nova（Bedrock 経由）
- xAI Grok

モデルラインナップは LDX hub 側で動的に管理されていますが、プラグイン側にはビルド時点のリストを埋め込んでいます。新しいモデルを Dify ワークフローで使えるようにするには、プラグインのバージョンアップデートが必要です。

## 長時間ジョブ

プラグインは LDX hub の API をポーリングしてジョブの完了を待ちます。通常のワークロードならこれで十分です（前述の BERT 論文のベンチマークも 4 分以内で完走しています）。

例外的に長時間かかるジョブで Dify の実行タイムアウトを超える可能性がある場合のために、`webhook_url` パラメータをオプションで用意しています。プラグインがこの URL を LDX hub に渡し、サーバ側がジョブ完了時に指定 URL へ通知します。

> 注: サーバ側の Webhook 配信機能は現在実装準備中です。同期ポーリングは通常通り動作します。

## プライバシーとセキュリティ

このプラグインは LDX hub サーバと、選択したモデルに対応する AI プロバイダーに対してデータを送信します。API キーは Dify によって暗号化（PKCS1_OAEP）されます。プラグイン自体はデータを保存せず、テレメトリも送信しません。

詳細は [PRIVACY.md](https://github.com/ldxhub-io/dify-nodes-ldxhub/blob/main/PRIVACY.md) を参照してください。

## LDX hub について

LDX hub は [LDX Lab](https://ldxlab.io) が開発しています。複数の LLM プロバイダーにまたがるドキュメント AI 処理を、ひとつの API、ひとつのキー、ひとつの課金体系で提供します。

API 自体に関する質問は [https://ldxlab.io](https://ldxlab.io) を参照してください。

この Dify プラグインに関する質問やバグレポートは [GitHub Issues](https://github.com/ldxhub-io/dify-nodes-ldxhub/issues) からお願いします。
