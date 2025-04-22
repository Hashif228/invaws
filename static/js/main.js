function openAddProductModal() {
    document.getElementById('addProductModal').style.display = 'flex';
}

function closeAddProductModal() {
    document.getElementById('addProductModal').style.display = 'none';
}


function openEditProductModal(id, name, category, stock, price, supplier) {
    document.getElementById('productName').value = name;
    document.getElementById('productCategory').value = category;
    document.getElementById('productQuantity').value = stock;
    document.getElementById('productPrice').value = price;
    document.getElementById('productSupplier').value = supplier;
    
    // Set the action of the form to the correct URL for updating the product
    document.getElementById('editProductForm').action = '/edit_product/' + id;
    
    // Open the modal
    document.getElementById('editProductModal').style.display = 'flex';
}

function closeEditProductModal() {
    document.getElementById('editProductModal').style.display = 'none';
}



window.onclick = function(event) {
    const modal = document.getElementById('addProductModal');
    if (event.target == modal) {
        closeAddProductModal();
    }
}

// document.querySelector('#addProductModal form').addEventListener('submit', function(e) {
//     e.preventDefault();
//     alert('Product added successfully!');
//     closeAddProductModal();
//     this.reset();
// });

