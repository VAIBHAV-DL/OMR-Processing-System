import cv2
import numpy as np
import os
import pandas as pd
from pdf2image import convert_from_path

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
MERGED_PDF_PATH = r"C:\Users\Vaibhav\Desktop\Mpro9\OMR_NEW\input\kcet_omr_merged.pdf"
OUTPUT_EXCEL = r"C:\Users\Vaibhav\Desktop\Mpro9\OMR_NEW\output\OMR_Results.xlsx"
POPPLER_PATH = r"C:\Users\Vaibhav\Desktop\Mpro9\OMR_NEW\poppler-25.12.0\Library\bin"

# 📍 LOCKED COORDINATES
REF_LADDER_LEFT =  [7, 450, 187, 2600]
REF_LADDER_RIGHT = [2280, 450, 159, 2600]

ROIS = {
    "roll":    (218, 600, 393, 1531),
    "version": (210, 2268, 405, 128),
    "q_1_20":  (787, 588, 362, 2330),
    "q_21_40": (1340, 592, 366, 2334),
    "q_41_60": (1902, 588, 354, 2323),
}

# 🔧 FINAL ALIGNMENT SETTINGS
SECTION_CONFIG = {
    "roll":    {'cols': 5, 'padding': 5,  'nudge': -3, 'nudge_y': 1, 'step_offset': 0.0, 'density': 2}, 
    "version": {'cols': 4, 'padding': -4, 'nudge': 3,  'nudge_y': 4, 'step_offset': 0.5, 'density': 1, 'max_rows': 1}, 
    "q_1_20":  {'cols': 4, 'padding': -1, 'nudge': 4,  'nudge_y': 5, 'step_offset': 0.0, 'density': 1}, 
    "q_21_40": {'cols': 4, 'padding': 0,  'nudge': 5,  'nudge_y': 4, 'step_offset': 0.0, 'density': 1},
    "q_41_60": {'cols': 4, 'padding': -6, 'nudge': 4,  'nudge_y': 1, 'step_offset': 0.0, 'density': 1},
}

# 🎯 TUNED SENSITIVITY
BUBBLE_RADIUS = 16        
THRESHOLD_EMPTY = 320    
THRESHOLD_VALID = 500    
LADDER_CLEAN_DIST = 35

# ==========================================
# 🔧 ENGINE TOOLS
# ==========================================

