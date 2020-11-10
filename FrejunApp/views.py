import pickle
import os
import re
import io
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import reverse, redirect, render
from django.http.response import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
import pandas as pd
from pathlib import Path

import requests
import xml.etree.ElementTree as ET


from FrejunApp import Google
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django_google.flow import DjangoFlow, CLIENT_SECRET_FILE, SCOPES
from django_google.models import GoogleAuth

from .models import Candidate
from .serializers import DataSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


BASE_DIR = Path(__file__).resolve().parent.parent

SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'FrejunApp/Client_Secret.json')
API_NAME = 'drive'
API_VERSION = 'v3'
# Create your views here.
path = os.path.join(BASE_DIR, 'FrejunApp/static/FrejunApp/csvfiles/')


class List(APIView):

    def get(self, request):
        d1 = Candidate.objects.all()
        serializer = DataSerializer(d1, many=True)
        return Response(serializer.data)

    def post(self):
        pass


def home(request):
    return render(request, 'FrejunApp/index.html')


def saveModel(request):
    if request.method == "POST":
        file_name = request.POST['filen']
        status = []
        mob = []
        res = Candidate.objects.filter(filename=file_name)
        for r in res:
            mob.append(r.phone_number)
        for m in mob:
            status.append(checkStatus(m))
            # Updating the status field in model.
            Candidate.objects.filter(phone_number=m).update(status=status[-1])

        name2 = []
        mob2 = []
        status2 = []
        result = Candidate.objects.filter(filename=file_name)
        for r in result:
            name2.append(r.name)
            mob2.append(r.phone_number)
            status2.append(r.status)

        context = {'name': name2, 'mob': mob2, 'status': status2}
        # print(mob, status)
        return render(request, 'FrejunApp/result.html', context)


# def googleAPI(request):
#     return render(request, 'FrejunApp/drive.html')


# def download(request):
#     pass


# def handleUrl(request):
#     pass
#     if request.method == "POST":
#         service = Google.Create_Service(
#             CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
#         # print(dir(service))

#         file_id = request.POST['dfileid']
#         file_name = request.POST['dfilename']
#         request2 = service.files().get_media(fileId=file_id)
#         fh = io.BytesIO()
#         downloader = MediaIoBaseDownload(fh, request2)
#         done = False
#         while done is False:
#             status, done = downloader.next_chunk()
#             print("Download %d%%." % int(status.progress() * 100))

#         fh.seek(0)
#         destination = os.path.join(
#             BASE_DIR, f'FrejunApp/static/FrejunApp/csvfiles/{file_name}')
#         with open(destination, 'wb') as f:
#             f.write(fh.read())
#             f.close()

#         df = pd.read_csv(destination)

#         mobpatt = re.compile(
#             r'\b(mobile\sn.*|contact\sn.*|telephone\sn.*|phone\sn.*)\b', flags=re.I)
#         namepatt = re.compile(
#             r'\b(candidate\sn.*|full\sn.*|name)\b', flags=re.I)
#         mob = []
#         name = []

#         for i in df.columns:  # for every column i am checking for column name with matching pattern
#             if re.search(mobpatt, i):  # pattern matching happening here
#                 # if column name matched the pattern then i converting that column to list
#                 mob = df[i].to_list()

#         for i in df.columns:
#             if re.search(namepatt, i):
#                 # if column name matched the pattern then i converting that column to list
#                 name = df[i].to_list()

#         status = []
#         # resDict = {}
#         for m in mob:
#             status.append(checkStatus(m))
#         # status.append(checkStatus(m))
#         context = {'name': name, 'mob': mob, 'status': status, 'len': len(mob)}
#         # print(mob, status)
#         return render(request, 'FrejunApp/result.html', context)


def csvHandler(request):
    if request.method == "POST":
        if request.POST['dfileid'] and request.POST['dfilename']:
            service = Google.Create_Service(
                CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
        # print(dir(service))
            # Candidate.objects.all().delete()     #Deletes record every time when new file comes
            file_id = request.POST['dfileid']
            file_name = request.POST['dfilename']
            request2 = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request2)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

            fh.seek(0)
            destination = os.path.join(
                BASE_DIR, f'FrejunApp/static/FrejunApp/csvfiles/{file_name}')
            with open(destination, 'wb') as f:
                f.write(fh.read())
                f.close()

        elif request.FILES['upload']:
            Candidate.objects.all().delete()
            csvfile = request.FILES['upload']
            fs = FileSystemStorage()
            file_name = csvfile.name
            filepath = os.path.join(settings.MEDIA_ROOT, file_name)
            if os.path.exists(filepath):
                os.remove(filepath)

            fs.save(csvfile.name, csvfile)
            destination = path+file_name

        df = pd.read_csv(destination)

        mobpatt = re.compile(
            r'\b(mobile\sn.*|contact\sn.*|telephone\sn.*|phone\sn.*)\b', flags=re.I)
        namepatt = re.compile(
            r'\b(candidate\sn.*|full\sn.*|name)\b', flags=re.I)
        mob = []
        name = []

        for i in df.columns:  # for every column i am checking for column name with matching pattern
            if re.search(mobpatt, i):  # pattern matching happening here
                # if column name matched the pattern then i converting that column to list
                mob = df[i].to_list()

        for i in df.columns:
            if re.search(namepatt, i):
                # if column name matched the pattern then i converting that column to list
                name = df[i].to_list()

        # Saving name,mobile of csv file in model.
        for i in range(len(mob)):
            candidate = Candidate(filename=file_name,
                                  name=name[i], phone_number=mob[i])
            candidate.save()

        return render(request, 'FrejunApp/apicall.html', {'filename': file_name})


def saveStatus(request):
    pass


def checkStatus(mobile):
    if re.search(r'(^(((\+){1}91)|(91)){1}[1-9]{1}[0-9]{9}$)|(^[1-9]{1}[0-9]{9}$)', str(mobile)):
        res = requests.get(
            'https://kookoo.in/outbound/checkdnd.php?phone_no='+str(mobile)+'')

        xmltext = res.content
        xmltext = xmltext.decode('utf-8')
        root = ET.fromstring(xmltext)
        status = root[1].text
    else:
        status = "Invalid"
    return status
