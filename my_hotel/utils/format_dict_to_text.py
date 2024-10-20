def format_row(row):
    print("row",row)
    del row["id"]
    return "".join(f"{key.replace("_"," ").title()}:{row[key]} \n"  for key in row.keys())
