
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import make_regression
from scipy.stats import spearmanr
import math
from sklearn import gaussian_process
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (RBF, Matern, RationalQuadratic,
                                              ExpSineSquared, DotProduct,
                                              ConstantKernel)



df_1 = pd.read_csv('ip_3.csv',header=0)
y = pd.read_csv('weeks.csv',header = 0)
df = df_1.transpose()
df = df[1:]
X = df

median_pred = pd.DataFrame({"patient_id": X.index})
y = pd.concat([median_pred, y], axis=1)
y['patient_id'] = y['patient_id'].astype(str)
Y = y.set_index('patient_id')
Y = Y["weeks"]
Y



X["p"] = [x.split("_")[0] for x in X.index]
y["p"] = [x.split("_")[0] for x in Y.index]



ker_rbf = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))
ker_rq = ConstantKernel(1.0, (1e-3, 1e3)) * RationalQuadratic(alpha=0.1, length_scale=1)

kernel_list = [ker_rbf, ker_rq]

param_grid = {"kernel": kernel_list,
              "alpha": [1e1],
              "optimizer": ["fmin_l_bfgs_b"],
              "n_restarts_optimizer": [10,15,20,25]}
prediction = []
i = 0
scaler = MinMaxScaler(feature_range=(0, 1))
sc = StandardScaler()


for patient in X["p"].unique():
    X_val = X.loc[X.p==patient]
    X_train = X.loc[X.p!=patient]
    y_val = Y.loc[X.p==patient]
    y_train = Y.loc[X.p!=patient]
    X_val = X_val.drop("p", axis=1)
    X_train = X_train.drop("p", axis=1)
    pred_old = pd.DataFrame({"patient_id": X_train.index})
    X_train = sc.fit_transform(X_train)
    X_val = sc.fit_transform(X_val)
    #X_train, y_train = make_regression(n_samples=len(X_train), n_features=len(X.columns)-1)
    #X_val, y_val = make_regression(n_samples=len(X_val), n_features=len(X.columns)-1)
        
    gp = GaussianProcessRegressor()
    grid_search = GridSearchCV(gp, param_grid=param_grid,cv=2)
    grid_search.fit(X_train,y_train)

    preds  = grid_search.predict(X_val)
    prediction = np.append(prediction, preds)
    i += 1
    


print("Length of prediction:",len(prediction))
print("Length of y_val:",len(y_val))
print("Prediction:",prediction)

y_true = y.sort_values("patient_id")
y_true = np.array(y_true.weeks)
y_val  = y_true



mse = mean_squared_error(y_val,prediction)
print('Mean squared error:', mse)
print('Root Mean Squared Error (testing set):',np.sqrt(mean_squared_error(y_val,prediction)))

corr, p = spearmanr(y_val, prediction)
print("Correlation:", corr)
print("P value:", p)

print( "%.16f" % float(p))

log = -(math.log10(p))
print("-Log(p_val):",log)



