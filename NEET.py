import cv2
import numpy as np
import os
import pandas as pd
from pathlib import Path
from pdf2image import convert_from_path

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input" / "NEET"
OUTPUT_DIR = BASE_DIR / "output"

NEET_OMR_PATH = INPUT_DIR / "neet_omr_sheet1_merged.pdf"
OUTPUT_EXCEL = OUTPUT_DIR / "NEET_Results.xlsx"
POPPLER_PATH = None

OUTPUT_DIR.mkdir(exist_ok=True)

# 📍 YOUR PERFECTED LADDER ZONES
ZONE_L = [19, 155, 155, 2818]
ZONE_R = [2315, 132, 128, 2849]

# 📍 YOUR EXTRACTED ROIS
ROIS = {
    'roll':         (179, 401, 619, 526),
    'booklet_no':   (265, 1099, 452, 522),
    'booklet_code': (226, 1769, 533, 140),
    'q_1_50':       (986, 296, 241, 2549),
    'q_51_100':     (1360, 300, 233, 2541),
    'q_101_150':    (1730, 304, 233, 2529),
    'q_151_200':    (2100, 304, 233, 2533),
}

# 📍 YOUR TUNED GRID CONFIGURATION
BUBBLE_RADIUS = 12
SECTION_CONFIG = {
    'roll':         {'cols': 10, 'padding': -3, 'nudge_x': 1, 'nudge_y': 49, 'max_rows': 10},
    'booklet_no':   {'cols': 7,  'padding': 7,  'nudge_x': 1, 'nudge_y': 51, 'max_rows': 10},
    'booklet_code': {'cols': 4,  'padding': 16, 'nudge_x': 3, 'nudge_y': 50, 'max_rows': 1},
    'q_1_50':       {'cols': 4,  'padding': 13, 'nudge_x': 4, 'nudge_y': 1,  'max_rows': 50},
    'q_51_100':     {'cols': 4,  'padding': 9,  'nudge_x': 5, 'nudge_y': 0,  'max_rows': 50},
    'q_101_150':    {'cols': 4,  'padding': 9,  'nudge_x': 5, 'nudge_y': 0,  'max_rows': 50},
    'q_151_200':    {'cols': 4,  'padding': 9,  'nudge_x': 6, 'nudge_y': 0,  'max_rows': 50},
}

# 🎯 YOUR LOCKED SENSITIVITY THRESHOLDS
THRESHOLD_VALID = 398    
THRESHOLD_EMPTY = 250    

# ==========================================
# 🔧 CORE ENGINE
# ==========================================

