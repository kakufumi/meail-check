from flask import Flask, render_template, request
import MeCab
import math

app = Flask(__name__)

class SimpleClassifier:
    def __init__(self):
        try:
            self.tagger = MeCab.Tagger()
        except:
            import ipadic
            self.tagger = MeCab.Tagger(ipadic.MECAB_ARGS)
        
        self.folders = {"課題": [], "通知": []}
        self.word_probs = {"課題": {}, "通知": {}}
        self.train_initial()

    def parse(self, text):
        words = []
        node = self.tagger.parseToNode(text)
        while node:
            if node.feature.split(',')[0] in ['名詞', '動詞', '形容詞']:
                words.append(node.surface)
            node = node.next
        return words

    def train_initial(self):
        data = [
            ("提出 期限 レポート 課題 締切 添付 提出物 小テスト", "課題"),
            ("お知らせ メンテナンス 完了 ログイン 更新 掲示板 公開 配信 設定 案内 事務局 登録", "通知"),
            ("アルバイト 募集 採用 案内 募集要項 行事 イベント 参加 申込 個人通知 事務課", "通知")
        ]
        for text, cat in data:
            for w in self.parse(text):
                self.word_probs[cat][w] = self.word_probs[cat].get(w, 0) + 1

    # --- ここから差し替える部分 ---
    def classify(self, text):
        words = self.parse(text)
        scores = {"課題": 0, "通知": 0}
        hit_count = {"課題": 0, "通知": 0} 

        for cat in ["課題", "通知"]:
            for w in words:
                val = self.word_probs[cat].get(w, 0)
                scores[cat] += val
                if val > 0:
                    hit_count[cat] += 1
        
        # 判定ロジックの改善：どちらも0点（キーワードなし）なら「通知」へ
        if scores["課題"] == 0 and scores["通知"] == 0:
            category = "通知" 
        elif scores["課題"] > scores["通知"]:
            category = "課題"
        else:
            category = "通知"

        self.folders[category].insert(0, text)
        return category
    # --- ここまで ---

classifier = SimpleClassifier()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mail_text = request.form.get("email_text", "")
        if mail_text:
            classifier.classify(mail_text)
    return render_template("index.html", folders=classifier.folders)

if __name__ == "__main__":
    app.run(debug=True)