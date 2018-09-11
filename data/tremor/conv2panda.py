import numpy as np
import pandas as pd
import pickle

from scipy.io import loadmat

from date import matlab2ymdhms

data = loadmat('mbbp_cat_d_forHeidi')
mbbp_cat_d = data['mbbp_cat_d']
tbegin = mbbp_cat_d[:, 0]
lat = mbbp_cat_d[:, 2]
lon = mbbp_cat_d[:, 3]
depth = mbbp_cat_d[:, 4]
errlat = mbbp_cat_d[:, 5]
errlon = mbbp_cat_d[:, 6]
errdepth = mbbp_cat_d[:, 7]
nt = np.shape(mbbp_cat_d)[0]
YY = np.zeros(nt)
MM = np.zeros(nt)
DD = np.zeros(nt)
HH = np.zeros(nt)
mm = np.zeros(nt)
ss = np.zeros(nt)
for i in range(0, nt):
    (YY[i], MM[i], DD[i], HH[i], mm[i], ss[i]) = matlab2ymdhms(mbbp_cat_d[i, 0])

dataset = pd.DataFrame({'Year':YY.astype(int), 'Month':MM.astype(int), \
    'Day':DD.astype(int), 'Hour':HH.astype(int), 'Minute':mm.astype(int), \
    'Latitude':lat, 'Longitude':lon, 'Depth':depth, \
    'errLat':errlat, 'errLon':errlon, 'errDepth':errdepth})
pickle.dump([dataset], open('aghosh.pkl', 'wb'))
