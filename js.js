let product = [];
let total = 0;


function add(product, price) {
    console.log(product, price);
    products.push(product);
    total = total + price;
}

function pay() {
    window.alert(products.join(", /n"))
}
