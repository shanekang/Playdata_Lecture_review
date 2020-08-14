from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import RobustScaler
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


data = {'x1' : [13, np.nan, 17, 20, 22, 21, 11, 56, 999, 64],
        'x2' : [9, 555, 17, 11, np.nan, 10, 17, 777, 22, 34],
        'y' : [20, np.nan, 30, 27, np.nan, 32, 17, 20, 22, 899]}

df = pd.DataFrame(data)
df_0 = df.fillna(0)


scaler = StandardScaler() #기본 스케일, 평균과 표준편차 사용
scaler.fit(df_0) #fit 메서드를 실행하면 분포 모수를 객체내에 저장
X_train_1 = scaler.transform(df_0)

scaler = MinMaxScaler() #최대/최소 값이 각 각 1, 0이 되도록
scaler.fit(df_0)
X_train_2 = scaler.transform(df_0)

scaler = MaxAbsScaler() #최대절대값과 0이 각각 1,0이 되도록
scaler.fit(df_0)
X_train_3 = scaler.transform(df_0)

scaler = RobustScaler() #중앙값과 IQR(interquartile range사분범위) 사용 quartile 사분위수
scaler.fit(df_0)
X_train_4 = scaler.transform(df_0)

print(pd.DataFrame(X_train_1, columns = ["x1", "x2", "y"]))
print(pd.DataFrame(X_train_2, columns = ["x1", "x2", "y"]))
print(pd.DataFrame(X_train_3, columns = ["x1", "x2", "y"]))
print(pd.DataFrame(X_train_4, columns = ["x1", "x2", "y"]))
