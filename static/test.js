//var category_dict = {C0:"280000000000", C1:"280000000001", C2:"280000000002", CM:"280000000003", "C+":"280000000005"};
var bar_dict = {"category_left":"barcodeEAN_left", "category_right":"barcodeEAN_right"};

function change_category(el_name){
    var cat_el = document.getElementById(el_name);
    //console.log(cat_el.value, category_dict[cat_el.value]);
    var bar_el = document.getElementById(bar_dict[el_name]);
    bar_el.value = category_dict[cat_el.value];
}

function change_product(el_name){
    var prod_el = document.getElementById(el_name);
    //console.log(cat_el.value, category_dict[cat_el.value]);
    var bar_el = document.getElementById(bar_dict[el_name]);
    //bar_el.value = category_dict[cat_el.value];
}

//console.log("first");