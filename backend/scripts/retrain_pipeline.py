import os

os.system("python backend/scripts/export_ranking_dataset_from_db_v4.py")
os.system("python backend/scripts/train_ranker_lgbm_v2.py")

print("Retraining complete")