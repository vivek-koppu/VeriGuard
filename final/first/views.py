import io
from django.http import HttpResponse
from django.shortcuts import render
import pickle
from urllib.parse import urlparse, urlunparse
import requests
import validators
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

model = pickle.load(open('./models/phishing.pkl', 'rb'))

model1 = pickle.load(open('./models/fake_profile.pkl', 'rb'))

def home(request):
    return render(request,'home.html')

def main(request):
    input1 = request.POST.get('purlVal')
    input2 = request.POST.get('ppicVal')
    input3 = request.POST.get('lnameVal')
    input4 = request.POST.get('ldescVal')
    input5 = request.POST.get('eurlVal')
    input6 = request.POST.get('ppriVal')
    input7 = request.POST.get('cpostVal')
    input8 = request.POST.get('cfolVal')
    input9 = request.POST.get('cfolloVal')
    context = {'input1':input1,'input2':input2,'input3':input3,'input4':input4,'input5':input5,'input6':input6,'input7':input7,'input8':input8,'input9':input9}
    return render(request,'main.html',context)

def app(request):
    inp = request.POST.get('aadhaarVal')
    context = {'input':inp}
    return render(request,'app.html',context)

def index(request):
    inp = request.POST.get('urlVal')
    context = {'input':inp}
    return render(request,'index.html',context)

def check_url(url):
    flag = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            flag = 1
        else:
            flag = 0

    except ConnectionError as e:
        flag = 0
    
    except RequestException as e:
        flag = 0

    return flag

def remove_all_parameters(url):
    parsed_url = urlparse(url)
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        '',
        '',
        parsed_url.fragment
    ))
    return new_url


def predictURL(request):
    if request.method == 'POST':
        r = request.POST.get('urlVal')
        s = remove_all_parameters(r)
        l = check_url(s)
    result = model.predict([s])
    if l == 1 and validators.url(s) or result == 'good':
        ou = 'Real'
    else:
        ou = 'The given URL is Fake'
    context = {'output':ou,'input':r}
    return render(request,'index.html',context)

def label_encoding(df):
  label_encoding = {'Yes': 1, 'No': 0}
  df.loc[:, 'profile_pic'] = df.loc[:, 'profile_pic'].replace(label_encoding)
  df.loc[:, 'extern_url'] = df.loc[:, 'extern_url'].replace(label_encoding)
  df.loc[:, 'private'] = df.loc[:, 'private'].replace(label_encoding)
  return df

def predictfake(request):
    if request.method == 'POST':
        input1 = request.POST.get('purlVal')
        input2 = request.POST.get('ppicVal')
        input3 = request.POST.get('lnameVal')
        input4 = request.POST.get('ldescVal')
        input5 = request.POST.get('eurlVal')
        input6 = request.POST.get('ppriVal')
        input7 = request.POST.get('cpostVal')
        input8 = request.POST.get('cfolVal')
        input9 = request.POST.get('cfolloVal')
    validation = validators.url(input1)
    columns = ['profile_pic', 'len_fullname', 'len_desc',
       'extern_url', 'private', 'num_posts', 'num_followers', 'num_following']
    data = [[str(input2).capitalize(),int(input3),int(input4),str(input5).capitalize(),str(input6).capitalize(),int(input7),int(input8),int(input9)]]
    new_df = pd.DataFrame(data, columns=columns)
    new_df = label_encoding(new_df)
    prediction = model1.predict(new_df)
    if validation:
        if prediction[0] == 0:
            output = 'Real'
        else:
            output = 'The given profile is Fake'
    else:
        output = 'Please once check the given profile URL'
    context = {'output':output,'input1':input1,'input2':input2,'input3':input3,'input4':input4,'input5':input5,'input6':input6,'input7':input7,'input8':input8,'input9':input9}
    return render(request,'main.html',context)

def predictQR(request):
    data = None
    if request.method == 'POST' and request.FILES.get('qrVal'):
        image = request.FILES['qrVal']
        decoded_data = decode(Image.open(image))
        if decoded_data:
            data = decoded_data[0].data.decode('utf-8')
    s = remove_all_parameters(data)
    l = check_url(s)
    result = model.predict([s])
    if l == 1 and validators.url(s) or result == 'good':
        ou = 'Real'
    else:
        ou = 'The URL in the QR code is Fake or the provided QR code is fake'
    context = {'out':ou,'inp':data}
    return render(request,'index.html',context)

def generate(array):
    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

    c = 0
    inverted_array = list(reversed(array))

    for i in range(len(inverted_array)):
        c = d[c][p[((i + 1) % 8)][inverted_array[i]]]

    return inv[c]

def validate(aadhaar_number):
    aadhaar_string = str(aadhaar_number)
    aadhaar_string = aadhaar_string.replace(' ','')
    aadhaar_array = list(map(int, aadhaar_string))

    if len(aadhaar_array) != 12:
        return 'Aadhaar numbers should be 12 digits in length'

    check_sum_digit = aadhaar_array.pop()

    if any(not str(digit).isdigit() for digit in aadhaar_array):
        return 'Please check the Aadhaar Number'

    if generate(aadhaar_array) == check_sum_digit:
        return 'The given Aadhaar Number is valid'
    else:
        return 'The given Aadhaar Number is not valid'
    
def predictaadhaar(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        df = pd.read_excel(excel_file)
        cname = request.POST.get('aVal')
        output_column = []
        for aadhaar_number in df[cname]:
            output = validate(aadhaar_number)
            output_column.append(output)
        df['Output'] = output_column
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=output.xlsx'
        return response

    return render(request, 'app.html',{'in':cname})