import streamlit as st

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

# --- スコアリングロジック（最終合意の対応表を反映） ---
# キーは質問番号(Q1, Q2...), 値は選択肢('A'または'B')と加算される結果IDのリスト
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

# --- 質問リスト ---
QUESTIONS = [
    ("Q1", "働く上で最も重視するのは？", 
     "組織全体の効率を考え、仕組みを改善・管理すること。", 
     "利用者一人ひとりの暮らしに寄り添い、身体介護を丁寧に提供すること。"),
    ("Q2", "困難な状況での自分の強みは？", 
     "感情的にならず、安定した精神で業務を淡々と遂行できる。", 
     "専門性を活かし、課題解決のために活発に意見を出し、行動できる。"),
    ("Q3", "上司や組織の方針への態度は？", 
     "自分の意見とは違っても、まずは上司の指示に従い、それを実行する。", 
     "納得できない点があれば、改善を求めて積極的に自分の考えを主張する。"),
    ("Q4", "理想とするサービス提供は？", 
     "居宅（自宅）での生活を支えるため、外部サービスを計画・調整する。", 
     "施設（入居）での生活全般を支えるため、チームで深く関わる。"),
    ("Q5", "利用者さんとの関わり方で好むのは？", 
     "小規模な環境で、認知症の方と家庭的に深く関わる。", 
     "大規模な環境で、医療ニーズの高い方や看取りまで支援する。"),
    ("Q6", "サービス提供の「時間」として好むのは？", 
     "利用者さんの自宅を訪問し、短時間・一対一の支援を行う。", 
     "施設や事業所で、日中または24時間体制で勤務する。"),
    ("Q7", "サービスの目的として共感するのは？", 
     "在宅復帰やリハビリを重視し、自立を促す集中的な支援。", 
     "生活の継続を第一に、日々の活動を一緒に楽しみ、レクリエーションを行う。"),
    ("Q8", "職場の「雰囲気」として理想的なのは？", 
     "多くの専門職が連携し、医療的ケアにも対応できる手厚い環境。", 
     "職員数が少なく、地域との連携も活発な複合的なサービスを提供する環境。"),
    ("Q9", "自分の人柄を表すならどちら？", 
     "積極的に前に出て引っ張るリーダーシップがある。", 
     "誰に対しても温厚で人当たりが良く、穏やかに接することができる。"),
    ("Q10", "仕事における自身の成長意欲は？", 
     "現状維持を望み、ストレスに鈍感でいることの安定性を重視する。", 
     "専門性を常に高め、新しい知識や技術の習得に意欲的に取り組む。"),
]

def calculate_score(answers):
    """回答に基づいてスコアを計算する"""
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
st.title("👨‍⚕️ 介護職の適職診断（全10問）")
st.markdown("ご自身の考えに最も近いものを選んでください。")
st.divider()

# 回答を保存するための辞書をセッションステートに格納
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# 質問の表示
with st.form(key='aptitude_form'):
    for q_code, q_title, choice_a, choice_b in QUESTIONS:
        st.subheader(f"{q_code}. {q_title}")
        
        # Streamlitのラジオボタンはユニークなキーが必要
        option = st.radio(
            label="選択してください",
            options=["A", "B"],
            format_func=lambda x: choice_a if x == "A" else choice_b,
            key=q_code,
            index=None,  # 初期選択なし
            label_visibility='collapsed' # ラベルは質問文で代用するため非表示に
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
        
        # 2位以下の結果を抽出
        top_other_results = [(score, name) for score, name in ranked_results if score < main_score]
        
        st.balloons()
        st.success("## 診断完了！あなたの適職タイプは...")
        
        st.markdown(f"**🥇 第一適職**: **{'、'.join(main_results)}**")
        st.metric(label="獲得スコア", value=f"{main_score}点")

        # 結果の詳細とメッセージ
        if "管理職" in main_results:
            st.info("""
            **【管理職】**の傾向が強く見られました。あなたは**感情的に安定し、組織の指示に従い、人当たりが良い**という、弊社が求める拠点長の特性を特に満たしています。
            現場での専門性よりも、組織の調和と運営を重視する働き方が最適です。
            """)
        else:
            st.info("あなたの適職は現場での専門性や特定のケアスタイルを活かせる職種です。")
        
        st.divider()
        st.subheader("その他の適職")
        
        if top_other_results:
            for i, (score, name) in enumerate(top_other_results[:3]): # 上位3つまで表示
                st.write(f"**{i+2}位**：{name} (スコア: {score}点)")
        else:
            st.write("全ての適職が同点でした！")