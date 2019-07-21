from flask import Flask, request, jsonify
from main import main

app = Flask(__name__)

@app.route('/')
def get():
    stock_a = request.args.get('a')
    stock_b = request.args.get('b')
    if stock_a and stock_b:
        return jsonify(main(stock_a.strip(), stock_b.strip()))
    return {}


if __name__ == '__main__':
    app.run(debug=True)
