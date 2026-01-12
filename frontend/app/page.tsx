'use client';

import { useState, useEffect } from 'react';
import { api, Category, Product, CategoryCreate, ProductCreate } from '@/lib/api';

export default function InventoryPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'products' | 'categories'>('dashboard');

  // Form states
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showProductForm, setShowProductForm] = useState(false);
  const [categoryForm, setCategoryForm] = useState<CategoryCreate>({ name: '', description: '' });
  const [productForm, setProductForm] = useState<ProductCreate>({
    name: '', description: '', price: 0, quantity: 0, category_id: 0, sku: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [categoriesData, productsData] = await Promise.all([
        api.getCategories(),
        api.getProducts()
      ]);
      setCategories(categoriesData);
      setProducts(productsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createCategory(categoryForm);
      setCategoryForm({ name: '', description: '' });
      setShowCategoryForm(false);
      loadData();
    } catch (error) {
      console.error('Failed to create category:', error);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createProduct(productForm);
      setProductForm({ name: '', description: '', price: 0, quantity: 0, category_id: 0, sku: '' });
      setShowProductForm(false);
      loadData();
    } catch (error) {
      console.error('Failed to create product:', error);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (confirm('Delete this category?')) {
      try {
        await api.deleteCategory(id);
        loadData();
      } catch (error) {
        console.error('Failed to delete category:', error);
      }
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (confirm('Delete this product?')) {
      try {
        await api.deleteProduct(id);
        loadData();
      } catch (error) {
        console.error('Failed to delete product:', error);
      }
    }
  };

  const totalValue = products.reduce((sum, product) => sum + (product.price * product.quantity), 0);
  const lowStockProducts = products.filter(p => p.quantity < 10);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading your inventory...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-3 rounded-xl">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Custom RDBMS Inventory
                </h1>
                <p className="text-gray-500 text-sm">Powered by custom database engine</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-50 px-4 py-2 rounded-lg border border-green-200">
                <span className="text-green-700 font-semibold">${totalValue.toFixed(2)}</span>
                <span className="text-green-600 text-sm ml-1">Total Value</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-xl mb-8 w-fit">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: '📊' },
            { id: 'products', label: 'Products', icon: '📦' },
            { id: 'categories', label: 'Categories', icon: '🏷️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-white text-indigo-600 shadow-md'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.id === 'products' && (
                <span className="bg-indigo-100 text-indigo-600 text-xs px-2 py-1 rounded-full">
                  {products.length}
                </span>
              )}
              {tab.id === 'categories' && (
                <span className="bg-purple-100 text-purple-600 text-xs px-2 py-1 rounded-full">
                  {categories.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Total Products</p>
                    <p className="text-3xl font-bold text-gray-900">{products.length}</p>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-xl">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Categories</p>
                    <p className="text-3xl font-bold text-gray-900">{categories.length}</p>
                  </div>
                  <div className="bg-purple-50 p-3 rounded-xl">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Total Value</p>
                    <p className="text-3xl font-bold text-gray-900">${totalValue.toFixed(2)}</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-xl">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Low Stock</p>
                    <p className="text-3xl font-bold text-red-600">{lowStockProducts.length}</p>
                  </div>
                  <div className="bg-red-50 p-3 rounded-xl">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Products & Low Stock Alert */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Products</h3>
                <div className="space-y-3">
                  {products.slice(0, 5).map(product => {
                    const category = categories.find(c => c.id === product.category_id);
                    return (
                      <div key={product.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-500">{category?.name}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">${product.price}</p>
                          <p className="text-sm text-gray-500">Qty: {product.quantity}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {lowStockProducts.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg border border-red-200 p-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-red-700">Low Stock Alert</h3>
                  </div>
                  <div className="space-y-3">
                    {lowStockProducts.map(product => (
                      <div key={product.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                        <div>
                          <p className="font-medium text-gray-900">{product.name}</p>
                          <p className="text-sm text-red-600">Only {product.quantity} left</p>
                        </div>
                        <button className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-red-700 transition-colors">
                          Restock
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Products Tab */}
        {activeTab === 'products' && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Products Management</h2>
              <button
                onClick={() => setShowProductForm(true)}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Product</span>
              </button>
            </div>

            {/* Product Form Modal */}
            {showProductForm && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-xl font-semibold text-gray-900">Add New Product</h3>
                  </div>
                  <form onSubmit={handleCreateProduct} className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="Product Name"
                        value={productForm.name}
                        onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 bg-white"
                        required
                      />
                      <select
                        value={productForm.category_id}
                        onChange={(e) => setProductForm({...productForm, category_id: parseInt(e.target.value)})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 bg-white"
                        required
                      >
                        <option value="">Select Category</option>
                        {categories.map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                      </select>
                      <input
                        type="number"
                        step="0.01"
                        placeholder="Price"
                        value={productForm.price}
                        onChange={(e) => setProductForm({...productForm, price: parseFloat(e.target.value)})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 bg-white"
                        required
                      />
                      <input
                        type="number"
                        placeholder="Quantity"
                        value={productForm.quantity}
                        onChange={(e) => setProductForm({...productForm, quantity: parseInt(e.target.value)})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 bg-white"
                        required
                      />
                      <input
                        type="text"
                        placeholder="SKU (optional)"
                        value={productForm.sku}
                        onChange={(e) => setProductForm({...productForm, sku: e.target.value})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent col-span-2 text-gray-900 bg-white"
                      />
                      <textarea
                        placeholder="Description (optional)"
                        value={productForm.description}
                        onChange={(e) => setProductForm({...productForm, description: e.target.value})}
                        className="border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent col-span-2 text-gray-900 bg-white"
                        rows={3}
                      />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                      <button
                        type="button"
                        onClick={() => setShowProductForm(false)}
                        className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200"
                      >
                        Create Product
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* Products Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map(product => {
                const category = categories.find(c => c.id === product.category_id);
                return (
                  <div key={product.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-200 group">
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-lg mb-1">{product.name}</h3>
                          <span className="inline-block bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full">
                            {category?.name || 'Uncategorized'}
                          </span>
                        </div>
                        <button
                          onClick={() => handleDeleteProduct(product.id)}
                          className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-all duration-200 p-1"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                      
                      {product.description && (
                        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{product.description}</p>
                      )}
                      
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-500 text-sm">Price</span>
                          <span className="font-bold text-lg text-gray-900">${product.price}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-500 text-sm">Stock</span>
                          <span className={`font-semibold ${product.quantity < 10 ? 'text-red-600' : 'text-green-600'}`}>
                            {product.quantity} units
                          </span>
                        </div>
                        {product.sku && (
                          <div className="flex justify-between items-center">
                            <span className="text-gray-500 text-sm">SKU</span>
                            <span className="text-gray-700 text-sm font-mono">{product.sku}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 px-6 py-3 border-t border-gray-100">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-500">Total Value</span>
                        <span className="font-semibold text-gray-900">
                          ${(product.price * product.quantity).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Categories Tab */}
        {activeTab === 'categories' && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Categories Management</h2>
              <button
                onClick={() => setShowCategoryForm(true)}
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Category</span>
              </button>
            </div>

            {/* Category Form Modal */}
            {showCategoryForm && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-xl font-semibold text-gray-900">Add New Category</h3>
                  </div>
                  <form onSubmit={handleCreateCategory} className="p-6 space-y-4">
                    <input
                      type="text"
                      placeholder="Category Name"
                      value={categoryForm.name}
                      onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                      className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 bg-white"
                      required
                    />
                    <textarea
                      placeholder="Description (optional)"
                      value={categoryForm.description}
                      onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})}
                      className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 bg-white"
                      rows={3}
                    />
                    <div className="flex justify-end space-x-3 pt-4">
                      <button
                        type="button"
                        onClick={() => setShowCategoryForm(false)}
                        className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
                      >
                        Create Category
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* Categories Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categories.map(category => {
                const productCount = products.filter(p => p.category_id === category.id).length;
                const categoryValue = products
                  .filter(p => p.category_id === category.id)
                  .reduce((sum, p) => sum + (p.price * p.quantity), 0);
                
                return (
                  <div key={category.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-200 group">
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-xl mb-2">{category.name}</h3>
                          {category.description && (
                            <p className="text-gray-600 text-sm">{category.description}</p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteCategory(category.id)}
                          disabled={productCount > 0}
                          className={`opacity-0 group-hover:opacity-100 transition-all duration-200 p-1 ${
                            productCount > 0 
                              ? 'text-gray-400 cursor-not-allowed' 
                              : 'text-red-500 hover:text-red-700'
                          }`}
                          title={productCount > 0 ? "Cannot delete category with products" : "Delete category"}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <p className="text-blue-600 text-sm font-medium">Products</p>
                          <p className="text-blue-900 text-xl font-bold">{productCount}</p>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg">
                          <p className="text-green-600 text-sm font-medium">Value</p>
                          <p className="text-green-900 text-xl font-bold">${categoryValue.toFixed(2)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}