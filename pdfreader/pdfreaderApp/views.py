from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import get_template

from .forms import AddInvoiceForm, AddDishForm, SignUpForm
from .models import Invoices, Suppliers, Products, Dishes, DishesProducts, QRCode, User
from .functions import an_admin, generate_code, verifyInvoiceFile, checkFileInfo, verifyDishPhoto, generateQRCode, getSessionMessage
from io import BytesIO
from weasyprint import HTML


def home(request):
    return render(request, 'pdfreaderApp/index.html', {})

#################
#### INVOICE ####
#################

def invoices(request):
    if not an_admin(request): return redirect('home')

    invoices = Invoices.objects.all()
    return render(request, 'pdfreaderApp/invoice/all.html', {'invoices': invoices})

def invoice(request, code):
    invoice =   Invoices.objects.get(code=code)
    products=   Products.objects.filter(invoice_id=invoice.id)
    return render(request, 'pdfreaderApp/invoice/unique.html', {'invoice': invoice, 'products': products})

def add_invoice(request):
    if not an_admin(request): return redirect('home')

    message = {'success': [], 'error': []}
    invoices = Invoices.objects.all()
    if request.method == 'POST':
        form = AddInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_errors = verifyInvoiceFile(file)
            if not file_errors:
                new_invoice = Invoices.objects.create(file=file, name=file.name)
                result = checkFileInfo(file)
                if result:
                    supplier = Suppliers.objects.filter(name=result['name'])
                    if not supplier:
                        supplier = Suppliers.objects.create(name=result['name'])
                        supplier.save()
                    else:
                        supplier = supplier[0]
                    date    =   result['date'].split('-')
                    if len(date[2]) == 2:
                        date[2] = '20'+date[2]
                    shipping_date = date[2]+'-'+date[1]+'-'+date[0]

                    new_invoice.supplier_id     =   supplier.id
                    new_invoice.shipping_date   =   shipping_date
                    new_invoice.save()

                    for product in result['products']:
                        new_product = Products.objects.create(invoice_id = new_invoice.id, name=product)
                        new_product.save()

                    message['success'].append('La facture a bien été ajoutée et traitée.')
                else:
                    message['error'].append('Le facture a été ajoutée mais pas reconnue et n\'a donc pas pu être traitée.')

                return render(request, 'pdfreaderApp/invoice/add.html', {'invoices': invoices, 'message': message})
                
            message['error'] = file_errors
            return render(request, 'pdfreaderApp/invoice/add.html', {'invoices': invoices, 'message': message})

        print(form.errors)
        message['error'].append('Le formulaire n\'est pas valide.')
        return render(request, 'pdfreaderApp/invoice/add.html', {'invoices': invoices, 'message': message})
    else:
        form = AddInvoiceForm()
        return render(request, 'pdfreaderApp/invoice/add.html', {'form': form})

def delete_invoice(request, id):
    if not an_admin(request): return redirect('home')

    message = {}
    if request.method == "POST":
        invoice = Invoices.objects.get(id=id)
        invoice.delete()
        message['success'] = ['Le fichier "'+invoice.name+'" a bien été supprimé.']
    invoices = Invoices.objects.all()
    return render(request, 'pdfreaderApp/invoice/all.html', {'invoices': invoices})


###################
##### PRODUCT #####
###################

def products(request):
    products = Products.objects.all()
    return render(request, 'pdfreaderApp/products/all.html', {'products': products})

def search_product(request):
    if request.method == 'GET' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        query = request.GET.get('query')
        products = Products.objects.filter(name__istartswith=query)
        results = []
        for product in products:
            invoice = Invoices.objects.get(id = product.invoice_id)
            data = {'product': {'id': product.id, 'name': product.name}, 'invoice': {'id': invoice.id, 'name': invoice.name, 'path': invoice.file.url, 'date': invoice.shipping_date}}
            results.append(data)
        return JsonResponse(results, safe=False)
    return JsonResponse([])

 
##################
###### DISH ######
##################

def dishes(request):
    user = request.session.get('user', None)
    if user:
        user = User.objects.get(id=user['id'])
    response = getAllDishes()
    return render(request, 'pdfreaderApp/dish/all.html', {'response': response, 'user': user})

