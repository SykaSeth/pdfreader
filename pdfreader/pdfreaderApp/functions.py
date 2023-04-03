import PyPDF2
import re
# le projet utilise PyPDF3 et non PyPDF2 comme ici (changement au niveau des methodes: numPages extractText etc)
# QR Code
import pyqrcode
import png
import random
import string
import uuid

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, data={}):
    template = get_template(template_src)
    html  = template.render(data)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding="UTF-8")
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="file.pdf"'
        return response
    return None


def an_admin(request):
    user = request.session.get('user', None)
    if user:
        return user['is_admin']
    return False

def generate_code():
    # Créer une liste de 4 caractères aléatoires
    chars = random.choices(string.ascii_letters + string.digits, k=4)
    # Concaténer les caractères en une chaîne
    code = ''.join(chars)
    return code

def generate_unique_code():
    return str(uuid.uuid4().hex[:10] + '-' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5)))

def handle_uploaded_file(f):
    with open('pdfreaderApp/static/uploads/'+f.name, 'wb+') as destination :
        for chunk in f.chunks():
            destination.write(chunk)


def verifyInvoiceFile(f):
    errors = []
    if not f.name.endswith('.pdf'):
        errors.append('Le fichier doit être un fichier au format PDF.')
    if f.size > 1000000:
        errors.append('Le fichier est trop lourd ('+str(int(f.size/1000))+'Ko > 1000Ko).')
    return errors

def verifyDishPhoto(p):
    errors = []
    if p.size > 5000000:
        errors.append('L\'image est trop lourde ('+str(int(p.size/1000000))+'Mo > 5Mo).')
    return errors

