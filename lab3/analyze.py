import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Set seaborn style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)


def generate_plots():
    cleaned_file = "lab3/relative_risks_cleaned.csv"
    if not os.path.exists(cleaned_file):
        raise FileNotFoundError(f"{cleaned_file} not found. Run process_data.py first.")

    print(f"Loading cleaned data from {cleaned_file}...")
    df = pd.read_csv(cleaned_file)

    # 1. Histogram of Relative Risks for 'All-age' group
    print("Generating histogram_all_age.png...")
    plt.figure(figsize=(9, 5))
    all_age_data = df["All-age"].dropna()
    sns.histplot(all_age_data, bins=35, kde=True, color="#2b5c8f")
    plt.title("Rozkład Ryzyka Względnego (RR) dla grupy 'All-age'", fontsize=14, pad=15)
    plt.xlabel("Ryzyko Względne (RR)", fontsize=12)
    plt.ylabel("Liczebność (skala logarytmiczna)", fontsize=12)
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig("lab3/histogram_all_age.png", dpi=150)
    plt.close()

    # 2. Scatter Plot: Compare two age groups, '0-6 days' vs '7-27 days'
    print("Generating scatter_comparison.png...")
    plt.figure(figsize=(9, 5))
    scatter_data = df[["0-6 days", "7-27 days"]].dropna()
    sns.scatterplot(
        data=scatter_data,
        x="0-6 days",
        y="7-27 days",
        alpha=0.6,
        color="#e67e22",
        edgecolor="none",
    )

    # Draw y = x reference line
    max_val = max(scatter_data["0-6 days"].max(), scatter_data["7-27 days"].max())
    min_val = min(scatter_data["0-6 days"].min(), scatter_data["7-27 days"].min())
    plt.plot(
        [min_val, max_val],
        [min_val, max_val],
        "r--",
        linewidth=1.5,
        label="y = x (równe ryzyko)",
    )

    plt.xscale("log")
    plt.yscale("log")
    plt.title("Porównanie Ryzyka Względnego: 0-6 dni vs 7-27 dni", fontsize=14, pad=15)
    plt.xlabel("Ryzyko Względne (0-6 dni) - skala log", fontsize=12)
    plt.ylabel("Ryzyko Względne (7-27 dni) - skala log", fontsize=12)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig("lab3/scatter_comparison.png", dpi=150)
    plt.close()

    # 3. Bar Plot: Unsafe water source
    print("Generating water_source_risks.png...")
    # Filter for Unsafe water source and Diarrhoeal diseases
    water_df = df[
        (df["Risk"] == "Unsafe water source") & (df["Outcome"] == "Diarrhoeal diseases")
    ].copy()

    if len(water_df) > 0:
        plt.figure(figsize=(10, 6))
        # Melt selected columns for easy plotting
        age_groups_to_plot = [
            "All-age",
            "0-6 days",
            "7-27 days",
            "28-364 days",
            "1-4 years",
        ]
        melted_water = water_df.melt(
            id_vars=["Category_Units", "Sex"],
            value_vars=age_groups_to_plot,
            var_name="Grupa_Wiekowa",
            value_name="Ryzyko_Wzgledne",
        ).dropna()

        # Map age groups to Polish names for aesthetics
        pl_age_names = {
            "All-age": "Wszyscy",
            "0-6 days": "0-6 dni",
            "7-27 days": "7-27 dni",
            "28-364 days": "28-364 dni",
            "1-4 years": "1-4 lata",
        }
        melted_water["Grupa_Wiekowa"] = melted_water["Grupa_Wiekowa"].map(pl_age_names)

        sns.barplot(
            data=melted_water,
            x="Category_Units",
            y="Ryzyko_Wzgledne",
            hue="Grupa_Wiekowa",
            palette="viridis",
        )
        plt.title(
            "Ryzyko Względne Chorób Biegunkowych z powodu niebezpiecznej wody pitnej",
            fontsize=13,
            pad=15,
        )
        plt.xlabel("Kategoria wody pitnej", fontsize=11)
        plt.ylabel("Ryzyko Względne (RR)", fontsize=11)
        plt.xticks(rotation=15, ha="right")
        plt.legend(title="Grupa wiekowa", frameon=True)
        plt.tight_layout()
        plt.savefig("lab3/water_source_risks.png", dpi=150)
        plt.close()
    else:
        print(
            "Warning: No data found for 'Unsafe water source' and 'Diarrhoeal diseases' to plot."
        )


class PDFReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("ArialUnicode", "I", 8)
            self.cell(
                0,
                10,
                "Eksploracja i wizualizacja danych - Orange - Sprawozdanie Lab 3",
                align="R",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            # Draw a line below the header
            self.line(10, 18, 200, 18)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("ArialUnicode", "I", 8)
        self.cell(0, 10, f"Strona {self.page_no()}", align="C")


def create_report_pdf():
    pdf = PDFReport()

    # Load Arial system font to support Polish signs
    font_path = r"C:\Windows\Fonts\arial.ttf"
    bold_font = r"C:\Windows\Fonts\arialbd.ttf"
    italic_font = r"C:\Windows\Fonts\ariali.ttf"

    if os.path.exists(font_path):
        pdf.add_font("ArialUnicode", "", font_path)
    else:
        # Fallback if font isn't found
        pdf.add_font("ArialUnicode", "", "helvetica")

    if os.path.exists(bold_font):
        pdf.add_font("ArialUnicode", "B", bold_font)
    if os.path.exists(italic_font):
        pdf.add_font("ArialUnicode", "I", italic_font)

    # PAGE 1: COVER PAGE
    pdf.add_page()
    pdf.set_font("ArialUnicode", "B", 18)
    pdf.ln(40)
    pdf.cell(
        0, 15, "SPRAWOZDANIE Z LABORATORIUM", align="C", new_x="LMARGIN", new_y="NEXT"
    )
    pdf.set_font("ArialUnicode", "", 14)
    pdf.cell(
        0,
        10,
        "Eksploracja i Wizualizacja Danych",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(20)
    pdf.set_font("ArialUnicode", "B", 16)
    pdf.cell(
        0,
        12,
        "Zajęcie 3: Użycie Orange w celu eksploracji",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(0, 12, "i wizualizacji danych", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(40)
    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(0, 8, "Student:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(0, 8, "Imię i nazwisko: Patryk", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(0, 8, "Wariant zadania:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(
        0,
        8,
        "Wariant 13: Global Burden of Disease Study 2019 (GBD 2019) Relative Risks",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(30)
    pdf.set_font("ArialUnicode", "I", 10)
    pdf.cell(
        0, 10, "Data wykonania: Czerwiec 2026", align="C", new_x="LMARGIN", new_y="NEXT"
    )

    # PAGE 2: OBJECTIVE, SOFTWARE AND DATA DESCRIPTION
    pdf.add_page()
    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "1. Cel ćwiczenia", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Celem zajęć jest nabycie podstawowej znajomości programu Orange Data Mining poprzez "
        "zaprojektowanie potoku (pipeline) do eksploracji, transformacji oraz wizualizacji "
        "danych statystycznych dla określonego wariantu. Analiza została przeprowadzona "
        "na zestawie danych GBD 2019 Relative Risks, opisującym ryzyka względne "
        "związane z różnymi czynnikami ryzyka zdrowotnego w podziale na grupy wiekowe, "
        "płeć oraz kategorie chorobowe.",
    )
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "2. Opis oprogramowania Orange", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Orange to otwarte oprogramowanie do analizy danych, uczenia maszynowego i wizualnej "
        "eksploracji danych. Program opiera się na koncepcji programowania wizualnego, "
        "w którym użytkownik buduje procesy (workflows) poprzez przeciąganie widgetów "
        "na płótno (canvas) i łączenie ich kablami przesyłającymi dane. "
        "Główne zalety środowiska Orange to:\n"
        "- Przejrzysty podział na grupy widgetów (Data, Transform, Visualize, Model, Evaluate itp.).\n"
        "- Interaktywne wykresy powiązane ze sobą (wybór punktów na jednym wykresie filtruje dane na innym).\n"
        "- Możliwość łatwego prototypowania modeli uczenia maszynowego.",
    )
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "3. Przygotowanie i opis danych", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Dane do ćwiczenia pochodzą z bazy danych GBD 2019 (Global Burden of Disease). "
        "Oryginalny plik excel 'relative_risks.xlsx' zawierał złożoną strukturę tabelaryczną z połączonymi komórkami "
        "oraz wartościami zapisanymi w postaci przedziałów ufności, np. '1.12 (1.05 - 1.20)'.\n"
        "W celu wczytania danych do programu Orange przygotowano skrypt w języku Python "
        "('process_data.py'), który wykonał następujące kroki czyszczenia danych:\n"
        "1. Odczytanie struktury nagłówków (wyodrębnienie grup wiekowych od kolumny 4 do 27).\n"
        "2. Przekształcenie danych z formy hierarchicznej do płaskiej struktury tabelarycznej.\n"
        "3. Wyekstrahowanie wartości średniej (pierwszej liczby przed nawiasem) dla każdej grupy wiekowej "
        "i zapisanie jej jako wartości numerycznej (float).\n"
        "4. Zapisanie oczyszczonych danych do formatu CSV: 'relative_risks_cleaned.csv'.",
    )
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(
        0,
        10,
        "4. Opis potoku (pipeline) w programie Orange",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Zbudowany potok w programie Orange składa się z następujących połączonych ze sobą widgetów:\n"
        "1. Widget File: Odpowiada za wczytanie pliku CSV 'relative_risks_cleaned.csv'. "
        "W ustawieniach pliku zdefiniowano odpowiednie typy kolumn (np. kolumny numeryczne dla grup wiekowych, "
        "tekstowe dla czynników ryzyka i płci).\n"
        "2. Widget Select Columns: Pozwala na określenie roli zmiennych w analizie. Zmienne "
        "'Risk', 'Outcome', 'Category_Units', 'Morbidity_Mortality' oraz 'Sex' zostały oznaczone "
        "jako metadane (meta attributes), natomiast kolumny z ryzykiem względnym dla poszczególnych "
        "grup wiekowych jako cechy (features).\n"
        "3. Widget Data Table: Podłączony do 'Select Columns' w celu bieżącej weryfikacji tabeli danych.\n"
        "4. Widget Distributions: Służy do wizualizacji rozkładu zmiennej 'All-age' w postaci histogramu.\n"
        "5. Widget Scatter Plot: Porównuje wartości ryzyka względnego między dwiema grupami wiekowymi "
        "('0-6 days' na osi X oraz '7-27 days' na osi Y).",
    )

    # PAGE 3: RESULTS - HISTOGRAM & SCATTER PLOT
    pdf.add_page()
    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(
        0, 10, "5. Wyniki eksploracji i wizualizacji", new_x="LMARGIN", new_y="NEXT"
    )

    pdf.set_font("ArialUnicode", "B", 11)
    pdf.cell(
        0,
        8,
        "5.1 Rozkład wartości ryzyka względnego (Histogram dla grupy 'All-age')",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        5.5,
        "Poniższy histogram (Wykres 1) przedstawia rozkład wartości ryzyka względnego dla grupy 'All-age'. "
        "Ze względu na dużą rozpiętość wartości, zastosowano skalę logarytmiczną na osi Y.",
    )
    pdf.ln(2)

    # Embed Histogram
    if os.path.exists("lab3/histogram_all_age.png"):
        pdf.image("lab3/histogram_all_age.png", x=15, w=180)
        pdf.ln(2)
        pdf.set_font("ArialUnicode", "I", 9)
        pdf.cell(
            0,
            8,
            "Wykres 1: Rozkład Ryzyka Względnego (RR) dla grupy 'All-age'",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(2)

    pdf.set_font("ArialUnicode", "B", 11)
    pdf.cell(
        0,
        8,
        "5.2 Porównanie grup wiekowych: 0-6 dni vs 7-27 dni",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        5.5,
        "Wykres punktowy (Wykres 2) przedstawia zależność wartości ryzyka względnego między dwoma pierwszymi "
        "okresami życia noworodków. Obydwie osie przedstawiono w skali logarytmicznej.",
    )
    pdf.ln(2)

    # Embed Scatter Plot
    if os.path.exists("lab3/scatter_comparison.png"):
        pdf.image("lab3/scatter_comparison.png", x=15, w=180)
        pdf.ln(2)
        pdf.set_font("ArialUnicode", "I", 9)
        pdf.cell(
            0,
            8,
            "Wykres 2: Wykres punktowy ryzyka względnego: 0-6 dni vs 7-27 dni",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(2)

    # PAGE 4: RESULTS - BAR PLOT, CONCLUSIONS AND REPO LINK
    pdf.add_page()
    pdf.set_font("ArialUnicode", "B", 11)
    pdf.cell(
        0,
        8,
        "5.3 Ryzyko względne dla czynnika 'Unsafe water source'",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        5.5,
        "Przeprowadzono szczegółową analizę wpływu niebezpiecznej wody pitnej na występowanie chorób "
        "biegunkowych. Poniższy wykres słupkowy (Wykres 3) przedstawia wartości ryzyka względnego "
        "w podziale na kategorie jakości wody oraz wybrane grupy wiekowe.",
    )
    pdf.ln(2)

    # Embed Bar Plot
    if os.path.exists("lab3/water_source_risks.png"):
        pdf.image("lab3/water_source_risks.png", x=15, w=180)
        pdf.ln(2)
        pdf.set_font("ArialUnicode", "I", 9)
        pdf.cell(
            0,
            8,
            "Wykres 3: Ryzyko względne chorób biegunkowych z powodu niebezpiecznej wody pitnej",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(2)

    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "6. Podsumowanie i wnioski", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 10)
    pdf.multi_cell(
        0,
        6,
        "1. Rozkład ryzyka względnego w grupie 'All-age' wykazuje silną asymetrię prawostronną. "
        "Większość czynników charakteryzuje się brakiem lub niskim wpływem na ryzyko chorobowe (wartości RR wokół 1.0), "
        "jednak istnieją rzadkie patogeny/czynniki o ekstremalnym wpływie, gdzie RR przekracza 10.0.\n"
        "2. Analiza wykresu punktowego wykazuje niemal idealną liniową korelację ryzyka względnego pomiędzy "
        "grupami wiekowymi 0-6 dni oraz 7-27 dni. Wynika to z faktu, że czynniki ryzyka środowiskowego i biologicznego "
        "oddziałują w bardzo podobny sposób w całym pierwszym miesiącu życia noworodka.\n"
        "3. W przypadku niebezpiecznej wody pitnej ('Unsafe water source'), ryzyko względne chorób biegunkowych "
        "jest najwyższe w grupie wiekowej '28-364 days' oraz '1-4 years'. Jest to spójne z wiedzą medyczną – "
        "w tym okresie następuje odstawianie od piersi i wprowadzanie pokarmów stałych/wody, co dramatycznie "
        "zwiększa ekspozycję dzieci na zanieczyszczenia patogenne.",
    )
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "7. Link do repozytorium zdalnego", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUnicode", "", 10)
    pdf.cell(
        0,
        6,
        "Wszystkie skrypty, dane oraz plik projektu Orange zostały umieszczone w zdalnym repozytorium GitHub:",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("ArialUnicode", "I", 10)
    pdf.cell(
        0,
        6,
        "https://github.com/patryk-eiwd/lab3-orange",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    output_path = "lab3/Sprawozdanie_Lab3.pdf"
    pdf.output(output_path)
    print(f"Successfully generated report PDF: {output_path}")


if __name__ == "__main__":
    generate_plots()
    create_report_pdf()
