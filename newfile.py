import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account

# Streamlitアプリのタイトル設定
st.title('スプレッドシート データ整形アプリ')

# サイドバーの設定
st.sidebar.header('設定')
uploaded_file = st.sidebar.file_uploader("JSONキーファイルをアップロード", type=['json'])

# スプレッドシートのURL入力
spreadsheet_url = st.sidebar.text_input('スプレッドシートのURLを入力してください')
sheet_name = st.sidebar.text_input('シート名を入力してください（空白の場合は最初のシート）')

if uploaded_file and spreadsheet_url:
    # 認証情報の設定
    try:
        credentials_dict = pd.read_json(uploaded_file, typ='series').to_dict()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        gc = gspread.authorize(credentials)
        
        # スプレッドシートIDを抽出
        if '/d/' in spreadsheet_url and '/edit' in spreadsheet_url:
            spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/edit')[0]
        else:
            spreadsheet_id = spreadsheet_url
        
        # スプレッドシートを開く
        sh = gc.open_by_key(spreadsheet_id)
        
        # シートを選択
        if sheet_name:
            worksheet = sh.worksheet(sheet_name)
        else:
            worksheet = sh.sheet1
        
        # データを取得
        data = worksheet.get_all_values()
        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)
        
        # データの表示
        st.subheader('取得したデータ')
        st.dataframe(df)
        
        # データ整形オプション
        st.subheader('データ整形オプション')
        
        # 列の選択
        selected_columns = st.multiselect('表示する列を選択', df.columns.tolist(), default=df.columns.tolist())
        
        # 行のフィルタリング
        filter_column = st.selectbox('フィルタリングする列を選択', ['なし'] + df.columns.tolist())
        
        if filter_column != 'なし':
            unique_values = df[filter_column].unique().tolist()
            filter_values = st.multiselect(f'{filter_column}の値を選択', unique_values, default=unique_values)
            filtered_df = df[df[filter_column].isin(filter_values)]
        else:
            filtered_df = df
        
        # 選択した列のみ表示
        if selected_columns:
            filtered_df = filtered_df[selected_columns]
        
        # 整形後のデータを表示
        st.subheader('整形後のデータ')
        st.dataframe(filtered_df)
        
        # CSVダウンロードボタン
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSVとしてダウンロード",
            data=csv,
            file_name="formatted_data.csv",
            mime="text/csv",
        )
        
    except Exception as e:
        st.error(f'エラーが発生しました: {e}')
else:
    st.info('JSONキーファイルとスプレッドシートのURLを入力してください。')
    
    # 使い方の説明
    st.subheader('使い方')
    st.markdown("""
    1. Google Cloud Platformでサービスアカウントを作成し、JSONキーをダウンロードします
    2. スプレッドシートを作成し、サービスアカウントと共有します
    3. JSONキーファイルをアップロードし、スプレッドシートのURLを入力します
    4. データを整形して表示・ダウンロードできます
    """)

