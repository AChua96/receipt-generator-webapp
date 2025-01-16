from flask import Flask, request, render_template, send_file
import os

app = Flask(__name__)

# Inventory dictionary to hold product names, prices, and stock quantities
inventory = {
    "Apple": {"price": 10.00, "stock": 50},
    "Banana": {"price": 5.00, "stock": 100},
    "Orange": {"price": 8.00, "stock": 75}
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
    quantities = request.form.getlist('quantities')

    receipt_lines = [f"Customer: {customer_name}", "---"]
    total = 0

    for item, qty in zip(purchased_items, quantities):
        if item in inventory:
            qty = int(qty)
            if qty > inventory[item]["stock"]:
                return render_template('index.html', inventory=inventory, message=f"Not enough stock for {item}.")

            price = inventory[item]["price"] * qty
            receipt_lines.append(f"{item} (x{qty}): PHP {price:.2f}")
            total += price

            # Deduct purchased quantity from stock
            inventory[item]["stock"] -= qty

    discount = 0
    if total >= 100:  # Apply a 15% discount for totals >= 100
        discount = total * 0.15
        total -= discount

    receipt_lines.append("\n---")
    receipt_lines.append(f"Subtotal: PHP {total + discount:.2f}")
    receipt_lines.append(f"Discount: PHP {discount:.2f}")
    receipt_lines.append(f"Total: PHP {total:.2f}")

    # Save receipt as .txt file
    receipt_filename = os.path.join(RECEIPT_FOLDER, "receipt.txt")
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

if __name__ == '__main__':
    app.run(debug=True)
