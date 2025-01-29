
import pandas as pd
diction = {'A':[1, 1, 2, 2, 3, 4, 4],
           'B':[1, 1, 4, 25, 3, 8, 4],
           'C':[4, 1, 2, 2, 50, 65, 4]
           }

df = pd.DataFrame(diction)

print(df.iloc[:,0])