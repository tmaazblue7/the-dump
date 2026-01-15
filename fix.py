from pathlib import Path
import re

p = Path("src/weekly_breakdown.py")
s = p.read_text()

# 1) Ensure pandas import is present
if "import pandas as pd" not in s:
    lines = s.splitlines(True)
    insert_at = 0
    if lines and lines[0].lstrip().startswith('"""'):
        # Skip module docstring
        for i in range(1, len(lines)):
            if lines[i].lstrip().startswith('"""'):
                insert_at = i + 1
                break
    lines.insert(insert_at, "import pandas as pd\n")
    s = "".join(lines)

# 2) Replace inplace dropna (avoids SettingWithCopyWarning)
s = s.replace(
    "historical_df.dropna(subset=['Historical_Call_Volume'], inplace=True)",
    "historical_df = historical_df.dropna(subset=['Historical_Call_Volume']).copy()"
)

# 3) Insert robust month-weights helper if missing
if "_get_month_weights(" not in s:
    # Insert after the last import line
    lines = s.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
        elif line.strip():
            break
    helper = '''
from typing import List

def _get_month_weights(weekly_pattern: "pd.DataFrame | pd.Series", month_num: int) -> List[float]:
    """
    Return a normalized list of 4 weekly weights for the given month.
    Works with MultiIndex or simple Index. Falls back to equal weights.
    """
    import pandas as pd  # local import keeps function portable
    # Which months exist?
    if isinstance(weekly_pattern.index, pd.MultiIndex):
        months_in_index = weekly_pattern.index.get_level_values(0).unique()
    else:
        months_in_index = weekly_pattern.index.unique()

    if month_num in months_in_index:
        try:
            row = weekly_pattern.loc[month_num]
        except Exception:
            return [0.25, 0.25, 0.25, 0.25]
        if isinstance(row, pd.DataFrame):
            vals = row.squeeze().to_numpy().tolist()
        elif isinstance(row, pd.Series):
            vals = row.to_numpy().tolist()
        else:
            try:
                vals = list(row)
            except Exception:
                return [0.25, 0.25, 0.25, 0.25]
    else:
        return [0.25, 0.25, 0.25, 0.25]

    # Coerce to exactly 4 weights (merge overflow, pad short)
    if len(vals) > 4:
        vals = vals[:3] + [sum(vals[3:])]
    elif len(vals) < 4:
        vals = vals + [0.0] * (4 - len(vals))

    # Normalize safely
    total = sum(v for v in vals if pd.notna(v))
    if not total or total <= 0:
        return [0.25, 0.25, 0.25, 0.25]
    return [float(v)/float(total) if pd.notna(v) else 0.0 for v in vals]
'''
    lines.insert(insert_at, helper)
    s = "".join(lines)

# 4) Replace the fragile membership check using .levels[0]
pattern = re.compile(
    r"weights\s*=\s*weekly_pattern\.loc\[month_num\]\s*if\s*month_num\s*in\s*weekly_pattern\.index\.levels\[0\]\s*else\s*\[[^\]]*\]"
)
s, n = pattern.subn("weights = _get_month_weights(weekly_pattern, month_num)", s)
if n == 0:
    pattern2 = re.compile(
        r"weights\s*=\s*weekly_pattern\.loc\[\s*month_num\s*\]\s*if\s*month_num\s*in\s*weekly_pattern\.index\.levels\[\s*0\s*\]\s*else\s*\[[^\]]*\]"
    )
    s, n2 = pattern2.subn("weights = _get_month_weights(weekly_pattern, month_num)", s)

p.write_text(s)
print("Updated src/weekly_breakdown.py")