'use strict';

const DEV_MOD = true; // à true si le site est en mode développement (utilisé dans checkout.js)
const IF_NULL = 'null'; // ce qui est affiché lorsque une valeur PHP à afficher est égale à NULL

/* -------- FONCTIONS  -------- */

/* -------------------------------- */
/* ------------ LINKS ------------- */
/* -------------------------------- */

const getRequestUrl = () => {
	let requestUrl = window.location.href;
    return '/';
	return requestUrl.substring(0, requestUrl.indexOf('/') + 10);
}

const getWwwUrl = () => {
	let wwwUrl = window.location.href;
    return '/';
	return wwwUrl.substring(0, wwwUrl.indexOf('/')) + '/application/www';
}


const getCurrentPage = () => {
    return window.location.pathname;
}
const getFirstPage = () => {
    const pathname = window.location.pathname;
    return pathname.split('/')[1];
}

/* -------------------------------- */
/* ---------- END LINKS ----------- */
/* -------------------------------- */


/* -------------------------------- */
/* ----------- STORAGE ------------ */
/* -------------------------------- */

const recupStorage = (name = 'OnobioCart') => {
    let result = JSON.parse(localStorage.getItem(name));
    if (result == null)
        return [];
    return result;
}
const saveStorage = (obj, name= 'OnobioCart') => {
    localStorage.setItem(name, JSON.stringify(obj));
}

const getCookie = (cname) => {
    const name = cname + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const split = decodedCookie.split(';');
    for (let i=0; i<split.length; i++) {
        let c = split[i];
        while (c.charAt(0) == ' ')
            c = c.substring(1);
        if (c.indexOf(name) == 0)
            return c.substring(name.length, c.length);
    }
    return "";
}

/* -------------------------------- */
/* --------- END STORAGE ---------- */
/* -------------------------------- */


/* -------------------------------- */
/* ------------- DATE ------------- */
/* -------------------------------- */

const today = () => {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    today = dd + '-' + mm + '-' + yyyy;
    return today;
}
const articleDate = () => {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    return dd + ' ' + monthToString(mm) + ' ' + yyyy;
}
// reconstruit une date sous le format de jour?mois?année avec ? correspondant à la séparation entrée en paramètre de la fonction
const redoDate = (date, separation) => {
    if(date){
        let day = date.substr(8, 2);
        let month = date.substr(5, 2);
        let year = date.substr(0, 4);
        let newDate = day+separation+month+separation+year;
        //console.log(newDate);
        return newDate;
    }
    return IF_NULL;
}
const redoTime = (date, separation) => {
    if(!date)
        return IF_NULL;
    let hour = date.substr(11, 2);
    let minute = date.substr(14, 2);
    let second = date.substr(17, 2);
    return hour+separation+minute+separation+second;
}
const redoFullDate = (date, sep1, sep2) => {
    if(!date)
        return IF_NULL;
    let first_part = redoDate(date, sep1);
    let second_part = redoTime(date, sep2);
    return [first_part, second_part];
}
const redoSimpleDate = (date, sep) => {
    if(date){
        date = date.split('-');
        date = date[2]+sep+date[1]+sep+date[0];
        //console.log(date);
        return date;
    }
    return IF_NULL;
}
// récupère l'heure d'une date
const recupHourFromDate = (date) => {
    if(date)
        return date.substr(11, 8);
    return IF_NULL;
}
const monthToString = (month) => {
    switch(month.toString()){
        case '01':
        case '1' :
			return 'Janvier';
		case '02':
        case '2' :
			return 'Février';
		case '03':
        case '3' :
			return 'Mars';
		case '04':
        case '4' :
			return 'Avril';
		case '05':
        case '5' :
			return 'Mai';
		case '06':
        case '6' :
			return 'Juin';
		case '07':
        case '7' :
			return 'Juillet';
		case '08':
        case '8' :
			return 'Août';
		case '09':
        case '9' :
			return 'Septembre';
		case '10':  
			return 'Octobre';
		case '11':
			return 'Novembre';
		case '12':  
			return 'Décembre';
    }
}

/* -------------------------------- */
/* ----------- END DATE ----------- */
/* -------------------------------- */

/* -------------------------------- */
/* ----------- NUMBERS ------------ */
/* -------------------------------- */

// Ajoute si possible le chiffre des dizaines au nombre entrer (renvoie donc une chaîne de caractère)
const addTens = (nb) => {
    if(nb<10)
        return '0'+nb;
    return nb;
}

const roundUp = (nb, precision) => {
    precision = Math.pow(10, precision);
    return Math.ceil(nb * precision) / precision;
}

// Equivalent de money_format() / number_format() en PHP
const formatMoneyAmount = (amount) => {
    let formatter = new Intl.NumberFormat('fr',
    {
        currency              : 'eur',
        maximumFractionDigits : 2,
        minimumFractionDigits : 2,
        style                 : 'currency'
    });
    return formatter.format(amount);
}

/* -------------------------------- */
/* --------- END NUMBERS ---------- */
/* -------------------------------- */


/* -------------------------------- */
/* ------------ STRING ------------ */
/* -------------------------------- */

// réduit la taille d'une chaîne de caractère à la taille entrée en paramètre de la fonction en ajoutant "..." à la fin si la chaîne est plus petite que celle entrée en paramètre
const reduceStr = (str, length) => {
    if(str){
        let newStr = str.substr(0, length);
        if(str.length>length){
            newStr+='...';
        }
        return newStr;
    }
    return IF_NULL;
}

const ucfirst = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

const escapeHtml = (text) => {
    if(!text)
        return IF_NULL;
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => { return map[m]; });
}

/* -------------------------------- */
/* ---------- END STRING ---------- */
/* -------------------------------- */