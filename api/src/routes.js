const Router = require('express').Router;
const controllers = require('./controllers');

const routes = Router();

routes.get('/browsing-history/:userId', controllers.getBrowsingHistory)

routes.delete('/browsing-history/:userId/:productId', controllers.deleteBrowsingHistory)

routes.get('/best-seller/:userId', controllers.getBestSeller)

routes.use((err, req, res, next) => {
    console.log(err);
    res.sendStatus(500);
});

module.exports = routes;