def dish(request, id):
    previous_page = request.META.get('HTTP_REFERER', '')

    dish    =   Dishes.objects.get(id=id)
    dps     =   DishesProducts.objects.filter(dish_id=dish.id)
    products=   []
    for dp in dps:
        product = Products.objects.get(id=dp.product_id)
        invoice = Invoices.objects.get(id=product.invoice_id)
        products.append({'id': product.id, 'name': product.name, 'invoice': {'name': invoice.name, 'path': invoice.file, 'date': invoice.shipping_date}})
    qr_code =   QRCode.objects.get(dish_id=dish.id)
    
    return render(request, 'pdfreaderApp/dish/unique.html', {'dish': dish, 'products': products, 'qr_code':qr_code, 'previous_page': previous_page})


def add_dish(request):
    if not an_admin(request): return redirect('dishes')
        
    message = {'success': [], 'error': []}
    products = Products.objects.all().order_by('-id')
    response = []
    for product in products:
        invoice = Invoices.objects.get(id = product.invoice_id)
        response.append({'product': {'id': product.id, 'name': product.name}, 'invoice': {'id': invoice.id, 'name': invoice.name, 'path': invoice.file, 'date': invoice.shipping_date}})
    
    if request.method == 'POST':
        form = AddDishForm(request.POST, request.FILES)
        if form.is_valid():
            name            =   form['name'].value()
            description     =   form['description'].value()
            photo           =   request.FILES['photo']
            form_products   =   request.POST.getlist('products[]')
            image_errors    =   verifyDishPhoto(photo)

            values = {'name': name, 'description': description, 'photo': photo, 'form_products': form_products}

            if not image_errors:
                if not form_products:
                    message['error'].append('Vous devez ajouter au moins un produit au plat.')
                else:
                    new_dish    =   Dishes.objects.create(name=name, photo=photo, description=description)
                    new_dish.save()

                    qr_code_link    =   request.build_absolute_uri(reverse('dish_pdf', args=(new_dish.id,)))
                    qr_code_name    =   name.replace(' ', '_')
                    generateQRCode(qr_code_link, qr_code_name)
                    qr_code_path    =   'qr_codes/'+qr_code_name+'.png'

                    new_qr_code     =   QRCode.objects.create(dish_id=new_dish.id, path=qr_code_path, link=qr_code_link)
                    new_qr_code.save()

                    for id in form_products:
                        new_dish_product  =   DishesProducts.objects.create(dish_id=new_dish.id ,product_id=id)
                        new_dish_product.save()
                    message['success'].append('Le plat a été ajouté avec succès.')
            else:
                message['error'] = image_errors

            if message['error']:
                return render(request, 'pdfreaderApp/dish/add.html', {'values': values, 'response': response, 'message': message})
            else:
                return render(request, 'pdfreaderApp/dish/add.html', {'response': response, 'message': message})

        print(form.errors)
        message['error'].append('Le formulaire n\'est pas valide.')
        return render(request, 'pdfreaderApp/dish/add.html', {'response': response, 'message': message})
    else:
        return render(request, 'pdfreaderApp/dish/add.html', {'response': response})

def update_dish(request, id):
    if not an_admin(request): return redirect('dishes')

    message = {'success': [], 'error': []}
    response = []
    
    products = Products.objects.all().order_by('-id')
    for product in products:
        invoice = Invoices.objects.get(id = product.invoice_id)
        response.append({'product': {'id': product.id, 'name': product.name}, 'invoice': {'id': invoice.id, 'name': invoice.name, 'path': invoice.file, 'date': invoice.shipping_date}})

    dish    =   Dishes.objects.get(id=id)
    dps     =   DishesProducts.objects.filter(dish_id=dish.id)
    dish_products   =   [d.product_id for d in dps]

    name        =   dish.name
    description =   dish.description

    if request.method == "POST":
        form = AddDishForm(request.POST, request.FILES)
        name        =   form['name'].value()
        description =   form['description'].value()
        dish_products   =   request.POST.getlist('products[]')

        if form.is_valid():
            photo       =   request.FILES.get('photo', False)

            if not photo:
                photo = dish.photo
            else:
                image_errors = verifyDishPhoto(photo)
                message['error'] = image_errors
            
            if not dish_products:
                message['error'].append('Vous devez ajouter au moins un produit au plat.')
            
            if not message['error']:
                dish.name       =   form['name'].value()
                dish.description=   form['description'].value()
                dish.photo      =   photo
                dish.save()

                old_dish_products = DishesProducts.objects.filter(dish_id = dish.id)
                old_dish_products.delete()
                for p_id in dish_products:
                    new_dish_product  =   DishesProducts.objects.create(dish_id=dish.id,product_id=p_id)
                    new_dish_product.save()
                message['success'].append('Le plat a été modifié avec succès.')

    values = {'name': name, 'description': description, 'dish_products': dish_products}
    
    return render(request, 'pdfreaderApp/dish/update.html', {'response': response, 'values': values, 'dish': dish, 'dish_products': dish_products, 'message': message})

