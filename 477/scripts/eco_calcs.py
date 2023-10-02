import pandas as pd


class Profit:
    def Pharma():

        df = pd.read_csv('tables/pharma.csv')
        df["D_profit"] = ((df["Sale Price"] - 20 - 20) * df["Desistothium"]) - 1.2e5
        df["H_profit"] = ((df["Sale Price"] - 20 - 20) * df["Hwaleksium"]) - 1.2e5
        df["S_profit"] = ((df["Sale Price"] - 20 - 20) * df["Schwartzinium"]) - 1.2e5

        print(df)

        print(df[df["D_profit"] == df["D_profit"].max()][["Sale Price", "D_profit"]], 
            df[df["H_profit"] == df["H_profit"].max()][["Sale Price", "H_profit"]], 
            df[df["S_profit"] == df["S_profit"].max()][["Sale Price", "S_profit"]], 
            sep='\n')
        
    def Factories():

        df = pd.read_csv('tables/factories.csv')
        print(df.dtypes) 
        # Widgets 2 iron, 1 wood
        # Gadget 1 iron, 3 cloth
        df["W_profit"] = ((df["Selling Price"] - 20 - 30) * df["Widgets Demand"]) - 1.2e5 
        df["W_profit_iron"] = ((df["Selling Price"] - 20 - 24) * df["Widgets Demand"]) - 1.2e5
        df["W_profit_iron_wood"] = ((df["Selling Price"] - 20 - 21) * df["Widgets Demand"]) - 1.2e5
        
        df["G_profit"] = ((df["Selling Price"] - 20 - 40) * df["Gadgets Demand"]) - 1.2e5
        df["G_profit_iron"] = ((df["Selling Price"] - 20 - 31) * df["Gadgets Demand"]) - 1.2e5 
        df["G_profit_iron_cloth"] = ((df["Selling Price"] - 20 - 28) * df["Gadgets Demand"]) - 1.2e5 

        print(df)

        print(df[df["W_profit"] == df["W_profit"].max()][["Sale Price", "W_profit"]], 
              df[df["G_profit"] == df["G_profit"].max()][["Sale Price", "G_profit"]], 
              sep='\n')