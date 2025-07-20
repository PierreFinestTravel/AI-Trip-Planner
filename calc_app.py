
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trip Calculation Tool", layout="wide")

st.title("🧮 Trip Cost & Margin Calculator")

uploaded_file = st.file_uploader("Upload your Trip Planner Excel (from Trip Builder)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Trip file loaded. Please enter cost and currency per item below:")

    margin_rules = {
        "Accommodation": 0.17,  # default
        "Golf": 0.17,
        "Activity": 0.12,
        "Transport": 0.12
    }

    currency_rates = {
        "ZAR": st.number_input("ZAR to EUR", value=0.051, key="zar"),
        "USD": st.number_input("USD to EUR", value=0.92, key="usd"),
        "GBP": st.number_input("GBP to EUR", value=1.16, key="gbp")
    }

    use_agency = st.checkbox("Include Agency Commission?")
    agency_rate = st.selectbox("Agency Commission %", [10, 12], index=0) / 100 if use_agency else 0.0

    admin_fee_pct = 0.025  # 2.5%

    # Load cheat sheet
    cheat_sheet = pd.read_excel("cheat_sheet_full.xlsx")
    type_lookup = {row["Name"]: row["Type"] for _, row in cheat_sheet.iterrows()}

    table = []
    total_net = 0.0

    for i, row in df.iterrows():
        for col in ["Hotel", "Golf", "Activities", "Transport"]:
            items = str(row[col]).split(",") if pd.notna(row[col]) else []
            for item in items:
                name = item.strip()
                if not name: continue

                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
                with col1:
                    st.markdown(f"**{name}**")
                with col2:
                    cost = st.number_input(f"Cost ({name})", min_value=0.0, step=10.0, key=f"c_{i}_{name}")
                with col3:
                    currency = st.selectbox(f"Currency ({name})", ["EUR", "ZAR", "USD", "GBP"], key=f"cur_{i}_{name}")
                with col4:
                    margin_override = st.number_input(f"Margin % ({name})", min_value=0.0, max_value=100.0,
                                                      value=None, key=f"m_{i}_{name}")
                with col5:
                    st.write("")

                item_type = type_lookup.get(name, col[:-1])  # fallback to column type
                rate = currency_rates.get(currency, 1.0) if currency != "EUR" else 1.0
                margin_pct = (margin_override / 100) if margin_override is not None else margin_rules.get(item_type, 0.12)

                cost_eur = cost * rate
                margin_amount = cost_eur * margin_pct
                subtotal = cost_eur + margin_amount
                table.append({
                    "Item": name,
                    "Type": item_type,
                    "Base Cost": cost,
                    "Currency": currency,
                    "Rate": rate,
                    "EUR Cost": cost_eur,
                    "Margin %": margin_pct,
                    "Selling Price": subtotal
                })
                total_net += subtotal

    total_with_admin = total_net * (1 + admin_fee_pct)
    final_total = total_with_admin * (1 + agency_rate)

    st.subheader("💶 Final Calculation Summary")
    st.write(f"Subtotal after margin: €{total_net:,.2f}")
    st.write(f"Admin Fee (2.5%): €{total_with_admin - total_net:,.2f}")
    if use_agency:
        st.write(f"Agency Commission ({agency_rate*100:.0f}%): €{final_total - total_with_admin:,.2f}")
    st.write(f"**Total Selling Price: €{final_total:,.2f}**")

    df_out = pd.DataFrame(table)
    df_out["Total After Admin + Commission"] = df_out["Selling Price"] * (1 + admin_fee_pct) * (1 + agency_rate)

    st.download_button("📥 Download Pricing Breakdown", data=df_out.to_csv(index=False), file_name="Calculated_Pricing.csv")

else:
    st.info("Awaiting file upload.")
