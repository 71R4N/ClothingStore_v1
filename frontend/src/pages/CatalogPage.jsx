import React, { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { Input, Select, Row, Col, Spin } from 'antd';
import ProductCard from '../components/ProductCard';
import { useSearchParams } from 'react-router-dom';

const { Search } = Input;
const { Option } = Select;

function CatalogPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  const fetchProducts = () => {
    setLoading(true);
    const params = Object.fromEntries(searchParams.entries());
    catalogService.getProducts(params)
      .then(res => setProducts(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts();
  }, [searchParams]);

  const onSearch = (value) => {
    if (value) searchParams.set('search', value);
    else searchParams.delete('search');
    setSearchParams(searchParams);
  };

  const onSortChange = (value) => {
    if (value) {
      searchParams.set('sort_by', 'price');
      searchParams.set('order', value);
    } else {
      searchParams.delete('sort_by');
      searchParams.delete('order');
    }
    setSearchParams(searchParams);
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <Search placeholder="Поиск по товарам" onSearch={onSearch} enterButton style={{ maxWidth: 400 }} />
        <Select placeholder="Сортировка по цене" allowClear onChange={onSortChange} style={{ width: 200 }}>
          <Option value="asc">Цена по возрастанию</Option>
          <Option value="desc">Цена по убыванию</Option>
        </Select>
      </div>
      {loading ? (
        <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
      ) : (
        <Row gutter={[16, 16]}>
          {products.map(product => (
            <Col key={product.id} xs={24} sm={12} md={8} lg={6}>
              <ProductCard product={product} />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}

export default CatalogPage;