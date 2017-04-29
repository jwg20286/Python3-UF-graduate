'''
Plotting module, check dir(Plotting) for available functions
'''
import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
import pandas as pd

import FuncLib
import Functions as func
import Utility as utl
import FreqSweep
import nmr

#=======================================================================
def sweepSingle(axis,swpdata,pltmode,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot sweep data based on input plot mode on given axis.
	This function does not create its own figure window.
	Syntax:
	-------
	line=sweepSingle(axis,swpdata,pltmode[,iter=0,fillstyle='full',markeredgewidth=0,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axis: the axis to plot into.
	swpdata: FreqSweep.FreqSweep class, has .f/.x/.y/.r attributes.
	pltmode: examples: 'fX'=>f vs x, 'xy'=>x vs y, 'rfn'=>nr vs f, 'ygy'=>gy vs gy; only f,x,y,r are acceptable axes, will plot gain corrected by adding 'g' anywhere into pltmode, will plot normalized by adding 'n' anywhere into pltmode; pltmode is case insensitive.
	iter,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legflag: show legend if true.
	legloc: legend location.
	bbox_to_anchor: legend anchor point, (0,0) is lower left of plot axis.
	legsize: legend font size.
	Returns:
	-------
	line: the plotted line's handle.
	'''
	def addgn(str,gn): #add string to 'x/y/r', will not change 'f'
		str=str.replace('x',gn+'x')
		str=str.replace('y',gn+'y')
		str=str.replace('r',gn+'r')
		return str

	pltmode=pltmode.lower() #make input case insensitive
	gflag=0
	nflag=0
	if 'g' in pltmode: #determine if gain correct plot is required
		gflag=1
	if 'n' in pltmode:
		nflag=1
	pltmode=pltmode.replace('g','')
	pltmode=pltmode.replace('n','')
	xis=pltmode[0]
	yis=pltmode[1]
	gn='g'*gflag+'n'*nflag
	xis=addgn(xis,gn)
	yis=addgn(yis,gn)

	line=axis.plot(eval('swpdata.'+xis),eval('swpdata.'+yis),color=utl.colorCode(iter%utl.lencc()),marker=utl.markerCode(iter%23),fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linestyle=utl.linestyleCode(iter%4),linewidth=linewidth,label=swpdata.filename.split('.')[0]+', %.2fmK'%swpdata.Tmm) #plot,rotates color,marker,linestyle
	axis.set_xlabel(utl.mkAxLabel(pltmode[0])) #label axes
	axis.set_ylabel(utl.mkAxLabel(pltmode[1]))
	if legflag: # determine if show legend
		axis.legend(bbox_to_anchor=bbox_to_anchor,loc=legloc,prop={'size':legsize}) #legend format: 'device_filenum, Tmm'
	axis.grid()
	return line
#=======================================================================
def sweepAll(axes,swpdata,pltmode,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot sweep data in a 'fx'+'fy'+'fr'+'xy' fashion.
	This function does not create its own figure window.
	Syntax:
	-------
	line=sweepAll(axes,swpdata,pltmode[,iter=0,fillstyle='full',markeredgewidth=0,markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axes: 2-by-2 axes matrix, dimensions beyond 0 and 1 will be ignored.
	swpdata: FreqSweep.FreqSweep class, has .f/.x/.y/.r/.gx/.gy/.gr attributes.
	pltmode: plot mode, supports 'x/y/r/all' and 'g/n'.
	iter,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns:
	--------
	line: tuple with all 4 lines' handles
	'''
	gflag=0
	nflag=0
	if 'g' in pltmode:
		gflag=1
	if 'n' in pltmode:
		nflag=1
	
	gn='g'*gflag+'n'*nflag
	mode0=gn+'fx'
	mode1=gn+'fy'
	mode2=gn+'fr'
	mode3=gn+'xy'
	line0=sweepSingle(axes[0][0],swpdata,mode0,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
	line1=sweepSingle(axes[0][1],swpdata,mode1,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	line2=sweepSingle(axes[1][0],swpdata,mode2,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	line3=sweepSingle(axes[1][1],swpdata,mode3,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	return np.array(line0+line1+line2+line3)
#=======================================================================
def sweepsAll(device,*args,logname=None,correctFunc=utl.gainCorrect,pltmode='all',figsize=(15,9),wspace=0.7,hspace=0.3,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='upper left',bbox_to_anchor=(1,1),legsize=10):
	'''
	Plots multiple curves in the same figure. When reading the data, this function uses the default correctFunc in FreqSweep.FreqSweep class object.
	Syntax:
	-------
	fig,axes,lines=sweepsAll(device,file#1,...,file#N,fold1,...,foldN,logname=log_file_path[,correctFunc=utl.gainCorrect,pltmode='all',figsize=(15,9),wspace=0.7,hspace=0.3,iter=0,fillstyle='full',markeredgewidth=0,markersize=4,linewidth=1,legloc='upper left',bbox_to_anchor=(1,1),legsize=10])
	fig,axes,lines=axes,sweepsAll(device,file#1,...,file#N,'fold'[,...][,...])
	Parameters
	----------
	device: str, device code string, e.g. 'h1m'.
	file#N: file numbers.
	fold: the fetched data will be divided by this number(s).
	logname: str, sweeps log path.
	correctFunc: frequency roll-off correcting function.
	pltmode: plot mode, supports extra 'g/n'.
	figsize,wspace,hspace,iter,fillstyle,markeredgewidth,markersize,linewidth: fig and axes settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns
	-------
	fig,axes,lines: handles, each element of the 'lines' tuple is a tuple of four 'line's from fx/fy/fr/xy plots.
	Notes:
	------
	logname is not optional.
	'''
	from FreqSweep import FreqSweep as fswp

	pltmode=pltmode.lower() #make input case insensitive
	if isinstance(args[-1],str): #construct filenums and folds lists
		filenums=args[:-1]
		folds=[float(args[-1])]*len(args) #repeat single element
	elif len(args)%2==0:
		filenums=args[:int(len(args)/2)]
		folds=args[int(len(args)/2):]
	else:
		raise TypeError('Numbers of filenums and folds do not match')
	
	fig,axes=plt.subplots(2,2,figsize=figsize)
	fig.subplots_adjust(wspace=wspace,hspace=hspace)
	
	lines=[]
	for filenum,fold in zip(filenums,folds):
		swpdata=fswp(utl.mkFilename(device,filenum),xtimes=1/fold,ytimes=1/fold,rtimes=1/fold,correctFunc=correctFunc,logname=logname)
		line=sweepAll(axes,swpdata,pltmode,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
		lines.append(line)
		iter+=1
	
	return fig,axes,lines
#=======================================================================
def nmrSingle(axis,swpdata,pltmode,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot nmr sweep data based on input plot mode on given axis.
	This function does not create its own figure window.
	Syntax:
	-------
	line=nmrSingle(axis,swpdata,pltmode[,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axis: the axis to plot into.
	swpdata: nmr.nmr class.
	pltmode: str, plot mode, examples: 'td'=time_vs_FID, 'fi'=frequency_vs_fftFIDimag... Can recognize 't/d/f/r/i/m/p', pltmode is case insensitive.
	iter,fillstyle,markeredgestyle,markersize,linewidth: axis settings.
	legflag: show legend if true.
	legloc: legend location.
	bbox_to_anchor: legend anchor point, (0,0) is lower left of plot axis.
	legsize: legend font size.
	Returns:
	-------
	line: the plotted line's handle.
	'''
	def translatePltmode(str):
		if str=='t':# Time
			str=str.replace('t','t0fill')
		elif str=='d':# free-induction-Decay
			str=str.replace('d','nmr0fill')
		elif str=='f':# Frequency
			str=str.replace('f','f0fill')
		elif str=='r':# Real part of fft
			str=str.replace('r','fftnmr0fill.real')
		elif str=='i':# Imaginary part of fft
			str=str.replace('i','fftnmr0fill.imag')
		elif str=='m':# Magnitude of fft
			str=str.replace('m','fftnmr0fill_m')
		elif str=='p':
			str=str.replace('p','fftnmr0fill_ph')
		else:
			raise TypeError('Unrecognizable input pltmode')
		return str
	
	pltmode=pltmode.lower()
	xis=translatePltmode(pltmode[0])
	yis=translatePltmode(pltmode[1])

	line=axis.plot(eval('swpdata.'+xis),eval('swpdata.'+yis),color=utl.colorCode(iter%utl.lencc()),marker=utl.markerCode(iter%23),fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linestyle=utl.linestyleCode(iter%4),linewidth=linewidth,label=swpdata.filename.split('.')[0]) #plot,rotates color,marker,linestyle
	axis.set_xlabel(utl.mkNmrAxLabel(pltmode[0])) #label axes
	axis.set_ylabel(utl.mkNmrAxLabel(pltmode[1]))
	if legflag: # determine if show legend
		axis.legend(bbox_to_anchor=bbox_to_anchor,loc=legloc,prop={'size':legsize}) #legend format: 'device_filenum'
	axis.grid()
	return line
#=======================================================================
def nmrAll(axes,swpdata,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot nmr data in a 'td'+'fr'+'fi' fashion.
	This function does not create its own figure window.
	Syntax:
	-------
	line=nmrAll(axes,swpdata[,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axes: 1x3 axes matrix, dimensions beyond 2 will be ignored.
	swpdata: nmr.nmr class.
	iter,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns:
	--------
	line: tuple with all 3 lines' handles
	'''
	line0=nmrSingle(axes[0],swpdata,'td',iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
	line1=nmrSingle(axes[1],swpdata,'fr',iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	line2=nmrSingle(axes[2],swpdata,'fi',iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	return np.array(line0+line1+line2)
#=======================================================================
def nmrsAll(*filenums,pltmode='all',tstep=2e-7,zerofillnum=0,logname='NLog_001.dat',figsize=(15,5),wspace=0.9,hspace=0.3,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='upper left',bbox_to_anchor=(1,1),legsize=10):
	'''
	Plots multiple nmr signal in the same figure.
	Syntax:
	-------
	fig,axes,lines=nmrsAll(file#1,...,file#N,[,pltmode='all',tstep=2e-7,zerofillnum=0,figsize=(15,5),wspace=0.9,hspace=0.3,iter=0,fillstyle='full',markeredgewidth=0.5,markersize=4,linewidth=1,legloc='upper left',bbox_to_anchor=(1,1),legsize=10])
	fig,axes,lines=axes,sweepsAll(device,file#1,...,file#N,[,pltmode='all',tstep=2e-7,zerofillnum=0,figsize=(15,5),wspace=0.9,hspace=0.3,markersize=4,linewidth=1,iter=0,legloc='upper left',bbox_to_anchor=(1,1),legsize=10])
	Parameters
	----------
	file#N: file numbers.
	pltmode: plot mode, supports 'all' and 't/d/f/r/i/m/p'.
	tstep,zerofillnum: nmr file reading parameters.
	logname: nmr log path.
	figsize,wspace,hspace,iter,fillstyle,markeredgewidth,markersize,linewidth: fig and axes settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns
	-------
	fig,axes,lines: handles, each element of the 'lines' tuple is a tuple of four 'line's from fx/fy/fr/xy plots.
	'''
	from nmr import nmr

	pltmode=pltmode.lower() #make input case insensitive
	
	if 'all' in pltmode:
		fig,axes=plt.subplots(1,3,figsize=figsize)
		fig.subplots_adjust(wspace=wspace,hspace=hspace)
	else:
		fig,axes=plt.subplots(1,1,figsize=figsize)
	
	lines=[]
	for filenum in filenums:
		swpdata=nmr(utl.mkFilename('NMR',filenum),tstep=tstep,zerofillnum=zerofillnum,logname=logname)
		if 'all' in pltmode:
			line=nmrAll(axes,swpdata,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
		else:
			line=nmrSingle(axes,swpdata,pltmode,iter=iter,fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
		lines.append(line)
		iter+=1
	
	return fig,axes,lines
#=======================================================================
def fitCheckSim(axes,data,fitmode,funcs1,funcs2,sharenum,popt1,popt2,res,frange=(-np.inf,np.inf),markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Check sim fitting result and plot. Assume funcs1&2 as X&Y-channels, and sqrt(x**2+y**2) as R-channel. 
	Syntax:
	-------
	lines=fitCheckSim(axes,data,fitmode,funcs1,funcs2,sharenum,popt1,popt2,res[,frange=(-inf,inf),markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	data: data with attributes f/x/y/r/gx/gy/gr
	funcs1&2: function lists 1&2.
	sharenum: number of parameters shared by funcs1&2.
	popt1&2: fitting results for funcs1&2.
	res: fitting residuals.
	frange: frequency range (low,high) bounds.
	markersize,linewidth: axes and fig settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns:
	--------
	lines: all plotted lines handles.
	Note:
	------
	When plot fitted curves, they are within frange. The terms containing the shared parameters are considered main terms, and the rest are backgrounds.
	'''
	if 'g' in fitmode:
		y1=data.gx
		y2=data.gy
		y3=data.gr
	else:
		y1=data.x
		y2=data.y
		y3=data.r
	
#	x=data.f
#	condition=(x>=frange[0])&(x<=frange[1])
#	x=x[condition]
	_,OrCond=utl.build_condition(frange,data.f)
	x=data.f[OrCond]

	model1=func.assemble(funcs1,np.ones(len(funcs1)))
	model2=func.assemble(funcs2,np.ones(len(funcs2)))
	out1=model1(x,*popt1)
	out2=model2(x,*popt2)

	n=1 #create main,bg functions, and their popt values pmain,pbg
	while func.paramsize(func.assemble(funcs1[:n],np.ones(n)))<sharenum:
		n+=1
	main1=func.assemble(funcs1[:n],np.ones(n))
	ps1=func.paramsize(main1)
	pmain1=popt1[:ps1]
	out1m=main1(x,*pmain1)
	#bg1=assemble(funcs1[n:],np.ones(len(funcs1)-n)) #can be used as an alternative tool to calculate background==out1-out1m.
	#pbg1=popt1[ps1:]

	n=1
	while func.paramsize(func.assemble(funcs2[:n],np.ones(n)))<sharenum:
		n+=1
	main2=func.assemble(funcs2[:n],np.ones(n))
	ps2=func.paramsize(main2)
	pmain2=popt2[:ps2]
	out2m=main2(x,*pmain2)
	#bg2=assemble(funcs2[n:],np.ones(len(funcs2)-n)
	#pbg2=popt2[ps2:]

	line000=axes[0][0].plot(data.f,y1,color='k',marker='.',markersize=markersize,linewidth=0,label='Data points') # data points with full range
	line001=axes[0][0].plot(x,out1,color='r',markersize=0,linestyle='-',linewidth=linewidth,label='Fit total') # fitted total with frange
	line002=axes[0][0].plot(x,out1m,color='b',markersize=0,linestyle='-.',linewidth=linewidth,label='Shared component') #main terms within frange
	line003=axes[0][0].plot(x,out1-out1m,color='g',markersize=0,linestyle='--',linewidth=linewidth,label='Background') #non-shared part is named as the background
	axes[0][0].set_xlabel('Frequency (Hz)')
	axes[0][0].set_ylabel('X-channel (Vpp)')
	axes[0][0].grid()
	axes[0][0].legend(loc=legloc,bbox_to_anchor=bbox_to_anchor,prop={'size':legsize}) #legend in X-channel

	line010=axes[0][1].plot(data.f,y2,color='k',marker='.',markersize=markersize,linewidth=0)
	line011=axes[0][1].plot(x,out2,color='r',markersize=0,linestyle='-',linewidth=linewidth)
	line012=axes[0][1].plot(x,out2m,color='b',markersize=0,linestyle='-.',linewidth=linewidth)
	line013=axes[0][1].plot(x,out2-out2m,color='g',markersize=0,linestyle='--',linewidth=linewidth)
	axes[0][1].set_xlabel('Frequency (Hz)')
	axes[0][1].set_ylabel('Y-channel (Vpp)')
	axes[0][1].grid()
	
	line100=axes[1][0].plot(data.f,y3,color='k',marker='.',markersize=markersize,linewidth=0)
	line101=axes[1][0].plot(x,np.sqrt(out1**2+out2**2),color='r',markersize=0,linestyle='-',linewidth=linewidth)
	axes[1][0].set_xlabel('Frequency (Hz)')
	axes[1][0].set_ylabel('R-channel (Vpp)')
	axes[1][0].grid()

	line110=axes[1][1].plot([x.min(),x.max()],[0,0],color='k',markersize=0,linestyle='-',linewidth=linewidth,label='Zero guideline')#0-guideline
	line111=axes[1][1].plot(np.concatenate((x,x)),res,color='r',marker='.',markersize=markersize,linewidth=0,label='Residual') #residual
	axes[1][1].set_xlabel('Frequency (Hz)')
	axes[1][1].set_ylabel('Residual (Vpp)')
	axes[1][1].grid()
	return np.array([[line000+line001+line002+line003,line010+line011+line012+line013],[line100+line101,line110+line111]])

#=======================================================================
def fitCheckSim_file(filename,filepopt,header,fitmode,funcs1,funcs2,sharenum,logname=None,ftimes=1,xtimes=1,ytimes=1,rtimes=1,correctFunc=utl.gainCorrect,frange=(-np.inf,np.inf),figsize=(12,9),wspace=0.4,hspace=0.3,markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):

	from FreqSweep import FreqSweep as fswp

	popt=utl.fswpFitLoad(filename,filepopt,header)
	data=fswp(filename,ftimes=ftimes,xtimes=xtimes,ytimes=ytimes,rtimes=rtimes,correctFunc=utl.gainCorrect,logname=logname)
	if 'g' in fitmode:
		y1=data.gx
		y2=data.gy
	else:
		y1=data.x
		y2=data.y
	
	folds1=np.ones(len(funcs1))
	folds2=np.ones(len(funcs2))
	_,OrCond=utl.build_condition(frange,data.f)
	x=data.f[OrCond]
	y1=y1[OrCond]
	y2=y2[OrCond]
	y=np.concatenate((y1,y2))
	model1=func.assemble(funcs1,folds1)
	model2=func.assemble(funcs2,folds2)
	fitmodel=func.assembleShare(model1,model2,sharenum)
	res=fitmodel(x,*popt)-y

	_,popt1,popt2=func.paramUnfold(popt,funcs1,folds1,funcs2,folds2,sharenum)
	fig,axes=plt.subplots(2,2,figsize=figsize)
	fig.subplots_adjust(wspace=wspace,hspace=hspace)
	lines=fitCheckSim(axes,data,fitmode,funcs1,funcs2,sharenum,popt1,popt2,res,frange=frange,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
	return fig,axes,lines
#=======================================================================
def fitChecknmr(axes,data,popt,marker='.',markersize=1,linewidth=1,bbox_to_anchor=(0,1),legloc='lower left',legsize=8):
	'''
	Plot nmr data. FID vs fitted FID; FFT FID vs fitted FFT FID, both real and imaginary. Zerofilling is assumed.
	Syntax:
	-------
	lines=fitChecknmr(axes,data,popt[,marker='.',markersize=1,linewidth=1,bbox_to_anchor=(0,1),legloc='lower left',legsize=8])
	Parameters:
	-----------
	axes: 1x3 subplots axes to plot onto.
	data: nmr signal data.
	popt: Fitted parameters describing the FFT FID peaks.
	marker,markersize,linewidth: Fitted curve plot settings.
	bbox_to_anchor,lfilenmr.egloc,legsize: legend position and size.
	Returns:
	--------
	lines: matrix, lines[0][0]=raw FID data, lines[0][1]=fitted FID data; lines[1][0]=raw FFT real, lines[1][1]=fit to the smoothed FFT real; lines[2][0]=raw FFT imag, lines[2][1]=fit to the smoothed FFT imag.
	Note:
	-----
	marker,markersize,linewidth do not affact raw data plot or smoothed data plot, but only the fitted curves.
	'''
	def newr(f,*p):
		return FuncLib.FID0ffts(f,*p,zerofillnum=data.zerofillnum).real
	def newi(f,*p):
		return FuncLib.FID0ffts(f,*p,zerofillnum=data.zerofillnum).imag
	newFID=FuncLib.FID0s(data.t,*popt,zerofillnum=data.zerofillnum)
	newFFTr=newr(data.f,*popt)
	newFFTi=newi(data.f,*popt)

	line00=axes[0].plot(data.t0fill,data.nmr0fill,marker='.',markersize=1,linewidth=1,color='blue',label=data.filename) #show FID, label with filename
	line01=axes[0].plot(data.t0fill,newFID,marker=marker,markersize=markersize,linewidth=0,color='red') #show fitted FID
	axes[0].set_xlabel('Time (s)')
	axes[0].set_ylabel('FID Amplitude (a.u.)')
	axes[0].ticklabel_format(axis='x',style='sci',scilimits=(0,0))
	axes[0].legend(bbox_to_anchor=bbox_to_anchor,loc=legloc,prop={'size':legsize}) #legend

	line10=axes[1].plot(data.f0fill,data.fftnmr0fill.real,marker='.',markersize=1,linewidth=2,color='blue') #show FFT FID real part
	line11=axes[1].plot(data.f0fill,newFFTr,marker=marker,markersize=markersize,linewidth=linewidth,color='red') #show fited FFT FID real part
	axes[1].set_xlabel('Frequency (Hz)')
	axes[1].set_ylabel('FFT Real (a.u.)')
	axes[1].ticklabel_format(axis='x',style='sci',scilimits=(0,0))

	line20=axes[2].plot(data.f0fill,data.fftnmr0fill.imag,marker='.',markersize=1,linewidth=2,color='blue') #show FFT FID imag part
	line21=axes[2].plot(data.f0fill,newFFTi,marker=marker,markersize=markersize,linewidth=linewidth,color='red') #show fitted FFT FID imag part
	axes[2].set_xlabel('Frequency (Hz)')
	axes[2].set_ylabel('FFT Imaginary (a.u.)')
	axes[2].ticklabel_format(axis='x',style='sci',scilimits=(0,0))
	return np.array([line00+line01,line10+line11,line20+line21])
#=======================================================================
def fitChecknmr_file(filenmr,filepopt,tstep=2e-7,figsize=(16,5),wspace=0.4,hspace=0.2,marker='.',markersize=1,linewidth=1,bbox_to_anchor=(0,1),legloc='lower left',legsize=8):
	'''
	Check NMR fit by reading fitted parameters from saved file.
	Syntax:
	-------
	fig,axes,lines=fitChecknmr_file(filenmr,filepopt[,tstep=2e-7,figsize=(16,5),wspace=0.4,hspace=0.2,marker='.',markersize=1,linewidth=1,bbox_to_anchor=(0,1),legloc='lower left',legsize=8])
	Parameters:
	-----------
	filenmr: str, NMR file name.
	filepopt: str, saved file of optimized parameters, assumed whitespace as delimiter.
	tstep: NMR FID reading parameter.
	figsize,wspace,hspace: figure layout.
	marker,markersize,linewidth: line settings.
	bbox_to_anchor,legloc,legsize: legend settings.
	Returns:
	--------
	fig: figure handle.
	axes: 1x3 subplots axes to plot onto.
	lines: plotted lines handles.
	'''
	from nmr import nmr

	popt,_,zerofillnum=utl.nmrFitLoad(filenmr,filepopt)
	data=nmr(filenmr,tstep=tstep,zerofillnum=zerofillnum)
	
	fig,axes=plt.subplots(1,3,figsize=figsize)
	fig.subplots_adjust(wspace=wspace,hspace=hspace)
	lines=fitChecknmr(axes,data,popt,marker=marker,markersize=markersize,linewidth=linewidth,bbox_to_anchor=bbox_to_anchor,legloc=legloc,legsize=legsize)
	return fig,axes,lines
#=======================================================================
def sweep_single(axis,swpdata,pltmode,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0.5,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Single sweep plot function designed for sweep.py->singleSweep.
	Plot sweep data based on input plot mode on given axis.
	This function does not create its own figure window.
	Syntax:
	-------
	line=sweep_single(axis,swpdata,pltmode[,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0,markersize=4,linewidth=1,legflag=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axis: the axis to plot into.
	swpdata: sweep.singleSweep class, has .f/.x/.y/.r attributes.
	pltmode: examples: 'fX'=>f vs x, 'xy'=>x vs y, 'rfn'=>nr vs f, 'ygy'=>gy vs gy; only f,x,y,r are acceptable axes, will plot gain corrected by adding 'g' anywhere into pltmode, will plot normalized by adding 'n' anywhere into pltmode; pltmode is case insensitive.
	iter_color/marker/linestyle,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legflag: show legend if true.
	legloc: legend location.
	bbox_to_anchor: legend anchor point, (0,0) is lower left of plot axis.
	legsize: legend font size.
	Returns:
	-------
	line: the plotted line's handle.
	'''
	def addgn(str,gn): #add string to 'x/y/r', will not change 'f'
		str=str.replace('x',gn+'x')
		str=str.replace('y',gn+'y')
		str=str.replace('r',gn+'r')
		return str

	pltmode=pltmode.lower() #make input case insensitive
	gflag=0
	nflag=0
	if 'g' in pltmode: #determine if gain correct plot is required
		gflag=1
	if 'n' in pltmode:
		nflag=1
	pltmode=pltmode.replace('g','')
	pltmode=pltmode.replace('n','')
	xis=pltmode[0]
	yis=pltmode[1]
	gn='g'*gflag+'n'*nflag
	xis=addgn(xis,gn) # found what to use as x
	yis=addgn(yis,gn) # found what to use as y

	line=axis.plot(getattr(swpdata,xis).values,getattr(swpdata,yis).values,color=utl.colorCode(iter_color%utl.lencc()),marker=utl.markerCode(iter_marker%23),fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linestyle=utl.linestyleCode(iter_linestyle%4),linewidth=linewidth,label=swpdata._filename.split('.')[0]) #plot,rotates color,marker,linestyle
	axis.set_xlabel(utl.mkAxLabel(pltmode[0])) #label axes
	axis.set_ylabel(utl.mkAxLabel(pltmode[1]))
	if legflag: # determine if show legend.
		axis.legend(bbox_to_anchor=bbox_to_anchor,loc=legloc,prop={'size':legsize}) #legend format: 'device_filenum'
	axis.grid()
	return line
#=======================================================================
def sweep_multiple(axis,swpdata,pltmodes,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0.5,markersize=4,linewidth=1,legflag=True,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot one or more plots in one figure by calling sweep_single multiple times.
	Syntax:
	-------
	lines=sweep_multiple(axis,swpdata,pltmodes,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0.5,markersize=4,linewidth=1,legflag=True,legloc='lower left',bbox_to_anchor=(0,1),legsize=10)
	Parameters:
	-----------
	axis: single matplotlib.axes._subplots.AxesSubplot or list or numpy.ndarray, allowed inputs are one axis, or a list/matrix of axes.
	pltmode: str or list_of_str, plot modes.
	iter_color/marker/linestyle,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legflag: boolean, show legend if True.
	legloc: str, legend location.
	bbox_to_anchor: legend anchor point, (0,0) is lower left of plot axis.
	legsize: legend font size.
	Returns:
	--------
	line: list, list of the plotted lines' handles.
	'''
	def addgn(str,gn): #add string to 'x/y/r', will not change 'f'
		str=str.replace('x',gn+'x')
		str=str.replace('y',gn+'y')
		str=str.replace('r',gn+'r')
		return str
	
	def decode_pltmode(pltmode): #found what to use ax x and y
		pltmode=pltmode.lower() #case insensitive input
		gflag=0
		nflag=0
		if 'g' in pltmode: #determine if gain correct plot is required
			gflag=1
		if 'n' in pltmode:
			nflag=1
		pltmode=pltmode.replace('g','')
		pltmode=pltmode.replace('n','')
		xis=pltmode[0]
		yis=pltmode[1]
		gn='g'*gflag+'n'*nflag
		xis=addgn(xis,gn) # found what to use as x
		yis=addgn(yis,gn) # found what to use as y
		return pltmode, xis, yis
	
	axis=np.asarray(axis)
	axis=axis.flatten(order='C') # 'C' means flatten to row like

	if not isinstance(pltmodes,list or tuple):
		pltmodes=[pltmodes] # make sure pltmodes is a list
	
	#three lists with 'gn' removed
	pm_list=[]
	xis_list=[]
	yis_list=[]
	for pltmode in pltmodes:
		pltmode, xis,yis=decode_pltmode(pltmode)
		pm_list.append(pltmode) # pm_list contains no 'g' or 'n'
		xis_list.append(xis)
		yis_list.append(yis)
	
	lines=[]
	for i in range(0,len(pltmodes)):
		line=axis[i].plot(getattr(swpdata,xis_list[i]).values,getattr(swpdata,yis_list[i]).values,color=utl.colorCode(iter_color%utl.lencc()),marker=utl.markerCode(iter_marker%23),fillstyle=fillstyle,markeredgewidth=markeredgewidth,markersize=markersize,linestyle=utl.linestyleCode(iter_linestyle%4),linewidth=linewidth,label=swpdata._filename.split('.')[0]) #plot,rotates color,marker,linestyle
		axis[i].set_xlabel(utl.mkAxLabel(pm_list[i][0])) #label axes
		axis[i].set_ylabel(utl.mkAxLabel(pm_list[i][1]))
		if legflag: # determine if show legend
			axis[i].legend(bbox_to_anchor=bbox_to_anchor,loc=legloc,prop={'size':legsize}) #legend format: 'device_filenum'
			legflag=False # only show legend once
		axis[i].grid()
		lines.append(line)

	return lines
#=======================================================================
def sweep_all(axes,swpdata,pltmode,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0.5,markersize=4,linewidth=1,legflag=True,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Plot sweep data in a 'fx'+'fy'+'fr'+'xy' fashion.
	This function does not create its own figure window.
	Syntax:
	-------
	line=sweep_all(axes,swpdata,pltmode[,iter_color=0,iter_marker=0,iter_linestyle=0,fillstyle='full',markeredgewidth=0,markersize=4,linewidth=1,legflag=True,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	axes: 2-by-2 axes matrix, dimensions beyond 0 and 1 will be ignored.
	swpdata: sweep.sweepSingle class, has .f/.x/.y/.r/.gx/.gy/.gr attributes.
	pltmode: plot mode, supports 'x/y/r/all' and 'g/n'.
	iter_color/marker/linestyle,fillstyle,markeredgewidth,markersize,linewidth: axis settings.
	legflag: show legend if True.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns:
	--------
	line: tuple with all 4 lines' handles
	'''
	gflag=0
	nflag=0
	if 'g' in pltmode:
		gflag=1
	if 'n' in pltmode:
		nflag=1
	
	gn='g'*gflag+'n'*nflag
	mode0=gn+'fx'
	mode1=gn+'fy'
	mode2=gn+'fr'
	mode3=gn+'xy'

	lines=sweep_multiple(axes,swpdata,[mode0,mode1,mode2,mode3],fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=legflag,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
	#line0=sweep_single(axes[0][0],swpdata,mode0,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
	#line1=sweep_single(axes[0][1],swpdata,mode1,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	#line2=sweep_single(axes[1][0],swpdata,mode2,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	#line3=sweep_single(axes[1][1],swpdata,mode3,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=0)
	#return np.array(line0+line1+line2+line3)
	return lines
#=======================================================================
def sweeps_multiple(device,*args,logname=None,correctFunc=utl.gainCorrect,normByParam='VLowVpp',pltmode='all',subplots_layout=None,figsize=(15,9),wspace=0.7,hspace=0.3,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0.5,markersize=4,linewidth=1,legflag=True,legloc='upper left',bbox_to_anchor=(1,1),legsize=10):
	'''
	Plots multiple curves in the same figure. When reading the data, this function uses the default correctFunc in FreqSweep.FreqSweep class object.
	Syntax:
	-------
	fig,axes,lines=sweeps_multiple(device,file#1,...,file#N,fold1,...,foldN,logname=log_file_path[,correctFunc=utl.gainCorrect,normByParam='VLowVpp',pltmode='all',subplots_layout=None,figsize=(15,9),wspace=0.7,hspace=0.3,fillstyle='full',iter_color=0,iter_marker=0,iter_linestyle=0,markeredgewidth=0,markersize=4,linewidth=1,legflag=True,legloc='upper left',bbox_to_anchor=(1,1),legsize=10])
	fig,axes,lines=axes,sweeps_multiple(device,file#1,...,file#N,'fold'[,...])
	Parameters
	----------
	device: str, device code string, e.g. 'h1m'.
	file#N: file numbers.
	fold: the fetched data will be divided by this number(s).
	logname: str, sweeps log path.
	correctFunc: frequency roll-off correcting function.
	pltmode: plot mode, supports extra 'g/n'.
	subplots_layout: 1x2 tuple, matplotlib.subplots row & column numbers.
	figsize,wspace,hspace,iter,fillstyle,markeredgewidth,markersize,linewidth: fig and axes settings.
	legflag: boolean, show legend if True.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns
	-------
	fig,axes,lines: handles, each element of the 'lines' tuple is a tuple of four 'line's from fx/fy/fr/xy plots.
	'''
	from sweep import singleSweep as sswp

	#pltmode=pltmode.lower() #make input case insensitive
	if isinstance(args[-1],str): #construct filenums and folds lists
		filenums=args[:-1]
		folds=[float(args[-1])]*len(args) #repeat single element
	elif len(args)%2==0:
		filenums=args[:int(len(args)/2)]
		folds=args[int(len(args)/2):]
	else:
		raise TypeError('Numbers of filenums and folds do not match')
	
	#fig,axes=plt.subplots(2,2,figsize=figsize)
	#fig.subplots_adjust(wspace=wspace,hspace=hspace)
	if subplots_layout is not None:
		fig,axes=plt.subplots(subplots_layout[0],subplots_layout[1],figsize=figsize)
	elif 'all' not in pltmode:
		if not isinstance(pltmode,list or tuple):
			pltmode=[pltmode]
		fig,axes=plt.subplots(1,len(pltmode),figsize=figsize)
	else:
		fig,axes=plt.subplots(2,2,figsize=figsize)

	fig.subplots_adjust(wspace=wspace,hspace=hspace)

	lines=[]
	for filenum,fold in zip(filenums,folds):
		swpdata=sswp(utl.mkFilename(device,filenum),fold={'x':fold,'y':fold,'r':fold},correctFunc=correctFunc,logname=logname,normByParam=normByParam)
		if 'all' in pltmode:
			line=sweep_all(axes,swpdata,pltmode,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=legflag,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
		else:
			line=sweep_multiple(axes,swpdata,pltmode,fillstyle=fillstyle,iter_color=iter_color,iter_marker=iter_marker,iter_linestyle=iter_linestyle,markeredgewidth=markeredgewidth,markersize=markersize,linewidth=linewidth,legflag=legflag,legloc=legloc,bbox_to_anchor=bbox_to_anchor,legsize=legsize)
		lines.append(line)
		iter_color+=1
		iter_marker+=1
		iter_linestyle+=1
	
	return fig,axes,lines
#=======================================================================
def fitCheck_1sim(axes,data,fitmode,funcs1,funcs2,sharenum,popt1,popt2,res,frange=(-np.inf,np.inf),markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10):
	'''
	Check sim fitting result and plot. Assume funcs1&2 as X&Y-channels, and sqrt(x**2+y**2) as R-channel. 
	Syntax:
	-------
	lines=fitCheckSim(axes,data,fitmode,funcs1,funcs2,sharenum,popt1,popt2,res[,frange=(-inf,inf),markersize=4,linewidth=1,legloc='lower left',bbox_to_anchor=(0,1),legsize=10])
	Parameters:
	-----------
	data: data with attributes f/x/y/r/gx/gy/gr
	funcs1&2: function lists 1&2.
	sharenum: number of parameters shared by funcs1&2.
	popt1&2: fitting results for funcs1&2.
	res: fitting residuals.
	frange: frequency range (low,high) bounds.
	markersize,linewidth: axes and fig settings.
	legloc: legend location.
	bbox_to_anchor: legend anchor point.
	legsize: legend font size.
	Returns:
	--------
	lines: all plotted lines handles.
	Note:
	------
	When plot fitted curves, they are within frange. The terms containing the shared parameters are considered main terms, and the rest are backgrounds.
	'''
	if 'g' in fitmode:
		y1=data.gx.values
		y2=data.gy.values
		y3=data.gr.values
	else:
		y1=data.x.values
		y2=data.y.values
		y3=data.r.values
	
	_,OrCond=utl.build_condition_series(frange,data.f)
	x=data.f[OrCond].values

	model1=func.assemble(funcs1,np.ones(len(funcs1)))
	model2=func.assemble(funcs2,np.ones(len(funcs2)))
	out1=model1(x,*popt1)
	out2=model2(x,*popt2)

	n=1 #create main,bg functions, and their popt values pmain,pbg
	while func.paramsize(func.assemble(funcs1[:n],np.ones(n)))<sharenum:
		n+=1
	main1=func.assemble(funcs1[:n],np.ones(n))
	ps1=func.paramsize(main1) #param size of main1
	pmain1=popt1[:ps1] # param main 1
	out1m=main1(x,*pmain1)
	#bg1=assemble(funcs1[n:],np.ones(len(funcs1)-n)) #can be used as an alternative tool to calculate background==out1-out1m.
	#pbg1=popt1[ps1:]

	n=1
	while func.paramsize(func.assemble(funcs2[:n],np.ones(n)))<sharenum:
		n+=1
	main2=func.assemble(funcs2[:n],np.ones(n))
	ps2=func.paramsize(main2)
	pmain2=popt2[:ps2]
	out2m=main2(x,*pmain2)
	#bg2=assemble(funcs2[n:],np.ones(len(funcs2)-n)
	#pbg2=popt2[ps2:]

	line000=axes[0][0].plot(data.f.values,y1,color='k',marker='.',markersize=markersize,linewidth=0,label='Data points') # data points with full range
	line001=axes[0][0].plot(x,out1,color='r',markersize=0,linestyle='-',linewidth=linewidth,label='Fit total') # fitted total with frange
	line002=axes[0][0].plot(x,out1m,color='b',markersize=0,linestyle='-.',linewidth=linewidth,label='Shared component') #main terms within frange
	line003=axes[0][0].plot(x,out1-out1m,color='g',markersize=0,linestyle='--',linewidth=linewidth,label='Background') #non-shared part is named as the background
	axes[0][0].set_xlabel('Frequency (Hz)')
	axes[0][0].set_ylabel('X-channel (Vpp)')
	axes[0][0].grid()
	axes[0][0].legend(loc=legloc,bbox_to_anchor=bbox_to_anchor,prop={'size':legsize}) #legend in X-channel

	line010=axes[0][1].plot(data.f.values,y2,color='k',marker='.',markersize=markersize,linewidth=0)
	line011=axes[0][1].plot(x,out2,color='r',markersize=0,linestyle='-',linewidth=linewidth)
	line012=axes[0][1].plot(x,out2m,color='b',markersize=0,linestyle='-.',linewidth=linewidth)
	line013=axes[0][1].plot(x,out2-out2m,color='g',markersize=0,linestyle='--',linewidth=linewidth)
	axes[0][1].set_xlabel('Frequency (Hz)')
	axes[0][1].set_ylabel('Y-channel (Vpp)')
	axes[0][1].grid()
	
	line100=axes[1][0].plot(data.f.values,y3,color='k',marker='.',markersize=markersize,linewidth=0)
	line101=axes[1][0].plot(x,np.sqrt(out1**2+out2**2),color='r',markersize=0,linestyle='-',linewidth=linewidth)
	axes[1][0].set_xlabel('Frequency (Hz)')
	axes[1][0].set_ylabel('R-channel (Vpp)')
	axes[1][0].grid()

	line110=axes[1][1].plot([x.min(),x.max()],[0,0],color='k',markersize=0,linestyle='-',linewidth=linewidth,label='Zero guideline')#0-guideline
	line111=axes[1][1].plot(np.concatenate((x,x)),res,color='r',marker='.',markersize=markersize,linewidth=0,label='Residual') #residual
	axes[1][1].set_xlabel('Frequency (Hz)')
	axes[1][1].set_ylabel('Residual (Vpp)')
	axes[1][1].grid()
	return np.array([[line000+line001+line002+line003,line010+line011+line012+line013],[line100+line101,line110+line111]])
#=======================================================================

