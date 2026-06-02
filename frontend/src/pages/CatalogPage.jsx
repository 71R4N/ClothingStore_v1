import React, { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { Input, Select, Row, Col, Spin, Slider, Checkbox, Button, Card, Space } from 'antd';
import { SearchOutlined, FilterOutlined, ReloadOutlined } from '@ant-design/icons';
import ProductCard from '../components/ProductCard';
import { useSearchParams } from 'react-router-dom';

const { Search } = Input;
const { Option } = Select;

function CatalogPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const [priceRange, setPriceRange] = useState([0, 5000]);
  const [showFilters, setShowFilters] = useState(false);

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

  useEffect(() => {
  const categoryFromUrl = searchParams.get('category');
  if (categoryFromUrl && !searchParams.get('category_id')) {
    searchParams.set('category_id', categoryFromUrl);
    setSearchParams(searchParams);
  }
}, []);

  const onSearch = (value) => {
    if (value) searchParams.set('search', value);
    else searchParams.delete('search');
    setSearchParams(searchParams);
  };

  const onSortChange = (value) => {
    if (value) {
      const [sort_by, order] = value.split('_');
      searchParams.set('sort_by', sort_by);
      searchParams.set('order', order);
    } else {
      searchParams.delete('sort_by');
      searchParams.delete('order');
    }
    setSearchParams(searchParams);
  };

  const handlePriceFilter = () => {
    searchParams.set('min_price', priceRange[0]);
    searchParams.set('max_price', priceRange[1]);
    setSearchParams(searchParams);
  };

  const resetFilters = () => {
    setSearchParams({});
    setPriceRange([0, 5000]);
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', flexWrap: 'wrap', gap: 16, justifyContent: 'space-between', alignItems: 'center' }}>
        <Space wrap>
          <Search
            placeholder="Поиск по товарам"
            onSearch={onSearch}
            enterButton={<SearchOutlined />}
            style={{ width: 300 }}
            allowClear
          />
          <Select
            placeholder="Сортировка"
            allowClear
            onChange={onSortChange}
            style={{ width: 200 }}
            value={searchParams.get('sort_by') ? `${searchParams.get('sort_by')}_${searchParams.get('order')}` : undefined}
          >
            <Option value="price_asc">Цена по возрастанию</Option>
            <Option value="price_desc">Цена по убыванию</Option>
            <Option value="created_at_desc">Новинки</Option>
          </Select>
          <Button icon={<FilterOutlined />} onClick={() => setShowFilters(!showFilters)}>Фильтры</Button>
          <Button icon={<ReloadOutlined />} onClick={resetFilters}>Сбросить</Button>
        </Space>
      </div>

      <Row gutter={[24, 24]}>
        {showFilters && (
          <Col xs={24} sm={8} md={6}>
            <Card title="Цена" size="small">
              <Slider range min={0} max={10000} value={priceRange} onChange={setPriceRange} />
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>${priceRange[0]}</span>
                <span>${priceRange[1]}</span>
              </div>
              <Button type="primary" block style={{ marginTop: 16 }} onClick={handlePriceFilter}>Применить</Button>
            </Card>
          </Col>
        )}
        <Col xs={24} sm={showFilters ? 16 : 24} md={showFilters ? 18 : 24}>
          {loading ? (
            <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
          ) : products.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 60 }}>Товары не найдены</div>
          ) : (
            <Row gutter={[24, 24]}>
              {products.map(product => (
                <Col key={product.id} xs={24} sm={12} md={8} lg={6}>
                  <ProductCard product={product} />
                </Col>
              ))}
            </Row>
          )}
        </Col>
      </Row>
    </div>
  );
}

export default CatalogPage;