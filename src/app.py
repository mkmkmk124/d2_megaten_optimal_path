import streamlit as st
import os
import sys
sys.path.insert(0, "./src")


DUMMY_NAME = "-"


def writeOptimalPair(church, name, arch):
    if arch:
        if 'left_name' in church.arch_scores[name]:
            st.write(f"{name}({church.getArchStr(arch)}) = {church.arch_scores[name]['left_name']}({church.getArchStr(church.arch_scores[name]['left_arch'])}) + {church.arch_scores[name]['right_name']}({church.getArchStr(church.arch_scores[name]['right_arch'])})")
            writeOptimalPair(church, church.arch_scores[name]['left_name'], church.arch_scores[name]["left_arch"])
            writeOptimalPair(church, church.arch_scores[name]['right_name'], church.arch_scores[name]["right_arch"])
    else:
        if 'left_name' in church.base_scores[name]:
            st.write(f"{name}({church.getArchStr(arch)}) = {church.base_scores[name]['left_name']}({church.getArchStr(church.base_scores[name]['left_arch'])}) + {church.base_scores[name]['right_name']}({church.getArchStr(church.base_scores[name]['right_arch'])})")
            writeOptimalPair(church, church.base_scores[name]['left_name'], church.base_scores[name]["left_arch"])
            writeOptimalPair(church, church.base_scores[name]['right_name'], church.base_scores[name]["right_arch"])

st.title("悪魔合体 最適合体パス探索")

from church import Church
DEVIL_LIST = os.path.join(os.path.dirname(__file__), "../data/devil_list.csv")
COMB_JSON = os.path.join(os.path.dirname(__file__), "../data/combination.json")
church = Church(DEVIL_LIST, COMB_JSON)

st.sidebar.markdown("## 最適経路探索対象悪魔の指定")
target = st.sidebar.selectbox(
    '悪魔名称',
    [DUMMY_NAME] + list(church.data["name"].values),
    0
    )

arch = st.sidebar.checkbox('アーキタイプ付き', True)

st.sidebar.markdown("## コストゼロ悪魔の指定")
rare_arch_flags = {}
rare_arch_flags["★★★★"] = st.sidebar.checkbox('★4悪魔(アーキタイプ付き)', False)
rare_arch_flags["★★★"] = st.sidebar.checkbox('★3悪魔(アーキタイプ付き)', True)
rare_arch_flags["★★"] = st.sidebar.checkbox('★2悪魔(アーキタイプ付き)', False)
rare_arch_flags["★"] = st.sidebar.checkbox('★1悪魔(アーキタイプ付き)', False)
rare_base_flags = {}
rare_base_flags["★★★★"] = st.sidebar.checkbox('★4悪魔(素体)', False)
rare_base_flags["★★★"] = st.sidebar.checkbox('★3悪魔(素体)', False)
rare_base_flags["★★"] = st.sidebar.checkbox('★2悪魔(素体)', True)
rare_base_flags["★"] = st.sidebar.checkbox('★1悪魔(素体)', True)

flagment_base_score_zero_devils = st.sidebar.multiselect(
    '断片召喚悪魔(素体)',
    ["マカミ","アピス","パワー","ミトラ"],
    ["マカミ","アピス","パワー","ミトラ"]
    )

aura2_50_devils = ["ティアマト", "セタンタ", "アラハバキ", "フォルネウス", "ライラ", "カマソッソ","ユニコーン","カハク"]
aura2_50_base_score_zero_devils = st.sidebar.multiselect(
    'アウラゲート2_50層出現悪魔(素体)',
    aura2_50_devils,
    []
    )

other_base_score_zero_devils = st.sidebar.multiselect(
    'その他悪魔(素体)',
    church.data["name"].values,
    []
    )
other_arch_score_zero_devils = st.sidebar.multiselect(
    'その他悪魔(アーキタイプ付き)',
    church.data["name"].values,
    []
    )
base_score_zero_devils = flagment_base_score_zero_devils + aura2_50_base_score_zero_devils + other_base_score_zero_devils
for rare, rare_base_flag in rare_base_flags.items():
    if rare_base_flag:
        base_score_zero_devils += list(church.getDevilsNameByRare(rare).values)
arch_score_zero_devils = other_arch_score_zero_devils
for rare, rare_arch_flag in rare_arch_flags.items():
    if rare_arch_flag:
        arch_score_zero_devils += list(church.getDevilsNameByRare(rare).values)

if target != DUMMY_NAME:
    church.calcOptimalPath(target,
                          arch=arch,
                          base_score_zero_devils=base_score_zero_devils,
                          arch_score_zero_devils=arch_score_zero_devils)

    st.write(f"■対象悪魔: {church.target['name']} ({church.getArchStr(church.arch)})")
    st.write(f"■総マグネタイト: {church.score}")
    st.write("■合体経路:")
    writeOptimalPair(church, target, arch)

st.markdown("- - -")
FOOTER="""
## ページ概要
「Ｄ×２ * 真・女神転生リベレーション」において、指定された悪魔への最適な合体経路を検索し、使用マグネタイト料とその合体経路を表示します。
最適な合体経路とは、合体に使用するマグネタイトが一番少ない合体経路を意味しています。

## 使い方
1. 左サイドバーの「悪魔名称」に悪魔合体の最適経路を求めたい悪魔を選択します。
2. アーキタイプ付きの悪魔を合体したい場合には、左サイドバーの「アーキタイプ付き」をチェックします。(チェックがない場合には、素体の悪魔への合体経路を求めます。)
3. 最適経路計算の際に、マグネタイトのコストをゼロとみなす悪魔の設定をします。
4. ページ上部に指定された悪魔への最適合体経路と総マグネタイト使用量が表示されます。

## Copyright
* [「Ｄ×２ * 真・女神転生リベレーション」](https://d2-megaten-l.sega.jp/)は
[株式会社アトラス](https://www.atlus.co.jp/)、
[株式会社セガゲームス](https://sega-games.co.jp/) の著作物です。  
* 悪魔データは[wim-lab](https://github.com/wim-lab/d2)から取得、改変しています。
    * 改変内容: csvファイルへの形式変更、悪魔の名称変更
* ソースコードは[こちら](https://github.com/mkmkmk124/d2_megaten_optimal_path)
"""

st.markdown(FOOTER)

# for debug データ確認
# st.write(church.data)