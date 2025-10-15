import streamlit as st
import pandas as pd

# --- 診断結果の定義 ---
RESULTS_MAP = {
    1: "管理職",
    2: "特別養護老人ホーム",
    3: "有料老人ホーム",
    4: "介護老人保健施設",
    5: "訪問介護",
    6: "デイサービス",
    7: "グループホーム",
    8: "居宅（在宅）",
    9: "施設のケアマネジャー",
    10: "サービス付き高齢者向け住宅や小規模多機能型居宅介護など"
}

# --- スコアリングロジック ---
# 最終合意の対応表に基づき、選択肢('A'または'B')と加算される結果IDのリストを定義
SCORING_RULES = {
    'Q1': {'A': [1, 9], 'B': [2, 3, 4, 5, 6, 7, 10]},
    'Q2': {'A': [1], 'B': [2, 4, 5, 8, 9]},
    'Q3': {'A': [1], 'B': [2, 3, 4, 6, 7]},
    'Q4': {'A': [8, 9], 'B': [2, 3, 4, 7]},
    'Q5': {'A': [7], 'B': [2, 3]},
    'Q6': {'A': [5], 'B': [2, 3, 4, 6, 7, 10]},
    'Q7': {'A': [4], 'B': [6]},
    'Q8': {'A': [2, 3, 4], 'B': [10]},
    'Q9': {'A': [2, 3, 4, 5, 6, 7, 8, 9, 10], 'B': [1]}, 
    'Q10': {'A': [1], 'B': [2, 3, 4, 5, 6, 7, 8, 9, 10]}
}

# --- 診断結果メッセージ ---
MESSAGES = {
    "管理職": "🎉 天性のマネジメント気質！あなたは、**感情に左右されず冷静で、指示を素直に実行できるプロの裏方**です。現場の主役になるより、組織の平和と安定を最優先できます。全体のバランスを取り、大きな組織を円滑に動かす仕事にこそ、あなたの才能が輝きます！",
    "特別養護老人ホーム": "💖 究極の「終活」サポーター！あなたは利用者さんの**最後の暮らし**まで、とことん深く関わりたい情熱家！重度の身体介護や看取りも含め、24時間365日、生活すべてを支えるのがミッション。**濃い人間関係とチームの絆**の中で、最高のやりがいを感じられます！",
    "有料老人ホーム": "✨ サービス業のプロ！あなたは**快適さやホテルのような質**を追求するのが得意。施設での長期生活をトータルでコーディネートし、利用者さんの満足度を上げたい欲求が強いです。大規模で洗練された環境で、**手厚く、行き届いた**ケアを提供するのが天職です！",
    "介護老人保健施設": "💪 リハビリの鬼！**在宅復帰**という目標に向けて、利用者をスパルタ...ではなく（笑）、集中的にサポートするのがあなた！医療とリハビリが一体となった環境で、**回復プロセス**を見るのが大好き。利用者さんの**卒業**を心から喜べる、前向きな人に向いています！",
    "訪問介護": "🚗 孤高のケア職人！あなたは**一匹狼**タイプ！誰にも邪魔されず、利用者さんと**一対一**でじっくり向き合いたい。利用者さんの自宅というプライベートな空間で、細かなニーズに対応する**自律性や責任感**がピカイチ。フットワーク軽く働きたい人に最適です！",
    "デイサービス": "🎨 ムードメーカー！あなたは利用者さんを**笑顔にするのが得意なエンターテイナー！**日中の限られた時間で、レクリエーションやイベントを楽しみ、活気ある時間を作るのが使命です。夜勤もないため、**仕事とプライベートのメリハリ**をつけたい人にぴったりです！",
    "グループホーム": "🏡 家庭的な癒やし担当！あなたは**大規模な場所が苦手なアットホーム志向**。少人数で家族のような関係性を築き、特に**認知症の方**に対して愛情深く寄り添うことができます。ゆっくりとした時間の中で、暮らしの質を上げたいと考える方に天職です。",
    "居宅（在宅）": "🗺️ 地域の司令塔！あなたは**調整役と計画作りが得意な戦略家**！現場で働くよりも、利用者さんの自宅生活に必要な**パズルのピース**（様々なサービス）を組み合わせて、最高の在宅プランを作ることに情熱を燃やします。全体を見て動かしたいあなたに最適です！",
    "施設のケアマネジャー": "📝 施設内の調整マニア！あなたは現場の経験と**計画作成**のスキルを掛け合わせたいタイプ。施設内で他の職員と連携を取りながら、利用者さん全員のケアプランを完璧に管理したい。**全体を統括するポジション**で、あなたの緻密さが役立ちます！",
    "サービス付き高齢者向け住宅など": "🌐 ハイブリッドな働き方！あなたは**一つの枠に収まりたくない自由人！**入居サービスも通所サービスも提供する複合的な環境で、幅広いスキルを身につけたい。地域との関わりも深く、**多様な働き方**や新しい介護サービスにチャレンジしたい方にぴったりです！"
}

