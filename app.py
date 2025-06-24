from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

# Load data
names_df = pd.read_csv("NAMES.csv")
wt1_df = pd.read_csv("WT-1.csv")
wt2_df = pd.read_csv("WT-2.csv")
wt3_df = pd.read_csv("WT-3.csv")
wt4_df = pd.read_csv("WT-4.csv")

wt3_df.rename(columns={"CHEM": "CHE"}, inplace=True)

MAX_MARK = 120
TOTAL_MAX = 360

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            student_id = int(request.form["student_id"])
        except:
            return render_template("index.html", result="Invalid ID")

        if student_id not in names_df["IDNO"].values:
            return render_template("index.html", result="Student ID not found.")
        
        student = names_df[names_df["IDNO"] == student_id].iloc[0]
        name = student["NAME"]
        section = student["SEC"]

        test_dfs = [("WT-1", wt1_df), ("WT-2", wt2_df), ("WT-3", wt3_df),("WT-4", wt4_df)]
        records = []
        graph_data = {"Test": [], "MAT": [], "PHY": [], "CHE": []}

        for label, df in test_dfs:
            row = df[df["IDNO"] == student_id]
            exdate = row["EXDATE"].values[0] if "EXDATE" in df.columns and not row.empty else ""
            if row.empty:
                record = {
                    "Test": label, "Date": exdate,
                    "MAT": "Absent", "PHY": "Absent", "CHE": "Absent",
                    "TOT": "Absent", "PERCENT": "Absent"
                }
            else:
                row = row.iloc[0]
                try:
                    mat = float(row["MAT"])
                    phy = float(row["PHY"])
                    che = float(row["CHE"])
                except:
                    mat = phy = che = 0

                total = mat + phy + che
                percent = round((total / TOTAL_MAX) * 100, 2)
                record = {
                    "Test": label, "Date": exdate,
                    "MAT": mat, "PHY": phy, "CHE": che,
                    "TOT": total, "PERCENT": f"{percent}%"
                }
                graph_data["Test"].append(label)
                graph_data["MAT"].append(mat)
                graph_data["PHY"].append(phy)
                graph_data["CHE"].append(che)
            records.append(record)

        valid_rows = [r for r in records if isinstance(r["MAT"], (int, float)) and isinstance(r["PHY"], (int, float)) and isinstance(r["CHE"], (int, float))]

        if valid_rows:
            total_mat = sum(r["MAT"] for r in valid_rows)
            total_phy = sum(r["PHY"] for r in valid_rows)
            total_che = sum(r["CHE"] for r in valid_rows)
            total_total = sum(r["TOT"] for r in valid_rows)
            total_percent = round((total_total / (TOTAL_MAX * len(valid_rows))) * 100, 2)

            avg_mat = round(total_mat / len(valid_rows), 2)
            avg_phy = round(total_phy / len(valid_rows), 2)
            avg_che = round(total_che / len(valid_rows), 2)
            avg_total = round(avg_mat + avg_phy + avg_che, 2)
            avg_percent = round((avg_total / TOTAL_MAX) * 100, 2)
        else:
            total_mat = total_phy = total_che = total_total = total_percent = 0
            avg_mat = avg_phy = avg_che = avg_total = avg_percent = 0

        records.append({
            "Test": "Total", "Date": "",
            "MAT": total_mat, "PHY": total_phy, "CHE": total_che,
            "TOT": total_total, "PERCENT": f"{total_percent}%"
        })
        records.append({
            "Test": "AVERAGE", "Date": "",
            "MAT": avg_mat, "PHY": avg_phy, "CHE": avg_che,
            "TOT": avg_total, "PERCENT": f"{avg_percent}%"
        })

        df_graph = pd.DataFrame(graph_data)
        plt.figure(figsize=(6, 4))
        for subj in ["MAT", "PHY", "CHE"]:
            plt.plot(df_graph["Test"], df_graph[subj], marker='o', label=subj)
        plt.title(f"{name} ({student_id})")
        plt.xlabel("Test")
        plt.ylabel("Marks")
        plt.legend()
        plt.grid(True)
        graph_file = f"static/{student_id}.png"
        plt.savefig(graph_file)
        plt.close()

        result = {
            "name": name,
            "id": student_id,
            "sec": section,
            "report_rows": records,
            "graph": graph_file
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
