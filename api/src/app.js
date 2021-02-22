const express = require('express');
const routes = require('./routes');

const app = express();

const app_port = process.env.APP_PORT || 3000;

app.use('/', routes);

app.listen(app_port, () => {
    console.log(`App running on port ${app_port}.`)
});

module.exports = app;
