const pg = require('pg');

const db_host = process.env.DB_HOST;
const db_port = process.env.DB_PORT;
const db_name = process.env.DB_NAME;
const db_user = process.env.DB_USER;
const db_password = process.env.DB_PASSWORD;

const pool = new pg.Pool({
  host: db_host,
  port: db_port,
  database: db_name,
  user: db_user,
  password: db_password,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
})

module.exports = {

    getBrowsingHistory: (req, res, next) => {
        var sql = 'SELECT * FROM api_db.product_visits WHERE user_id = $1 order by visit_date desc limit 10';
        pool.query(sql, [req.params.userId], (err, results) => {
            if (err) {
                return next(err);
            }
            var products = [];
            for(var i=0; i<results.rows.length; i++) {
                products.push(results.rows[i]['product_id']);
            }
            res.status(200).json({
                'user-id': req.params.userId,
                'products': products,
                'type': 'personalized'
            })
        })
    },

    deleteBrowsingHistory: (req, res, next) => {
        var sql = 'DELETE FROM api_db.product_visits WHERE user_id = $1 AND product_id = $2;';
        pool.query(sql, [req.params.userId, req.params.productId], (err, results) => {
            if (err) {
                return next(err);
            }
            res.sendStatus(200)
        })
    },

    getBestSeller: (req, res, next) => {
        var sql1 = `
    select product_id
    from (
      select ps.product_id, ps.user_count, row_number() over(partition by c.category_id order by ps.user_count desc) as rnk
      from (
        select *
        from (
          select category_id, row_number() over(order by visit_date desc) as rnk
          from (
            select ps.category_id, max(pv.visit_date) as visit_date
            from api_db.product_visits pv
            inner join api_db.product_sales ps on ps.product_id = pv.product_id
            where pv.user_id = $1
            group by ps.category_id
          ) a
        ) a
        where rnk <= 3
      ) c
      inner join api_db.product_sales ps on c.category_id = ps.category_id
    ) a
    where rnk <= 10
    order by user_count desc
    limit 10;
        `;

        var sql2 = `
    select product_id
    from api_db.product_sales
    order by user_count desc
    limit 10;
        `;

        pool.query(sql1, [req.params.userId], (err, results) => {
            if (err) {
                return next(err);
            }
            if (results.rows.length >= 5) {
                var products = [];
                for(var i=0; i<results.rows.length; i++) {
                    products.push(results.rows[i]['product_id']);
                }
                res.status(200).json({
                    'user-id': req.params.userId,
                    'products': products,
                    'type': 'personalized'
                })
            }
            else {
                pool.query(sql2, (err, results) => {
                    if (err) {
                        return next(err);
                    }
                    if (results.rows.length >= 5) {
                        var products = [];
                        for(var i=0; i<results.rows.length; i++) {
                            products.push(results.rows[i]['product_id']);
                        }
                        res.status(200).json({
                            'user-id': req.params.userId,
                            'products': products,
                            'type': 'non-personalized'
                        })
                    }
                    else {
                        res.status(200).json({
                            'user-id': req.params.userId,
                            'products': [],
                            'type': 'non-personalized'
                        })
                    }
                })
            }
        })
    }
}