import glob
import pandas as pd

class DataLoader:
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        
    def load_dataset(self):
        files = glob.glob(self.data_folder_path+"*.csv")
        data_list = []
        for file in files:
            data_list.append(pd.read_csv(file))
        return pd.concat(data_list)

if __name__==('__main__'):
    data_folder_path = "MakeDataset/ScrapingData/"
    data_loader = DataLoader(data_folder_path=data_folder_path)
    data_list = data_loader.load_dataset()
    print(data_list.head(5))