import streamlit as st
import pandas as pd
import os

class ExpenseTracker:
    def __init__(self, members, csv_file="expenses.csv"):
        self.members = members  # 旅行メンバー
        self.csv_file = csv_file
        self.expenses = self.load_expenses()
    
    def add_expense(self, payer, amount, participants, description=""):
        split_amount = amount / len(participants)
        expense = {
            "payer": payer,
            "amount": amount,
            "participants": ",".join(participants),
            "description": description,
            "split_amount": split_amount
        }
        self.expenses.append(expense)
        self.save_expenses()
    
    def save_expenses(self):
        df = pd.DataFrame(self.expenses)
        df.to_csv(self.csv_file, index=False)
    
    def load_expenses(self):
        if os.path.exists(self.csv_file):
            return pd.read_csv(self.csv_file).to_dict(orient='records')
        return []
    
    def calculate_balances(self):
        balances = {member: 0 for member in self.members}
        for expense in self.expenses:
            balances[expense["payer"]] += expense["amount"]
            for participant in expense["participants"].split(","):
                balances[participant] -= expense["split_amount"]
        return balances
    
    def settle_debts(self):
        balances = self.calculate_balances()
        sorted_members = sorted(balances.items(), key=lambda x: x[1])
        settlements = []
        
        i, j = 0, len(sorted_members) - 1
        while i < j:
            debtor, debt_amount = sorted_members[i]
            creditor, credit_amount = sorted_members[j]
            
            amount = min(-debt_amount, credit_amount)
            balances[debtor] += amount
            balances[creditor] -= amount
            settlements.append(f"{debtor} → {creditor}: {amount:.2f}円")
            
            if balances[debtor] == 0:
                i += 1
            if balances[creditor] == 0:
                j -= 1
        
        return settlements

# Streamlit アプリのセットアップ
st.title("旅行費用精算アプリ")

# メンバーの設定
members = ["A", "B", "C"]
tracker = ExpenseTracker(members)

# 入力フォーム
st.subheader("支出の追加")
payer = st.selectbox("支払った人", members)
amount = st.number_input("金額", min_value=0, step=1000)
participants = st.multiselect("費用を負担する人", members, default=members)
description = st.text_input("用途")

if st.button("追加"):
    tracker.add_expense(payer, amount, participants, description)
    st.success("支出を追加しました！")
    st.experimental_rerun()

# 履歴表示
st.subheader("支出履歴")
expenses_df = pd.DataFrame(tracker.expenses)
if not expenses_df.empty:
    st.dataframe(expenses_df)
    
    if st.button("クリア履歴"):
        os.remove(tracker.csv_file)
        st.success("履歴を削除しました！")
        st.experimental_rerun()
else:
    st.write("履歴はありません。")

# 精算結果の表示
st.subheader("精算結果")
if st.button("計算"):
    settlements = tracker.settle_debts()
    if settlements:
        for settlement in settlements:
            st.write(settlement)
    else:
        st.write("精算の必要はありません。")