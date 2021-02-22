const pg = require('pg');
const sinon = require('sinon');
const {expect} = require('chai');
const chai = require('chai');
const chaiHttp = require('chai-http');

chai.use(chaiHttp);
chai.should();

describe('tet', () => {
  afterEach(() => {
    sinon.restore();
  });

  it('should return browsing history', (done) => {
    const mPool = { query: sinon.stub().callsFake((sql, params, cb) => {
        cb(null, { rows: [{product_id: 'p1'}, {product_id: 'p2'}, {product_id: 'p3'}, {product_id: 'p4'}, {product_id: 'p5'}] })
    }) };
    const poolStub = sinon.stub(pg, "Pool").callsFake(() => mPool);

    const app = require('../src/app');
    chai.request(app)
    .get('/browsing-history/user-1')
    .end((err, res) => {
        res.should.have.status(200);
        res.body.should.be.a('object');
        res.body.should.have.property('products');
        res.body.products.length.should.eql(5);
        res.body.type.should.eql('personalized');
        done();
    });

  })

  it('should return personalized', (done) => {
    const mPool = { query: sinon.stub().callsFake((sql, params, cb) => {
        cb(null, { rows: [{product_id: 'p1'}, {product_id: 'p2'}, {product_id: 'p3'}, {product_id: 'p4'}, {product_id: 'p5'}] })
    }) };
    const poolStub = sinon.stub(pg, "Pool").callsFake(() => mPool);
    const app = require('../src/app');
    chai.request(app)
    .get('/best-seller/user-1')
    .end((err, res) => {
        res.should.have.status(200);
        res.body.should.be.a('object');
        res.body.should.have.property('products');
        res.body.products.length.should.eql(5);
        res.body.type.should.eql('personalized');
        done();
    });

  })

})