def get_ladder_marks(img, zone_coords):
    x, y, w, h = zone_coords
    if x < 0 or y < 0 or x+w > img.shape[1] or y+h > img.shape[0]: return [], 0
    crop = img[y:y+h, x:x+w]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marks_y, marks_x_centers = [], []
    for c in cnts:
        bx, by, bw, bh = cv2.boundingRect(c)
        if 40 < cv2.contourArea(c) < 2500 and 0.4 < (bw / float(bh)) < 8.0:
            marks_y.append(y + by + bh//2)
            marks_x_centers.append(x + bx + bw//2)
    xy_pairs = sorted(zip(marks_y, marks_x_centers), key=lambda p: p[0])
    sorted_ys = [p[0] for p in xy_pairs]
    clean_ys = []
    if sorted_ys:
        clean_ys.append(sorted_ys[0])
        for m in sorted_ys[1:]:
            if m - clean_ys[-1] > LADDER_CLEAN_DIST: clean_ys.append(m)
    return clean_ys, x + w//2

def get_closest_y(target_y, y_list):
    if not y_list: return target_y
    return min(y_list, key=lambda val: abs(val - target_y))

def deskew_page(img, l_ys, l_x, r_ys, r_x):
    if len(l_ys) < 2 or len(r_ys) < 2: return img
    ry_target = get_closest_y(l_ys[0], r_ys)
    angle = np.degrees(np.arctan2(ry_target - l_ys[0], r_x - l_x))
    M = cv2.getRotationMatrix2D((img.shape[1]//2, img.shape[0]//2), angle, 1.0)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderValue=(255,255,255))

def measure_bubble(thresh_img, x, y):
    mask = np.zeros(thresh_img.shape, dtype="uint8")
    cv2.circle(mask, (x, y), BUBBLE_RADIUS, 255, -1)
    return cv2.countNonZero(cv2.bitwise_and(thresh_img, thresh_img, mask=mask))

def extract_section_matrix(thresh_img, roi_coords, l_ys, l_x, r_ys, r_x, section_name):
    rx, ry, rw, rh = roi_coords
    cfg = SECTION_CONFIG.get(section_name, {})
    num_cols, nudge_x, nudge_y, padding = cfg['cols'], cfg['nudge'], cfg['nudge_y'], cfg['padding']
    step_offset, density, max_rows = cfg['step_offset'], cfg['density'], cfg.get('max_rows', 9999)

    start_x = rx + padding + nudge_x
    cell_w = (rw - (2 * padding)) / num_cols
    relevant_indices = [i for i, y in enumerate(l_ys) if (ry - 20) < y < (ry + rh + 20)]
    
    matrix_scores = []
    rows_drawn = 0
    for i, idx in enumerate(relevant_indices):
        if rows_drawn >= max_rows: break
        ly = l_ys[idx]
        ry_mark = get_closest_y(ly, r_ys)
        
        step_h = (l_ys[relevant_indices[i+1]] - ly) if i < len(relevant_indices) - 1 else 35
        sub_rows = [0.0 + step_offset] if density == 1 else [0.0, 0.5]
        
        for row_ratio in sub_rows:
            if rows_drawn >= max_rows: break
            row_y = int(ly + (step_h * row_ratio) + (ry_mark - ly) * ((rx + rw//2 - l_x) / (r_x - l_x))) + nudge_y
            matrix_scores.append([measure_bubble(thresh_img, int(start_x + (c * cell_w) + (cell_w / 2)), row_y) for c in range(num_cols)])
            rows_drawn += 1
    return matrix_scores

def resolve_roll_number(matrix):
    if not matrix: return "?????"
    res = []
    for c in range(len(matrix[0])):
        col = [matrix[r][c] for r in range(len(matrix))]
        m_val = max(col)
        res.append(chr(65 + col.index(m_val)) if c < 2 and m_val >= THRESHOLD_VALID else (str(col.index(m_val)) if m_val >= THRESHOLD_VALID else "?"))
    return "".join(res)

def resolve_version(matrix):
    if not matrix or max(matrix[0]) < THRESHOLD_VALID: return "?"
    return chr(65 + matrix[0].index(max(matrix[0])))

def resolve_answers(matrix):
    answers = []
    for scores in matrix:
        m_val = max(scores)
        if m_val >= THRESHOLD_VALID:
            if len([s for s in scores if s >= THRESHOLD_EMPTY]) > 1: answers.append("*")
            else: answers.append(chr(65 + scores.index(m_val)))
        elif m_val >= THRESHOLD_EMPTY: answers.append("*")
        else: answers.append("-")
    return answers

# ==========================================
# 🚀 MAIN
# ==========================================

def main():
    if not os.path.exists(MERGED_PDF_PATH):
        print(f"❌ File not found: {MERGED_PDF_PATH}")
        return

    all_results = []
    print("\n" + "█"*60)
    print("█  OMR EXTRACTION - PRODUCTION ENGINE")
    print(f"█  Source: {os.path.basename(MERGED_PDF_PATH)}")
    print("█" + "="*58 + "█\n")

    try:
        pages = convert_from_path(MERGED_PDF_PATH, dpi=300, poppler_path=POPPLER_PATH)
        print(f"📂 Processing {len(pages)} pages...\n")

        for page_num, page_img in enumerate(pages):
            img = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2BGR)
            l_ys, l_x = get_ladder_marks(img, REF_LADDER_LEFT)
            r_ys, r_x = get_ladder_marks(img, REF_LADDER_RIGHT)
            img_aligned = deskew_page(img, l_ys, l_x, r_ys, r_x)
            
            gray = cv2.cvtColor(img_aligned, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            l_ys_f, l_x_f = get_ladder_marks(img_aligned, REF_LADDER_LEFT)
            r_ys_f, r_x_f = get_ladder_marks(img_aligned, REF_LADDER_RIGHT)

            # Extract Data
            roll = resolve_roll_number(extract_section_matrix(thresh, ROIS["roll"], l_ys_f, l_x_f, r_ys_f, r_x_f, "roll"))
            ver = resolve_version(extract_section_matrix(thresh, ROIS["version"], l_ys_f, l_x_f, r_ys_f, r_x_f, "version"))
            a1 = resolve_answers(extract_section_matrix(thresh, ROIS["q_1_20"], l_ys_f, l_x_f, r_ys_f, r_x_f, "q_1_20"))
            a2 = resolve_answers(extract_section_matrix(thresh, ROIS["q_21_40"], l_ys_f, l_x_f, r_ys_f, r_x_f, "q_21_40"))
            a3 = resolve_answers(extract_section_matrix(thresh, ROIS["q_41_60"], l_ys_f, l_x_f, r_ys_f, r_x_f, "q_41_60"))
            
            # Prepare row for Excel
            full_answers = a1 + a2 + a3
            page_data = {"Page": page_num + 1, "Roll Number": roll, "Version Code": ver}
            for i, val in enumerate(full_answers):
                page_data[f"Q{i+1}"] = val
            
            all_results.append(page_data)

            # --- TERMINAL DISPLAY ---
            print(f"📄 PAGE {page_num + 1} | ROLL: {roll} | VERSION: {ver}")
            print("-" * 40)
            print("📝 DETECTED ANSWERS:")
            for i in range(20):
                line = ""
                # Column 1 (Q1-Q20)
                q1 = i + 1
                val1 = a1[i] if i < len(a1) else " "
                line += f"   {q1:02d}: {val1}    "
                
                # Column 2 (Q21-Q40)
                q2 = i + 21
                val2 = a2[i] if i < len(a2) else " "
                line += f"|    {q2:02d}: {val2}    "
                
                # Column 3 (Q41-Q60)
                q3 = i + 41
                val3 = a3[i] if i < len(a3) else " "
                line += f"|    {q3:02d}: {val3}"
                print(line)
            print("-" * 40 + "\n")

        # Save to Excel
        if not os.path.exists(os.path.dirname(OUTPUT_EXCEL)):
            os.makedirs(os.path.dirname(OUTPUT_EXCEL))
            
        df = pd.DataFrame(all_results)
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"✅ SUCCESS: All extracted results saved to {OUTPUT_EXCEL}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
    print("\n█  COMPLETED")
    print("█" + "="*58 + "\n")

if __name__ == "__main__":
    main()