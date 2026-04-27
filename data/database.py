import pandas as pd

df1 = pd.read_csv(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\coding_interview_question_bank.csv")
df1 = df1[["question", "category"]]

df2 = pd.read_csv(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\python_interview_questions_500.csv")

df2 = df2.rename(columns = {
    "topic": "category"
})

df2 = df2[["question", "category"]]

df3 = pd.read_excel(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\Interview_Questions.xlsx")

df3 = df3.rename(columns={
    "Question": "question",
    "Skill": "category"
})

df3 = df3[["question", "category"]]

df4 = pd.read_csv(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\Software Questions.csv",encoding="cp1252")
encoding="latin1"
df4 = df4.rename(columns={
    "Question": "question",
    "Category": "category"
})

df4 = df4[["question", "category"]]

final_df = pd.concat(
    [df1, df2, df3, df4],
    ignore_index=True
)

final_df.drop_duplicates(
    subset=["question"],
    inplace=True
)

final_df.dropna(
    subset=["question", "category"],
    inplace=True
)

# final_df.to_csv(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\final_interview_questions.csv", index=False)