def duplicate_dish(request, id):
    if not an_admin(request): return redirect('dishes')

    message = {'success': [], 'error': []}
    response = []
    if request.method == "POST":
        dish = Dishes.objects.get(id=id)
        new_dish = dish.duplicate()
        new_dish.name = new_dish.name + " (copie)"
        new_dish.save()

        qr_code_link    =   request.build_absolute_uri(reverse('dish_pdf', args=(new_dish.id,)))
        qr_code_name    =   dish.name.replace(' ', '_') + '_' + generate_code()
        generateQRCode(qr_code_link, qr_code_name)
        qr_code_path    =   'qr_codes/' + qr_code_name + '.png'

        new_qr_code     =   QRCode.objects.create(dish_id=new_dish.id, path=qr_code_path, link=qr_code_link)
        new_qr_code.save()

        message['success'].append('Le plat a été dupliqué avec succès. Vous pouvez maintenant le modifier.')

        return redirect('update_dish', id = new_dish.id)
    else:
        response = getAllDishes()
        return render(request, 'pdfreaderApp/dish/all.html', {'response': response})

def delete_dish(request, id):
    if not an_admin(request): return redirect('dishes')

    message = {}
    if request.method == "POST":
        dish = Dishes.objects.get(id=id)
        dish.delete()
        response = getAllDishes()
        message['success'] = ['Le plat "'+dish.name+'" a bien été supprimé.']
        return render(request, 'pdfreaderApp/dish/all.html', {'response': response, 'message': message})
    else:
        response = getAllDishes()
        return render(request, 'pdfreaderApp/dish/all.html', {'response': response})

def dish_pdf(request, id):
    dish    =   Dishes.objects.get(id=id)
    dps     =   DishesProducts.objects.filter(dish_id=dish.id)
    products=   []
    for dp in dps:
        product = Products.objects.get(id=dp.product_id)
        invoice = Invoices.objects.get(id=product.invoice_id)
        products.append({'id': product.id, 'name': product.name, 'invoice': {'name': invoice.name, 'path': invoice.file, 'date': invoice.shipping_date}})
    qr_code =   QRCode.objects.get(dish_id=dish.id)

    size_of_product_element = int((297 - 11*2 - 15) / len(products)) # taille de la page: 297mm; taille d'une marge: 11mm; taille header: 15mm
    data = {'dish': dish, 'products': products, 'size_of_product_element': size_of_product_element, 'qr_code':qr_code}

    # Render HTML template
    template = get_template('pdfreaderApp/dish/pdf.html')
    html_string = template.render(data)

    # Generate PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = BytesIO()
    html.write_pdf(result, presentational_hints=True)

    # Return response with PDF file
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    # response['Content-Disposition'] = 'filename="dish_{}.pdf"'.format(id)
    response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(dish.name)
    return response
        


#################
#### QR CODE ####
#################

def qr_codes(request):    
    qr_codes = QRCode.objects.order_by('-date').all()
    response = []
    for qr_code in qr_codes:
        dish = Dishes.objects.get(id=qr_code.dish_id)
        response.append({'qr_code': qr_code, 'dish': dish})
    return render(request, 'pdfreaderApp/qrcode/all.html', {'response': response})

def qr_code(request, id):
    qr_code     =   QRCode.objects.get(id=id)
    dish        =   Dishes.objects.get(id=qr_code.dish_id)
    response    =   {'qr_code': qr_code, 'dish': dish}
    return render(request, 'pdfreaderApp/qrcode/unique.html', {'response': response})