def get_ladder_marks(img, zone):
    x, y, w, h = zone
    roi = img[y:y+h, x:x+w].copy()
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    raw_centers = [(x + bx + bw//2, y + by + bh//2) for c in cnts if 10 < cv2.contourArea(c) < 20000 for bx, by, bw, bh in [cv2.boundingRect(c)]]
    raw_centers.sort(key=lambda pt: pt[1])
    
    clean = []
    if raw_centers:
        clean.append(raw_centers[0])
        for pt in raw_centers[1:]:
            if pt[1] - clean[-1][1] > 8: clean.append(pt)
    return clean

def build_paired_grid(left_marks, right_marks):
    pairs = []
    used_r = set()
    for lx, ly in left_marks:
        best_match = None
        min_dist = 999
        for i, (rx, ry) in enumerate(right_marks):
            if i in used_r: continue
            if abs(ry - ly) < 15 and abs(ry - ly) < min_dist:
                min_dist = abs(ry - ly)
                best_match = (i, rx, ry)
        if best_match:
            used_r.add(best_match[0])
            pairs.append((lx, ly, best_match[1], best_match[2]))
    return pairs

def extract_section_matrix(thresh_img, roi_coords, paired_grid, section_name):
    rx, ry, rw, rh = roi_coords
    cfg = SECTION_CONFIG[section_name]
    num_cols, max_rows = cfg['cols'], cfg['max_rows']
    nudge_x, nudge_y, padding = cfg['nudge_x'], cfg['nudge_y'], cfg['padding']

    start_x = rx + padding + nudge_x
    cell_w = (rw - (2 * padding)) / num_cols
    relevant_pairs = [p for p in paired_grid if (ry - 20) < p[1] < (ry + rh + 20)]
    
    matrix_scores = []
    for i, (lx, ly, grid_rx, grid_ry) in enumerate(relevant_pairs):
        if i >= max_rows: break
        row_data = []
        for c in range(num_cols):
            cx = int(start_x + (c * cell_w) + (cell_w / 2))
            cy = int(ly + (grid_ry - ly) * ((cx - lx) / (grid_rx - lx))) + nudge_y
            
            mask = np.zeros(thresh_img.shape, dtype="uint8")
            cv2.circle(mask, (cx, cy), BUBBLE_RADIUS, 255, -1)
            row_data.append(cv2.countNonZero(cv2.bitwise_and(thresh_img, thresh_img, mask=mask)))
        matrix_scores.append(row_data)
        
    return matrix_scores

def resolve_vertical_digits(matrix):
    if not matrix: return "?"
    
    # 🟢 FIXED: The exact order printed on the NEET OMR column (Top to Bottom)
    DIGIT_MAP = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    
    res = []
    for c in range(len(matrix[0])):
        col = [matrix[r][c] for r in range(len(matrix))]
        m_val = max(col)
        if m_val >= THRESHOLD_VALID:
            idx = col.index(m_val)
            res.append(DIGIT_MAP[idx] if idx < len(DIGIT_MAP) else "?")
        else:
            res.append("?")
    return "".join(res)

def resolve_answers(matrix):
    answers = []
    for scores in matrix:
        m_val = max(scores)
        if m_val >= THRESHOLD_VALID:
            answers.append("*" if len([s for s in scores if s >= THRESHOLD_EMPTY]) > 1 else chr(65 + scores.index(m_val)))
        else:
            answers.append("*" if m_val >= THRESHOLD_EMPTY else "-")
    return answers

def resolve_code(matrix):
    if not matrix or max(matrix[0]) < THRESHOLD_VALID: return "?"
    return chr(65 + matrix[0].index(max(matrix[0])))

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================

def main():
    if not os.path.exists(NEET_OMR_PATH): print(f"❌ File not found: {NEET_OMR_PATH}"); return

    all_results = []
    print("\n" + "█"*60 + "\n█  NEET OMR PRODUCTION ENGINE v3.1\n" + "█" + "="*58 + "█\n")

    try:
        pages = convert_from_path(NEET_OMR_PATH, dpi=300, poppler_path=POPPLER_PATH)
        for page_num, page_img in enumerate(pages):
            img = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            
            # 1. Map the Grid
            paired_grid = build_paired_grid(get_ladder_marks(img, ZONE_L), get_ladder_marks(img, ZONE_R))

            # 2. Extract Data Matrices
            roll_mat = extract_section_matrix(thresh, ROIS["roll"], paired_grid, "roll")
            book_mat = extract_section_matrix(thresh, ROIS["booklet_no"], paired_grid, "booklet_no")
            code_mat = extract_section_matrix(thresh, ROIS["booklet_code"], paired_grid, "booklet_code")
            
            # 3. Decode Matrices
            roll = resolve_vertical_digits(roll_mat)
            booklet = resolve_vertical_digits(book_mat)
            code = resolve_code(code_mat)
            
            a1 = resolve_answers(extract_section_matrix(thresh, ROIS["q_1_50"], paired_grid, "q_1_50"))
            a2 = resolve_answers(extract_section_matrix(thresh, ROIS["q_51_100"], paired_grid, "q_51_100"))
            a3 = resolve_answers(extract_section_matrix(thresh, ROIS["q_101_150"], paired_grid, "q_101_150"))
            a4 = resolve_answers(extract_section_matrix(thresh, ROIS["q_151_200"], paired_grid, "q_151_200"))

            full_ans = a1 + a2 + a3 + a4
            
            # 4. Save to Data Structure
            page_data = {"Page": page_num + 1, "Roll": roll, "Booklet No": booklet, "Code": code}
            for i, val in enumerate(full_ans): page_data[f"Q{i+1}"] = val
            all_results.append(page_data)

            # 5. Terminal Display
            print(f"📄 PAGE {page_num+1} | ROLL: {roll} | BOOKLET: {booklet} | CODE: {code}\n" + "-"*60)
            print("  COL 1 (1-50)  |  COL 2 (51-100) | COL 3 (101-150) | COL 4 (151-200)")
            print("-" * 60)
            for i in range(50):
                v1, v2, v3, v4 = (a1[i] if i<len(a1) else '-'), (a2[i] if i<len(a2) else '-'), (a3[i] if i<len(a3) else '-'), (a4[i] if i<len(a4) else '-')
                print(f"  {i+1:03d}: {v1}       |  {i+51:03d}: {v2}        |  {i+101:03d}: {v3}        |  {i+151:03d}: {v4}")
            print("-" * 60 + "\n")

        # 6. Excel Export
        os.makedirs(os.path.dirname(OUTPUT_EXCEL), exist_ok=True)
        pd.DataFrame(all_results).to_excel(OUTPUT_EXCEL, index=False)
        print(f"✅ SUCCESS: All results securely saved to:\n📂 {OUTPUT_EXCEL}")

    except Exception as e: print(f"❌ ERROR: {e}")

if __name__ == "__main__": main()
