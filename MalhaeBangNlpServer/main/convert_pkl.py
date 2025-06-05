import pickle
import glob
import os

# pkl 파일 목록 가져오기
pkl_files = sorted(glob.glob("main/embedding_vectors_part*.pkl"))
print(f"🔍 총 {len(pkl_files)}개의 pkl 파일 발견됨")

# 각 파일을 다시 저장
for pkl_file in pkl_files:
    print(f"🔄 {pkl_file} 변환 중...")
    
    # 파일 읽기
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    
    # 새 파일명 생성
    new_file = pkl_file.replace('.pkl', '_new.pkl')
    
    # 다시 저장
    with open(new_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"✅ {new_file} 저장 완료!")

print("🎉 모든 파일 변환 완료!") 