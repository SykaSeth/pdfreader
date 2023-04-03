class User {
    constructor(){
        this.init();

        $(document).on('change', 'input', this.onChangeInput.bind(this));
    }
    init(){
        $('input').each((i, tgt) => {
            if(tgt.value.length)
                $(tgt).siblings('label').addClass('up')
        })
    }
    onChangeInput(e){
        const tgt = e.currentTarget;
        if(tgt.value.length){
            $(tgt).siblings('label').addClass('up')
        }else{
            $(tgt).siblings('label').removeClass('up')
        }
    }
}