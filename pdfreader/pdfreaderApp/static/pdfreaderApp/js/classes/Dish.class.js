class Dish {
    constructor(){
        this.checkedProducts = {};

        this.updateCheckedProducts(); // utile lors de la modification d'un plat

        $('input[name="name"]').change(this.updateProductNameDisplay.bind(this))
        $('span#uncheck').click(this.uncheckProducts.bind(this));
        $(document).on('change', 'input.product_checkbox', this.checkProduct.bind(this));

        $('button#find_products').click(this.searchProduct.bind(this));
        $('button#cancel_find_products').click(this.cancelSearchProduct.bind(this));
    }

    updateCheckedProducts(){
        const products = {}
        $('input.product_checkbox:checked').each((index, e) => {
            const id = 'product_'+e.value;
            products[id] = $('label[for="'+id+'"]').text();
        });
        this.checkedProducts = products
    }

    uncheckProducts(){
        $("input[name='products[]']").prop("checked", false);
        this.checkedProducts = {};
        this.updateProductsDisplay();
    }

    checkProduct(e){
        const tgt = e.currentTarget;
        const id = $(tgt).attr('id');
        const product_name = $('label[for="'+id+'"]').text();
        if(tgt.checked)
            this.checkedProducts[id] = product_name;
        else
            delete this.checkedProducts[id]
        this.updateProductsDisplay();
    }

    searchProduct(e){
        e.preventDefault();
        var query = $('input#product_search').val();
        if(!query.length) return;
        $.ajax({
            url: '/product/search',
            data: {
                'query': query
            },
            dataType: 'json',
            success: function(data) {
                if(data.length){
                    $('li.li_product').addClass('hide');
                    for(let i=0; i<data.length; i++){
                        $('li.li_product_'+data[i].product.id).removeClass('hide');
                    }
                }
            }
        });
    }
    cancelSearchProduct(e){
        e.preventDefault();
        $('#product_search').val('')
        $('li.li_product').removeClass('hide');
    }

    updateProductNameDisplay(e){
        $('span#dish_name').html(e.currentTarget.value)
    }
    updateProductsDisplay(){
        $('#recap_products ul').html('');
        $.each(this.checkedProducts, function(i, value) {
            $('#recap_products ul').prepend('<li>'+value+'</li>')
        });
    }
}