# --- スコア計算関数 ---
def calculate_score(answers):
    scores = {id: 0 for id in RESULTS_MAP.keys()}
    
    for q_name, answer in answers.items():
        if q_name in SCORING_RULES and answer in SCORING_RULES[q_name]:
            for result_id in SCORING_RULES[q_name][answer]:
                scores[result_id] += 1
    
    # スコアを降順にソートし、結果名とスコアをペアにする
    ranked_results = sorted(
        [(scores[id], RESULTS_MAP[id]) for id in scores.keys()],
        key=lambda x: x[0],
        reverse=True
    )
    return ranked_results

# --- Streamlit UIの構築 ---
st.set_page_config(layout="wide") 
st.title("👨‍⚕️ 介護職の適職診断（全10問）")
st.markdown("ご自身の考えに最も近いものを選んでください。")
st.divider()

if 'answers' not in st.session_state:
    st.session_state.answers = {}

# 質問の表示
with st.form(key='aptitude_form'):
    for q_code, q_title, choice_a, choice_b in QUESTIONS:
        st.subheader(f"{q_code}. {q_title}")
        
        options_text = [choice_a, choice_b]
        options_code = ["A", "B"]
        
        # Streamlitのラジオボタン
        option = st.radio(
            label="選択してください",
            options=options_code,
            format_func=lambda x: options_text[options_code.index(x)],
            key=q_code,
            index=None, 
            label_visibility='collapsed' 
        )
        st.session_state.answers[q_code] = option

    st.markdown("---")
    submitted = st.form_submit_button("診断結果を見る 🚀")

# 結果の表示ロジック
if submitted:
    # 全ての質問に回答しているかチェック
    if any(ans is None for ans in st.session_state.answers.values()):
        st.error("全ての質問に回答してください。")
    else:
        # スコア計算
        ranked_results = calculate_score(st.session_state.answers)
        
        main_score = ranked_results[0][0]
        
        # 第一適職（同点含む）を抽出
        main_results = [name for score, name in ranked_results if score == main_score]
        
        # 2位以下の結果を抽出（スコアがメインより低いもののみ）
        other_results = [(score, name) for score, name in ranked_results if score < main_score]
        
        # --- UI表示 ---
        st.balloons()
        st.success("## 診断完了！あなたの適職タイプは...")
        
        # -------------------
        # 第一適職の表示 (スコア表示なし)
        # -------------------
        main_results_text = '、'.join([f"【{name}】" for name in main_results])
        st.markdown(f"**🥇 第一適職**: **{main_results_text}**")

        
        # -------------------
        # 詳細な診断テキストの表示
        # -------------------
        
        if len(main_results) == 1:
            main_job = main_results[0]
            st.warning(MESSAGES.get(main_job, "最適な結果が見つかりました！"))
        else:
            st.warning(f"あなたは複数の職種（{main_results_text}）に、同じくらい高い適性を持っています！どの分野でも力を発揮できる万能タイプです。")

        st.divider()
        st.subheader("💡 他の適職候補（次点から最大3つの順位）")
        
        # -------------------
        # 他の適職候補の表示ロジック (3位まで)
        # -------------------
        
        if other_results:
            st.write("以下もあなたの可能性を広げる職種です。")
            
            display_candidates = []
            current_rank = 2 # 第一適職の次なので常に2位からスタート
            
            # 2位のスコアを取得
            next_score = other_results[0][0]
            
            # ランキングを付けて3位まで抽出（同点の結果は全て表示）
            
            # まず、2位の同点グループを全て抽出
            same_score_group = []
            for score, name in other_results:
                if score == next_score:
                    same_score_group.append(name)
                else:
                    break
            
            # 2位グループを候補に追加
            for name in same_score_group:
                display_candidates.append((current_rank, name))

            
            # 3位・4位グループを探す
            remaining_results = other_results[len(same_score_group):]
            if remaining_results:
                current_rank += 1 # 3位へ
                next_score = remaining_results[0][0]

                for score, name in remaining_results:
                    if score == next_score and current_rank <= 4: # 4位も表示する可能性を残し、次点を3位まで
                        display_candidates.append((current_rank, name))
                    elif score < next_score and current_rank <= 3:
                        current_rank += 1 # 順位を上げる
                        next_score = score
                        if current_rank <= 4:
                            display_candidates.append((current_rank, name))
                        else:
                            break
                    elif current_rank > 4:
                        break

            # 最終的な表示 (順位が4位以上のものは切り捨てる)
            final_candidates = [ (rank, name) for rank, name in display_candidates if rank <= 4 ]
            
            # 表示
            for rank, name in final_candidates:
                # 順位を正しく表示 (第一適職を1位とするため)
                st.write(f"**第{rank}位候補**：{name}")

        else:
            st.write("他の職種も全体的に高い適性を持っています！すべての職種で高い潜在能力があります。")
