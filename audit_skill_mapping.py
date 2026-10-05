from collections import Counter

from app.core.skill_mapping import SKILL_MAPPING


all_skills = []

for category, activities in SKILL_MAPPING.items():
    for activity_type, skills in activities.items():
        all_skills.extend(skills)


counter = Counter(all_skills)

print("=" * 60)
print("AUDIT SKILL MAPPING")
print("=" * 60)

print()
print(f"Total skill entries : {len(all_skills)}")
print(f"Unique skill names  : {len(counter)}")

print()
print("=" * 60)
print("DUPLIKAT PERSIS")
print("=" * 60)

duplicates = {
    skill: count
    for skill, count in counter.items()
    if count > 1
}

if duplicates:
    for skill, count in sorted(duplicates.items()):
        print(f"- {skill}: {count}x")
else:
    print("Tidak ada duplikat.")


print()
print("=" * 60)
print("SELURUH SKILL UNIK")
print("=" * 60)

for index, skill in enumerate(
    sorted(counter),
    start=1,
):
    print(
        f"{index:02d}. {skill}"
    )


print()
print("=" * 60)
print("KELOMPOK ISTILAH YANG PERLU REVIEW")
print("=" * 60)

possible_groups = [
    (
        "Berhitung / Counting",
        ["Berhitung", "Counting"],
    ),
    (
        "Memori / Recall",
        ["Memori", "Recall"],
    ),
    (
        "Kosakata / Vocabulary",
        ["Kosakata", "Vocabulary"],
    ),
    (
        "Visual-Spatial",
        ["Visual-Spatial", "Visual Spatial"],
    ),
    (
        "Mencocokkan / Matching",
        [
            "Mencocokkan Angka dan Jumlah",
            "Quantity Matching",
            "Mencocokkan Warna",
            "Color Matching",
            "Mencocokkan Bentuk",
            "Shape Matching",
            "Animal Matching",
            "Visual Matching",
            "Matching",
        ],
    ),
    (
        "Pengenalan / Recognition",
        [
            "Pengenalan Angka",
            "Number Recognition",
            "Color Recognition",
            "Mengenali Warna",
            "Shape Recognition",
            "Mengenali Bentuk",
            "Pengenalan Hewan",
            "Animal Recognition",
        ],
    ),
    (
        "Koordinasi",
        [
            "Koordinasi",
            "Koordinasi Mata-Tangan",
            "Respons Visual",
        ],
    ),
]


for title, skills in possible_groups:
    existing = [
        skill
        for skill in skills
        if skill in counter
    ]

    print()
    print(f"{title}:")
    
    if existing:
        for skill in existing:
            print(f"  - {skill}")
    else:
        print("  - Tidak ditemukan")