from flask import Flask, request, render_template, send_file
import os

app = Flask(__name__)

# Inventory dictionary to hold product names, prices, and stock quantities
inventory = {
    "Chili Garlic Oil 120g": {"price": 120.00, "stock": 0},
    "Chili Garlic Oil 220g": {"price": 220.00, "stock": 0},
    "Kuchay Dumpling 8pcs": {"price": 190.00, "stock": 11},
    "Hakaw 8pcs": {"price": 220.00, "stock": 16},
    "Shrimp Wonton 12pcs": {"price": 280.00, "stock": 0},
    "Japanese Siomai 12pcs": {"price": 280.00, "stock": 9},
    "Pork Shrimp w/ Mushroom Siomai 12pcs": {"price": 280.00, "stock": 0},
    "Beancurd Roll 12pcs": {"price": 320.00, "stock": 0},
    "Xiao Long Bao 12pcs": {"price": 330.00, "stock": 5},
    "Chicken Feet 500g": {"price": 320.00, "stock": 1},
    "Tausi Spareribs 300g": {"price": 320.00, "stock": 1}
}

# Folder to save receipts
RECEIPT_FOLDER = "receipts"
os.makedirs(RECEIPT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html', inventory=inventory)

@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    customer_name = request.form['customer_name']
    purchased_items = request.form.getlist('items')

    receipt_lines = [f"Customer: {customer_name}", "---"]
    total = 0

    for item in purchased_items:
        qty_key = f"quantities_{item}"
        qty = int(request.form.get(qty_key, 0))

        if item in inventory:
            if qty > inventory[item]["stock"]:
                return render_template('index.html', inventory=inventory, message=f"Not enough stock for {item}.")

            price = inventory[item]["price"] * qty
            receipt_lines.append(f"{item} (x{qty}): PHP {price:.2f}")
            total += price

            # Deduct purchased quantity from stock
            inventory[item]["stock"] -= qty

    discount = 0
    if total >= 3000:  # Apply a 15% discount for totals >= 3000
        discount = total * 0.15
        total -= discount

    receipt_lines.append("\n---")
    receipt_lines.append(f"Subtotal: PHP {total + discount:.2f}")
    receipt_lines.append(f"Discount: PHP {discount:.2f}")
    receipt_lines.append(f"Total: PHP {total:.2f}")

    # Save receipt as .txt file with customer name
    sanitized_name = customer_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    receipt_filename = os.path.join(RECEIPT_FOLDER, f"receipt_{sanitized_name}.txt")
    with open(receipt_filename, 'w') as file:
        file.write("\n".join(receipt_lines))

    return send_file(receipt_filename, as_attachment=True)

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    product_name = request.form['product_name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])

    inventory[product_name] = {"price": price, "stock": stock}
    return render_template('index.html', inventory=inventory, message=f"Added/Updated {product_name} with price PHP {price:.2f} and stock {stock}.")

@app.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    message = None
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        if product_name in inventory:
            inventory[product_name]['price'] = price
            inventory[product_name]['stock'] = stock
            message = f"Updated {product_name}: Price = PHP {price:.2f}, Stock = {stock}"
        else:
            inventory[product_name] = {"price": price, "stock": stock}
            message = f"Added new product {product_name}: Price = PHP {price:.2f}, Stock = {stock}"

    return render_template('manage_inventory.html', inventory=inventory, message=message)

if __name__ == '__main__':
    app.run(debug=True)