def checkFileInfo(f):
    # open the pdf file
    pdf = PyPDF2.PdfFileReader(f)

    page_obj = pdf.getPage(0)
    text = page_obj.extractText()
    # print(text)

    # text = text.split('\n')
    # return text

    # if text.split('\n')[0] == 'ProNatura SAS':
    if 'ProNatura SAS' in text:
        name = 'ProNatura SAS'
        date = re.search('[dD][uU][\s]*[0-9]{2}[/][0-9]{2}[/][0-9]{2}', text).group(0)
        date = date[3:].replace('/', '-').replace(' ', '')
        
        products = []
        r = re.compile('[L][0-9]{9}')
        for nb in range(pdf.numPages):
            page_obj = pdf.getPage(nb)
            text = page_obj.extractText()
            text = text.split('\n')
            for idx, i in enumerate(text):
                if r.match(i):
                    rr = re.compile('[0-9]{1,2}[,][0-9]{2}')
                    if rr.match(text[idx+2]):
                        products.append(text[idx+1][0:-1])
                    elif rr.match(text[idx+3]):
                        products.append(text[idx+1]+text[idx+2][0:-1])
                    else:
                        products.append(text[idx+1]+text[idx+2]+text[idx+3][0:-1])

    elif text.lower().count('reynaud') > 2:
        name = 'Reynaud'
        text = text.replace('Date Facture : ', 'ABCZ')
        date = re.search('[ABCZ]{4}[0-9]{2}[\.][0-9]{2}[\.][0-9]{4}', text)
        if date:
            date = date.group()
            date = date.replace('ABCZ', '').replace('.', '-').replace(' ', '')
        else:
            date = None
        products = re.findall('[0-9]{4,6}[\w 0-9*/()]*[1-9]{1}[\s]*[0-9]{1,3}[,]{1}[0-9]{3}', text)
        products_name = []
        for p in products:
            product = re.sub('[\s]*[1-9]{1}[\s]*[0-9]{1,3}[,]{1}[0-9]{3}', '', p)
            product = re.sub('[0-9]{4,6}[\s]*', '', product)
            products_name.append(product)

        products = products_name
    
    elif 'huillion' in text:
        name = 'Huillion'
        date = re.search('[B][L][0-9]{8}[\s]*[0-9]{2}[/][0-9]{2}[/][0-9]{4}[\s]*[C][L]', text).group(0)[-13:-3].replace('/', '-')
        products = []
        for nb in range(pdf.numPages):
            page_obj = pdf.getPage(nb)
            text = page_obj.extractText()

            text = re.sub('kg[\s]*[0-9]+[,][0-9]{3}[\s]*', '####', text)
            text = re.sub('[0-9]{1,3}[,][0-9]{2}[\s]*', '', text)
            text = re.sub('[A-Z]{2}[0-9]{3}[-][0-9]+[\s]*', '', text)
            text = re.sub('[0-9]{6}[/][0-9]{6}[\s]*', '', text)
            text = re.sub('[0-9]{2}[/][0-9]{2}[/][0-9]{4}[\s]*', '', text)
            text = re.sub('[0-9]+[/][0-9]+[-][0-9]+[/][0-9]+[\s]*', '', text)
            text = re.sub('[0-9]{5,8}[\s]*', '', text)
            text = re.sub(',[\s]*au kg', '', text)
            text = re.sub('Carton [0-9]{1}[\s]*[0-9]{1,3}[\s]*', '####', text)
            text = text.replace('unités', '----')
            text = re.sub('Carton\(s\)[\n]*[0-9]{1,2}[\s]*----[0-9]+[\s]*', '####', text)
            text = text.replace('---- ', '####')
            text = text.replace('unité(s) ', 'unité(s)').replace('unité(s)', '----')

            text = re.sub('----[0-9]{1,3}[\s]*', '####', text)
            text = re.sub('----[\s]*[0-9]{2}', '####', text)
            text = re.sub(',[\s\n]*au kg', '', text)
            text = text.replace('Carton(s) ', 'unité(s)').replace('unité(s)', '----')
            text = text[text.find('####'):]
            text = re.sub('[\n]', '', text)
            text = text.replace(' è', 'è').replace(' é', 'é').replace('c hè', 'chè')
            if nb+1 == pdf.numPages:
                text = text[0:text.find('COLIS:')-3]

            text = text.split('####')[1:]
            products.extend(text)

    elif 'poder' in text:
        name = 'Poder Sarl'
        if 'PODER SARL' in text:
            date = re.search('[0-9]{2}[/][0-9]{2}[/][0-9]{2}Vos Ref.', text).group(0)[:-8].replace('/', '-').replace('-22', '-2022').replace('-23', '-2023')
            products = []

            nb_of_page = pdf.numPages
            for nb in range(nb_of_page):
                page_obj = pdf.getPage(nb)
                text = page_obj.extractText()
                text = text.split('\n')
                index = [idx for idx, i in enumerate(text) if i == 'N° Lot']
                if index:
                    text = text[index[0]+1:-3]
                    text = [i for i in text if not i.startswith('Lots :')]
                    bad_array = ['BIOBREIZHFRANCECAT1','BIOFRANCECAT2','BIOBREIZHFRANCECAT2','FACTURATIONPIECE','BIOESPAGNECAT2','BIOBREIZHFRANCE','PIECEHORSOP','40FACTURATIONPIECE','COLIS','PC']
                    for idx, i in enumerate(text):
                        if i.replace(' ', '') not in bad_array:

                            bio_idx = i.find('BIO')
                            colis_idx = i.find('COLIS')
                            if bio_idx != -1:
                                i = i[:bio_idx+3]
                            elif colis_idx != -1:
                                i = i[:colis_idx-1]

                            if idx+1 in range(len(text)):
                                if text[idx + 1].replace(' ', '') not in bad_array:
                                    del text[idx + 1]
                                else:
                                    products.append(i)
            products = [i for idx, i in enumerate(products) if not 'TTC.  TVA' in i and not 'Palettes Qté' in i and not 'PAL PERDUE' in i and not 'Net à Payer' in i]
        else:
            date = re.search('[0-9]{2}[/][0-9]{2}[/][0-9]{4}', text).group(0).replace('/', '-')
            products = []
            nb_of_page = pdf.numPages
            for nb in range(nb_of_page):
                page_obj = pdf.getPage(nb)
                text = page_obj.extractText()
                text = text.split('\n')
                for idx, i in enumerate(text):
                    r = re.compile('^[0-9]+,[0-9]{3}')
                    r2 = re.compile('[0-9]+,[0-9]{2}')
                    if r.match(i):
                        bio_idx = i.find('BIO')
                        price=re.search('[0-9]+,[0-9]{2}[\s]', i).group(0)
                        price_idx = i.find(price)
                        if bio_idx == -1:
                            products.append(i[price_idx+len(price)+3:-1])
                        else:
                            products.append(i[price_idx+len(price)+3:bio_idx+3])
    else:
        return False

    return {
        'name': name,
        'date': date,
        'products': products
    }

def generateQRCode(link, name):
    qr_code = pyqrcode.create(link)
    qr_code.png('media/qr_codes/'+name+'.png', scale=5)

def decodeQRCode(path):
    from pyzbar.pyzbar import decode
    from PIL import Image
    decodeQR = decode(Image.open(path))
    return decodeQR[0].data.decode('ascii')

def getSessionMessage(request):
    if 'message' in request.session:
        message = request.session['message']
        request.session.pop('message', None)
        return message
    return {}