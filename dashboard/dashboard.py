import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "main.csv"))

# Mengubah kolom tanggal menjadi datetime
df["dteday"] = pd.to_datetime(df["dteday"])

# Mengubah kode tahun menjadi tahun sebenarnya
df["year"] = df["yr"].map({
    0: 2011,
    1: 2012
})

# Mengubah temperatur normalized menjadi Celsius
df["temp_c"] = df["temp"] * 41

st.title("🚲 Bike Sharing Dashboard")

st.write(
    "Dashboard analisis penyewaan sepeda berdasarkan data tahun 2011–2012."
)

st.subheader("📌 Business Questions")

with st.expander("Pertanyaan 1"):
    st.write(
        "Berapa persen pertumbuhan total penyewaan sepeda tahun "
        "2012 dibanding 2011, dan di bulan apa pertumbuhannya paling "
        "tinggi, agar operator bisa merencanakan penambahan sesuai "
        "bulan permintaan naik?"
    )

with st.expander("Pertanyaan 2"):
    st.write(
        "Pada rentang suhu berapa (per 5°C) rata-rata penyewaan "
        "harian tertinggi selama 2011–2012, dan di suhu berapa "
        "penyewaan turun lebih dari 25% dari puncaknya, agar operator "
        "bisa menetapkan ambang suhu untuk menambah atau mengurangi sepeda?"
    )

with st.expander("Pertanyaan 3"):
    st.write(
        "Berapa persentase penyewaan oleh pengguna casual dan "
        "registered terhadap total penyewaan sepeda selama 2011–2012, "
        "agar operator bisa menentukan segmen yang diprioritaskan "
        "untuk promosi?"
    )

st.sidebar.header("Filter Data")

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

filtered_df = df[df["year"].isin(selected_year)].copy()

total_rentals = filtered_df["cnt"].sum()
total_registered = filtered_df["registered"].sum()
total_casual = filtered_df["casual"].sum()

registered_pct = (
    total_registered / total_rentals * 100
)

casual_pct = (
    total_casual / total_rentals * 100
)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Penyewaan",
        f"{total_rentals:,}"
    )

with col2:
    st.metric(
        "Registered",
        f"{registered_pct:.2f}%"
    )

with col3:
    st.metric(
        "Casual",
        f"{casual_pct:.2f}%"
    )

st.subheader(
    "📈 Total Penyewaan Sepeda per Bulan"
)

monthly_rentals = (
    filtered_df
    .groupby(["mnth", "year"])["cnt"]
    .sum()
    .unstack()
)

fig, ax = plt.subplots(figsize=(10, 5))

for year in monthly_rentals.columns:
    ax.plot(
        monthly_rentals.index,
        monthly_rentals[year],
        marker="o",
        label=str(year)
    )

ax.set_title(
    "Perbandingan Total Penyewaan Sepeda Tahun 2011 dan 2012"
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penyewaan")

ax.set_xticks(range(1, 13))
ax.set_xticklabels([
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
])

ax.legend()
ax.grid(axis="y", alpha=0.3)

st.pyplot(fig)

st.subheader(
    "📊 Pertumbuhan Penyewaan Sepeda Tahun 2012 dibandingkan 2011"
)

# Menghitung pertumbuhan penyewaan per bulan
monthly_growth = (
    filtered_df
    .groupby(["mnth", "year"])["cnt"]
    .sum()
    .unstack()
)

# Memastikan kolom tahun tersedia
if 2011 in monthly_growth.columns and 2012 in monthly_growth.columns:

    monthly_growth["growth_pct"] = (
        (monthly_growth[2012] - monthly_growth[2011])
        / monthly_growth[2011]
    ) * 100

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        monthly_growth.index,
        monthly_growth["growth_pct"]
    )

    ax.set_title(
        "Pertumbuhan Penyewaan Sepeda Tahun 2012 dibandingkan 2011"
    )
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Pertumbuhan (%)")

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
    ])

    ax.grid(axis="y", alpha=0.3)

    st.pyplot(fig)

st.subheader(
    "🌡️ Rata-rata Penyewaan Berdasarkan Rentang Suhu"
)

# Membuat rentang suhu setiap 5°C
bins = range(0, 41, 5)

labels = [
    f"{i}-{i+5}°C"
    for i in range(0, 40, 5)
]

filtered_df["temp_range"] = pd.cut(
    filtered_df["temp_c"],
    bins=bins,
    labels=labels,
    right=False
)

avg_rentals_by_temp = (
    filtered_df
    .groupby(
        "temp_range",
        observed=False
    )["cnt"]
    .mean()
)

# Menghitung batas penurunan 25%
peak_rentals = avg_rentals_by_temp.max()
threshold_25 = peak_rentals * 0.75

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    avg_rentals_by_temp.index,
    avg_rentals_by_temp.values
)

ax.axhline(
    threshold_25,
    linestyle="--",
    label="Batas penurunan 25%"
)

ax.set_title(
    "Rata-rata Penyewaan Sepeda Berdasarkan Rentang Suhu"
)
ax.set_xlabel("Rentang Suhu")
ax.set_ylabel("Rata-rata Penyewaan Harian")

ax.legend()
ax.grid(axis="y", alpha=0.3)

st.pyplot(fig)

st.subheader(
    "👥 Proporsi Penyewaan Berdasarkan Tipe Pengguna"
)

user_type_pct = pd.Series({
    "Casual": casual_pct,
    "Registered": registered_pct
})

fig, ax = plt.subplots(figsize=(7, 7))

ax.pie(
    user_type_pct,
    labels=user_type_pct.index,
    autopct="%1.2f%%",
    startangle=90
)

ax.set_title(
    "Persentase Penyewaan Berdasarkan Tipe Pengguna"
)

st.pyplot(fig)

st.subheader("💡 Key Insights")

st.markdown("""
- Total penyewaan sepeda meningkat sebesar **64,88%** pada tahun 2012 dibandingkan tahun 2011, dengan pertumbuhan tertinggi terjadi pada bulan Maret sebesar **157,44%**.
- Rata-rata penyewaan harian tertinggi terjadi pada rentang suhu **25–30°C**, yaitu sebesar **5.726,24 penyewaan per hari**. Penyewaan turun lebih dari 25% dari nilai puncaknya mulai pada rentang suhu **15–20°C**.
- Pengguna **registered menyumbang 81,17%** dari total penyewaan selama 2011–2012, sedangkan pengguna **casual menyumbang 18,83%**.
""")

st.subheader("📌 Recommendation")

st.markdown("""
- Menyesuaikan ketersediaan sepeda dengan pola permintaan, terutama menjelang periode pertumbuhan tinggi seperti bulan Maret.
- Menyesuaikan alokasi sepeda berdasarkan kondisi suhu dengan mempertimbangkan tingginya penyewaan pada suhu 25–30°C.
- Mempertahankan pengguna registered serta membuat promosi yang ditujukan untuk meningkatkan penggunaan dari segmen casual.
""")
