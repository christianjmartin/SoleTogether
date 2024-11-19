const express = require('express');
const SneaksAPI = require('sneaks-api');
const sneaks = new SneaksAPI();

const app = express();
const PORT = 5001;

app.get('/sneakers', (req, res) => {
    const keyword = req.query.keyword || '';
    const limit = parseInt(req.query.limit) || 25;

    sneaks.getProducts(keyword, limit, (err, products) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(products);
        }
    });
});


app.listen(PORT, () => {
    console.log(`Sneaks-API server running at http://localhost:${PORT}`);
});