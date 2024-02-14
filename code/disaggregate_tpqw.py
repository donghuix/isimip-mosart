from scipy import interpolate
import numpy as np

def disaggregate_tpqw(tday,temp,tmax,tmin,pres,huss,wind,hmax,hmin,tsub):
	numd         = len(tday)
	tintp        = np.empty(((numd+1)*2,))
	tempintp     = np.empty(((numd+1)*2,))
	tintp[0]     = tsub[0]
	tintp[-1]    = tsub[-1]
	tempintp[0]  = temp[0]
	tempintp[-1] = temp[-1]

	if hmin == 0 or hmax == 0:
		if hmin < hmax:
			ll = hmax - hmin
			hmin = 1
			hmax = 1 + ll
		elif hmin > hmax:
			ll = hmin - hmax
			hmax = 1
			hmin = 1 + ll
	
	if hmin == 7 or hmax == 7:
		if hmin < hmax:
			ll = hmax - hmin
			hmax = 6
			hmin = 6 - ll
		elif hmin > hmax:
			ll = hmin - hmax
			hmin = 6
			hmax = 6 - ll

	for i in range(numd):
		if hmax > hmin:
			tintp[2*i + 1]    = tsub[i*8 + hmin] 
			tintp[2*i + 2]    = tsub[i*8 + hmax] 
			tempintp[2*i + 1] = tmin[i]
			tempintp[2*i + 2] = tmax[i]

		else:
			tintp[2*i + 1]    = tsub[i*8 + hmax] 
			tintp[2*i + 2]    = tsub[i*8 + hmin] 
			tempintp[2*i + 1] = tmax[i]
			tempintp[2*i + 2] = tmin[i]

	f1      = interpolate.PchipInterpolator(tintp, tempintp, axis=0, extrapolate=None)
	temp3hr = f1(tsub)
	f2      = interpolate.interp1d(tday,pres,kind='nearest',fill_value="extrapolate",axis=0)
	pres3hr = f2(tsub)
	f3      = interpolate.interp1d(tday,huss,kind='nearest',fill_value="extrapolate",axis=0)
	huss3hr = f3(tsub)
	f4      = interpolate.interp1d(tday,wind,kind='nearest',fill_value="extrapolate",axis=0)
	wind3hr = f4(tsub)

	return temp3hr, pres3hr, huss3hr, wind3hr