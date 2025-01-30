from dataclasses import dataclass
import pandas as pd
import os


@dataclass
class Config:
    UPLOAD_FOLDER: str = "uploads"
    PAGES_FOLDER: str = "pages"
    CROPS_FOLDER: str = "crops"
    DATA_FOLDER: str = "data"
    SORTED_PDF: str = "sorted_acts.pdf"
    DATA_FILE: str = "data/all_data.csv"
    SORTED_DF: str = "data/sorted_data.csv"

    def ensure_dirs(self):
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.PAGES_FOLDER, exist_ok=True)
        os.makedirs(self.CROPS_FOLDER, exist_ok=True)
        os.makedirs(self.DATA_FOLDER, exist_ok=True)

        if not os.path.exists(self.DATA_FILE):
            pd.DataFrame(columns=["uploaded_file", "page", "object_number"]).to_csv(self.DATA_FILE, index=False)


config = Config()
config.ensure_dirs()
