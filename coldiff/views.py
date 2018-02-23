# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.core.files.storage import FileSystemStorage
import pandas as pd
import json
import os
import mimetypes

# Create your views here.
def compare(request):
	file1data = request.FILES['file1'].read()
	file1name = request.FILES['file1'].name

	file2data = request.FILES['file2'].read()
	file2name = request.FILES['file2'].name

	newFile = open("coldiff/files/"+file1name,'wb')
	newFile.write(file1data)
	newFile.close()

	newFile = open("coldiff/files/"+file2name,'wb')
	newFile.write(file2data)
	newFile.close()

	id_col = 'Make'
	compare_col = 'Model'

	# convert the two sheets to dataframes
	xls1 = pd.ExcelFile("coldiff/files/"+file1name)
	df1 = xls1.parse(xls1.sheet_names[0])
	xls2 = pd.ExcelFile("coldiff/files/"+file2name)
	df2 = xls2.parse(xls2.sheet_names[0])

	df1 = df1[[id_col, compare_col]]
	df2 = df2[[id_col, compare_col]]
	df1 = df1.rename(columns = {compare_col: compare_col+"1"})
	df2 = df2.rename(columns = {compare_col: compare_col+"2"})

	joindf = pd.merge(df1, df2, on=id_col,how='inner')

	joindf['Match'] = (joindf[compare_col+"1"]==joindf[compare_col+"2"])
	joindf['Match'] = joindf['Match'].astype(str)
	joindf = joindf.drop_duplicates()

	writer = pd.ExcelWriter('coldiff/files/comparison.xlsx')
	joindf.to_excel(writer,'Sheet1', index=False)
	writer.save()

	with open('coldiff/files/comparison.xlsx','r') as f:
		data = f.read()

	os.remove("coldiff/files/"+file1name)
	os.remove("coldiff/files/"+file2name)

	response = HttpResponse(data, content_type=mimetypes.guess_type('coldiff/files/comparison.xlsx')[0])
	response['Content-Disposition'] = "attachment; filename={0}".format('comparison.xlsx')
	response['Content-Length'] = os.path.getsize('coldiff/files/comparison.xlsx')
	return response

def index(request):
	return render(request, 'index.html')