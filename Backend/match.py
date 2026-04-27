def extract_skills(text):
    
    skills_db = [
        "python", "java", "c++", "c", "javascript", "typescript",
        "html", "css", "react", "angular", "vue",
        "node.js", "express", "django", "flask",
        "spring boot", "rest api", "graphql", "machine learning",
        "deep learning", "ai", "nlp",
        "computer vision", "data science", "data analysis",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "statistics", "linear algebra", "calculus",
        "sql", "mysql", "postgresql", "mongodb", "firebase",
        "redis", "data warehousing", "etl",
        "aws", "azure", "gcp",
        "docker", "kubernetes", "ci/cd",
        "jenkins", "terraform", "linux", "bash",
        "data structures", "algorithms", "system design",
        "operating systems", "computer networks", "dbms",
        "oop", "object oriented programming",
        "bioinformatics", "genomics", "proteomics",
        "molecular biology", "cell biology", "biochemistry",
        "crispr", "drug discovery", "clinical trials",
        "biostatistics", "lab techniques", "microscopy",
        "digital marketing", "seo", "sem", "content marketing",
        "social media marketing", "email marketing",
        "google analytics", "branding", "market research",
        "copywriting", "growth hacking",
        "project management", "product management",
        "agile", "scrum", "kanban",
        "leadership", "team management", "communication",
        "stakeholder management", "business analysis",
        "strategic planning", "operations management",
        "financial analysis", "accounting", "excel",
        "forecasting", "budgeting", "risk management",
        "ui/ux", "figma", "adobe xd", "photoshop",
        "user research", "wireframing", "prototyping"
    ]

    text = text.lower()

    skills = []

    for skill in skills_db:
        if skill in text:
            skills.append(skill)

    return list(set(skills))

def calculate_match(resume_skills, jd_skills):

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    if jd_skills:
        score = (len(matched) / len(jd_skills)) * 100
    else:
        score = 0   

    return score, matched, missing