from music21 import converter, note, chord

# MusicXML 파일 경로 (파일명 수정 필요)
score = converter.parse("./data/La Gazza ladra Overture_완판(20250202).musicxml")
note_data = []

for i, part in enumerate(score.parts):
    part_name = part.partName if part.partName else f"Part {i+1}"
    instrument_number = i + 1

    for element in part.recurse():
        if isinstance(element, note.Note):
            note_data.append({
                "instrument_number": instrument_number,
                "instrument": part_name,
                "type": "note",
                "pitch": element.pitch.nameWithOctave,
                "offset": element.offset,
                "duration": element.duration.quarterLength,
                "measure": element.getContextByClass("Measure").number if element.getContextByClass("Measure") else None,
                "pitches": None
            })
        elif isinstance(element, chord.Chord):
            note_data.append({
                "instrument_number": instrument_number,
                "instrument": part_name,
                "type": "chord",
                "pitch": None,
                "offset": element.offset,
                "duration": element.duration.quarterLength,
                "measure": element.getContextByClass("Measure").number if element.getContextByClass("Measure") else None,
                "pitches": [p.nameWithOctave for p in element.pitches]
            })


# Pandas로 보기 좋게 출력 (선택)
import pandas as pd
df = pd.DataFrame(note_data)

# 첫 4마디만 필터링
filtered = [n for n in note_data if n["measure"] in [1, 2, 3, 4]]

# 마디별로 그룹화
from collections import defaultdict

measures = defaultdict(list)
for entry in filtered:
    measures[entry["measure"]].append(entry)

# 마디별로 출력
for measure_number in sorted(measures.keys()):
    print(f"\n🎼 Measure {measure_number}")
    for entry in measures[measure_number]:
        pitch_info = entry["pitch"] if entry["type"] == "note" else f"Chord: {entry['pitches']}"
        print(f"  ▶ {entry['instrument_number']:>2}. {entry['instrument']:<20} | {pitch_info:<10} | duration: {entry['duration']} | offset: {entry['offset']}")

exit()            
# Pandas로 보기 좋게 출력 (선택)
import pandas as pd
df = pd.DataFrame(note_data)
print(df.head(100))

exit()
for index, row in df.iterrows():
    # print one row as one row
    #print(row)
    # print one row as one row
    print(f"index: {index}, instrument_number: {row['instrument_number']}, instrument: {row['instrument']}, type: {row['type']}, pitch: {row['pitch']}, offset: {row['offset']}, measure: {row['measure']}, pitches: {row['pitches']}")
    if index > 100: 
        break
