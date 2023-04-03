'use strict';

$(document).ready(function() {
	
    if(getFirstPage() == 'dish'){
        console.log('Dish JS');
        new Dish();
	}else if(getFirstPage() == 'user'){
        console.log('User JS');
        new User();
	}

});