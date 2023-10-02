import pandas as pd

# python -c "from eco_calcs import Profit; Profit.Pharma()"
# python -c "from eco_calcs import Profit; Profit.Factories()"

class Profit:
    def Pharma(df: pd.DataFrame = pd.read_csv('tables/pharma.csv')):

        df["D_profit"] = ((df["Sale Price"] - 20 - 20) * df["Desistothium"]) - 1.2e5
        df["H_profit"] = ((df["Sale Price"] - 20 - 20) * df["Hwaleksium"]) - 1.2e5
        df["S_profit"] = ((df["Sale Price"] - 20 - 20) * df["Schwartzinium"]) - 1.2e5

        df["D_profit_oil"] = ((df["Sale Price"] - 20 - 14) * df["Desistothium"]) - 1.2e5
        df["H_profit_oil"] = ((df["Sale Price"] - 20 - 14) * df["Hwaleksium"]) - 1.2e5
        df["S_profit_oil"] = ((df["Sale Price"] - 20 - 14) * df["Schwartzinium"]) - 1.2e5

        Profit.Optimum(df.rename({"Sale Price": "Selling Price"}, axis=1))
        
    def Factories(df: pd.DataFrame = pd.read_csv('tables/factories.csv')):

        df.loc[df["Widgets Demand"] > 2e5, 'Widgets Demand'] == 2e5 # Widgets 2 iron, 1 wood
        df.loc[df["Gadgets Demand"] > 2e5, 'Gadgets Demand'] == 2e5 # Gadget 1 iron, 3 cloth

        df["W_profit"] = ((df["Selling Price"] - 20 - 30) * df["Widgets Demand"] / 2) - 1.2e5 
        df["W_profit_iron"] = ((df["Selling Price"] - 20 - 24) * df["Widgets Demand"] / 2 ) - 1.2e5
        df["W_profit_iron_wood"] = ((df["Selling Price"] - 20 - 21) * df["Widgets Demand"] / 2 ) - 1.2e5
        
        df["G_profit"] = ((df["Selling Price"] - 20 - 40) * df["Gadgets Demand"]) - 1.2e5
        df["G_profit_iron"] = ((df["Selling Price"] - 20 - 31) * df["Gadgets Demand"]) - 1.2e5 
        df["G_profit_iron_cloth"] = ((df["Selling Price"] - 20 - 28) * df["Gadgets Demand"]) - 1.2e5 

        Profit.Optimum(df)

    @staticmethod
    def Optimum(df):
        mdf = pd.DataFrame()
        for col in df.columns:
            try:
                if col.split('_')[1] == 'profit':
                    d = df[df[col] == df[col].max()][["Selling Price", col]].rename(
                            {col: 'profit'}, axis=1)
                    
                    d["config"] = col

                    mdf = pd.concat([mdf, d], axis=0)
            except:
                pass

        print(mdf.sort_values('profit', ascending=False))