# ##################
# ###### USER ######
# ##################

def register(request):
    message = {'success': [], 'error': []}
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid:
            user = {
                'username'  :   request.POST.get('username'),
                'first_name':   request.POST.get('first_name'),
                'last_name' :   request.POST.get('last_name'),
                'email'     :   request.POST.get('email')
            }
            
            if User.objects.filter(email=user['email']):
                message['error'].append('Cette adresse mail est déjà utilisée.')
            if User.objects.filter(username=user['username']):
                message['error'].append('Ce nom d\'utilisateur existe déjà.')
            if len(message['error']) > 0:
                return render(request, 'pdfreaderApp/user/register.html', {'message': message})
            
            new_user = User.objects.create_user(**user)
            new_user.set_password(request.POST.get('password'))
            new_user.last_login = timezone.now()
            new_user.save()
            user['id'] = new_user.id

            message['success'] = ['Votre compte a bien été créé.']
            request.session['message'] = {'message': message}
            request.session['user'] =  user
            return redirect('user')
    else:
        return render(request, 'pdfreaderApp/user/register.html', {})
from django.contrib.auth import authenticate

def login(request):
    message = {'success': [], 'error': []}
    if request.method == 'POST':
        form = request.POST
        username = form['username']
        password = form['password']

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                user.last_login = timezone.now()
                user.save()
                request.session['user'] = user.to_json()
                request.session['message'] = {'success': ['Connecté avec succès.']}
                return redirect('user')
            else:
                message['error'].append('Le mot de passe est incorrect.')
        except User.DoesNotExist:
            message['error'].append('L\'identifiant est introuvable.')
    else:
        if 'user' in request.session:
            return redirect('user')
        
        message = getSessionMessage(request)

    return render(request, 'pdfreaderApp/user/login.html', {'message': message})

def logout(request):
    request.session.flush()
    return redirect('login')

def user(request):
    message = {}
    if 'user' not in request.session:
        return redirect('login')
    else:
        user = User.objects.get(id=request.session['user']['id'])
        message = getSessionMessage(request)
        return render(request, 'pdfreaderApp/user/simple.html', {'user': user, 'message': message})

def user_details(request):
    if 'user' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user']['id'])
    return render(request, 'pdfreaderApp/user/details.html', {'user': user})

def update_user(request):
    message = {}
    if 'user' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user']['id'])
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid:
            user.username = form['username'].value()
            user.first_name = form['first_name'].value()
            user.last_name = form['last_name'].value()
            user.save()
            message['success'] = ['Modification enregistrée.']
    else:
        user = User.objects.get(id=request.session['user']['id'])
    return render(request, 'pdfreaderApp/user/update.html', {'user': user, 'message': message})

def delete_user(request):
    return render(request, 'pdfreaderApp/user/login.html', {})

# ###################
# ###### ADMIN ######
# ###################

# def admin(request):
#     if 'user' not in request.session:
#         return redirect('login')
#     else:
#         user = User.objects.get(id=request.session['user']['id'])
#         if user.role != 'ADMIN':
#             return redirect('user')
#         return render(request, 'pdfreaderApp/user/admin/simple.html', {'user': user})

# def admin_users(request):
#     if 'user' not in request.session:
#         return redirect('login')
#     else:
#         user = User.objects.get(id=request.session['user']['id'])
#         if user.role != 'ADMIN':
#             return redirect('user')
    
#     users = User.objects.order_by('-date_joined').all()
#     return render(request, 'pdfreaderApp/user/admin/users.html', {'users': users})

###################################
####### SHORTCUTS FUNCTIONS #######
###################################

def getAllDishes():
    dishes = Dishes.objects.order_by('-date').all()
    result = []
    for dish in dishes:
        dps = DishesProducts.objects.filter(dish_id=dish.id)
        products = []
        for dp in dps:
            product = Products.objects.get(id=dp.product_id)
            products.append({'id': product.id, 'name': product.name})
        result.append({'dish': {'id': dish.id, 'name': dish.name, 'photo': dish.photo, 'date': dish.date}, 'products': products})
    return result