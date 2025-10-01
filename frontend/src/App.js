import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import "@/App.css";

// Import shadcn components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Checkbox } from './components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Calendar } from './components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './components/ui/popover';
import { format } from 'date-fns';
import { CalendarIcon, Users, TrendingUp, BarChart3, Plus, Edit, Trash2, Filter } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token by getting user info
      checkAuth();
    } else {
      setLoading(false);
    }
  }, [token]);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Auth check failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (email, password, full_name) => {
    try {
      const response = await axios.post(`${API}/register`, { 
        email, 
        password, 
        full_name 
      });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Status color functions
const getStatusColor = (status, actionStatusTypes = []) => {
  // For action statuses, try to get color from database
  const actionStatus = actionStatusTypes.find(ast => ast.key === status);
  if (actionStatus) {
    return actionStatus.color;
  }
  
  // Fallback colors
  const colorMap = {
    'made_order': '#22C55E', // зелений
    'completed_survey': '#8B5CF6', // фіолетовий
    'notified_about_promotion': '#8B5CF6', // фіолетовий
    'has_additional_questions': '#EF4444', // червоний
    'need_callback': '#F59E0B', // оранжевий
    'not_answering': '#EF4444', // червоний
    'planning_order': '#EAB308', // жовтий
    'debt': '#EF4444' // червоний для боргу
  };
  return colorMap[status] || '#6B7280';
};

const getClientStatusColor = (status, statusTypes = []) => {
  const statusType = statusTypes.find(st => st.name === status);
  return statusType ? statusType.color : '#3B82F6';
};

// Status names in Ukrainian
const getStatusName = (status) => {
  const nameMap = {
    'made_order': 'Зробив замовлення',
    'completed_survey': 'Пройшов опитування',
    'notified_about_promotion': 'Сповістив про акцію',
    'has_additional_questions': 'Має додаткові питання',
    'need_callback': 'Передзвонити',
    'not_answering': 'Не виходить на зв\'язок',
    'planning_order': 'Планує замовлення'
  };
  return nameMap[status] || status;
};

// Auth Pages
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = isLogin 
      ? await login(formData.email, formData.password)
      : await register(formData.email, formData.password, formData.full_name);

    if (result.success) {
      // Успішний логін - перенаправляємо на головну сторінку
      navigate('/', { replace: true });
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            {isLogin ? 'Вхід в систему' : 'Реєстрація'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <Label htmlFor="full_name">Повне ім'я</Label>
                <Input
                  id="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required={!isLogin}
                  data-testid="auth-full-name"
                />
              </div>
            )}
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                data-testid="auth-email"
              />
            </div>
            <div>
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                data-testid="auth-password"
              />
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
              data-testid="auth-submit"
            >
              {loading ? 'Обробка...' : (isLogin ? 'Увійти' : 'Зареєструватися')}
            </Button>
          </form>
          <div className="text-center mt-4">
            <Button
              variant="link"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setFormData({ email: '', password: '', full_name: '' });
              }}
              data-testid="auth-toggle"
            >
              {isLogin ? 'Потрібна реєстрація?' : 'Вже маєте акаунт?'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
};

// Navigation component
const Navigation = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 mb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">CRM Система</h1>
            </div>
            <div className="ml-6 flex space-x-8">
              <Link
                to="/"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                  location.pathname === '/'
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Users className="w-4 h-4 mr-2" />
                Клієнти
              </Link>
              <Link
                to="/daily-reports"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                  location.pathname === '/daily-reports'
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Щоденний звіт
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Привіт, {user?.full_name || user?.email}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              data-testid="logout-button"
            >
              Вийти
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Main Clients Page
const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [statusTypes, setStatusTypes] = useState([]);
  const [actionStatusTypes, setActionStatusTypes] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [editingClient, setEditingClient] = useState(null);
  const [newStatusType, setNewStatusType] = useState({ name: '', color: '#3B82F6' });
  const [editingStatusType, setEditingStatusType] = useState(null);

  // Load data
  useEffect(() => {
    loadData();
  }, [filterStatus]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [clientsRes, statusTypesRes, actionStatusTypesRes, statsRes, summaryRes] = await Promise.all([
        axios.get(`${API}/clients${filterStatus && filterStatus !== 'all' ? `?status_filter=${filterStatus}` : ''}`),
        axios.get(`${API}/client-status-types`),
        axios.get(`${API}/action-status-types`),
        axios.get(`${API}/clients/statistics`),
        axios.get(`${API}/clients/summary`)
      ]);
      
      setClients(clientsRes.data);
      setStatusTypes(statusTypesRes.data);
      setActionStatusTypes(actionStatusTypesRes.data);
      setStatistics(statsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Помилка завантаження даних');
    } finally {
      setLoading(false);
    }
  };

  // Client form handlers
  const handleSaveClient = async (clientData) => {
    try {
      if (editingClient) {
        await axios.put(`${API}/clients/${editingClient.id}`, clientData);
        toast.success('Клієнта оновлено');
      } else {
        await axios.post(`${API}/clients`, clientData);
        toast.success('Клієнта додано');
      }
      setEditingClient(null);
      loadData();
    } catch (error) {
      console.error('Error saving client:', error);
      toast.error('Помилка збереження клієнта');
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цього клієнта?')) {
      try {
        await axios.delete(`${API}/clients/${clientId}`);
        toast.success('Клієнта видалено');
        loadData();
      } catch (error) {
        console.error('Error deleting client:', error);
        toast.error('Помилка видалення клієнта');
      }
    }
  };

  // Status type handlers
  const handleSaveStatusType = async () => {
    try {
      if (editingStatusType) {
        await axios.put(`${API}/client-status-types/${editingStatusType.id}`, newStatusType);
        toast.success('Статус оновлено');
      } else {
        await axios.post(`${API}/client-status-types`, newStatusType);
        toast.success('Статус додано');
      }
      setNewStatusType({ name: '', color: '#3B82F6' });
      setEditingStatusType(null);
      loadData();
    } catch (error) {
      console.error('Error saving status type:', error);
      toast.error('Помилка збереження статусу');
    }
  };

  const handleDeleteStatusType = async (statusId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цей статус?')) {
      try {
        await axios.delete(`${API}/client-status-types/${statusId}`);
        toast.success('Статус видалено');
        loadData();
      } catch (error) {
        console.error('Error deleting status type:', error);
        toast.error('Помилка видалення статусу');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-gray-900">{statistics.total_clients || 0}</div>
            <div className="text-xs text-gray-500">Загальна кількість</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('made_order', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('made_order', actionStatusTypes) }}>
              {statistics.made_order || 0}
            </div>
            <div className="text-xs text-gray-500">Зробили замовлення</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('planning_order', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('planning_order', actionStatusTypes) }}>
              {statistics.planning_order || 0}
            </div>
            <div className="text-xs text-gray-500">Планують замовлення</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('need_callback', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('need_callback', actionStatusTypes) }}>
              {statistics.need_callback || 0}
            </div>
            <div className="text-xs text-gray-500">Передзвонити</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('completed_survey', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('completed_survey', actionStatusTypes) }}>
              {statistics.completed_survey || 0}
            </div>
            <div className="text-xs text-gray-500">Пройшли опитування</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('notified_about_promotion', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('notified_about_promotion', actionStatusTypes) }}>
              {statistics.notified_about_promotion || 0}
            </div>
            <div className="text-xs text-gray-500">Сповіщені про акцію</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('has_additional_questions', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('has_additional_questions', actionStatusTypes) }}>
              {statistics.has_additional_questions || 0}
            </div>
            <div className="text-xs text-gray-500">Мають питання</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('not_answering', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('not_answering', actionStatusTypes) }}>
              {statistics.not_answering || 0}
            </div>
            <div className="text-xs text-gray-500">Не відповідають</div>
          </CardContent>
        </Card>
        
        <Card style={{ borderLeft: `4px solid ${getStatusColor('debt', actionStatusTypes)}` }}>
          <CardContent className="p-4">
            <div className="text-2xl font-bold" style={{ color: getStatusColor('debt', actionStatusTypes) }}>
              {statistics.has_debt || 0}
            </div>
            <div className="text-xs text-gray-500">Мають борг</div>
          </CardContent>
        </Card>
      </div>

      {/* Summary Statistics */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
          Загальна статистика замовлень
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-green-600">
              {summary.total_expected_sets || 0}
            </div>
            <div className="text-sm text-gray-600">Планується наборів</div>
            <div className="text-xs text-gray-500 mt-1">
              {(summary.total_expected_amount || 0).toLocaleString('uk-UA')} ₴
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-blue-600">
              {summary.total_ordered_sets || 0}
            </div>
            <div className="text-sm text-gray-600">Замовлено наборів</div>
            <div className="text-xs text-gray-500 mt-1">
              {(summary.total_ordered_amount || 0).toLocaleString('uk-UA')} ₴
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-amber-600">
              {((summary.total_expected_amount || 0) - (summary.total_ordered_amount || 0)).toLocaleString('uk-UA')} ₴
            </div>
            <div className="text-sm text-gray-600">Залишилось планів</div>
            <div className="text-xs text-gray-500 mt-1">
              {((summary.total_expected_sets || 0) - (summary.total_ordered_sets || 0))} наборів
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-red-600">
              {(summary.total_debt || 0).toLocaleString('uk-UA')} ₴
            </div>
            <div className="text-sm text-gray-600">Загальний борг</div>
            <div className="text-xs text-gray-500 mt-1">
              {statistics.has_debt || 0} клієнтів
            </div>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Прогрес виконання планів</span>
            <span>
              {summary.total_expected_amount > 0 
                ? Math.round((summary.total_ordered_amount / summary.total_expected_amount) * 100)
                : 0
              }%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-300"
              style={{
                width: `${summary.total_expected_amount > 0 
                  ? Math.min((summary.total_ordered_amount / summary.total_expected_amount) * 100, 100)
                  : 0
                }%`
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2 items-center">
          <Filter className="w-4 h-4 text-gray-500" />
          <Select value={filterStatus || undefined} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Фільтр по статусу" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Всі статуси</SelectItem>
              <SelectItem value="made_order">Зробив замовлення</SelectItem>
              <SelectItem value="planning_order">Планує замовлення</SelectItem>
              <SelectItem value="need_callback">Передзвонити</SelectItem>
              <SelectItem value="completed_survey">Пройшов опитування</SelectItem>
              <SelectItem value="notified_about_promotion">Сповістив про акцію</SelectItem>
              <SelectItem value="has_additional_questions">Має питання</SelectItem>
              <SelectItem value="not_answering">Не відповідає</SelectItem>
              <SelectItem value="has_debt">Має борг</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2">
          <StatusTypeManagement 
            statusTypes={statusTypes}
            newStatusType={newStatusType}
            setNewStatusType={setNewStatusType}
            editingStatusType={editingStatusType}
            setEditingStatusType={setEditingStatusType}
            onSave={handleSaveStatusType}
            onDelete={handleDeleteStatusType}
          />
          <ActionStatusManagement 
            actionStatusTypes={actionStatusTypes}
            onSave={() => loadData()}
          />
          <ClientDialog 
            client={editingClient}
            statusTypes={statusTypes}
            actionStatusTypes={actionStatusTypes}
            onSave={handleSaveClient}
            onCancel={() => setEditingClient(null)}
            trigger={
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Додати клієнта
              </Button>
            }
          />
        </div>
      </div>

      {/* Clients Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ім'я Прізвище</TableHead>
                  <TableHead>Телефон</TableHead>
                  <TableHead>Статус клієнта</TableHead>
                  <TableHead>Борг</TableHead>
                  <TableHead>Статуси дій</TableHead>
                  <TableHead>Дата контакту</TableHead>
                  <TableHead>Коментар</TableHead>
                  <TableHead>Дії</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell className="font-medium">
                      {client.first_name} {client.last_name}
                    </TableCell>
                    <TableCell>{client.phone}</TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        style={{ 
                          borderColor: getClientStatusColor(client.client_status, statusTypes),
                          color: getClientStatusColor(client.client_status, statusTypes)
                        }}
                      >
                        {client.client_status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {client.debt > 0 && (
                        <span style={{ color: getStatusColor('debt') }} className="font-bold">
                          {client.debt} ₴
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      <ActionStatusPopover 
                        client={client} 
                        actionStatusTypes={actionStatusTypes}
                        onUpdate={loadData}
                      />
                    </TableCell>
                    <TableCell>
                      {client.last_contact_date ? 
                        format(new Date(client.last_contact_date), 'dd.MM.yyyy') : 
                        '-'
                      }
                    </TableCell>
                    <TableCell>
                      <CommentCell client={client} onUpdate={loadData} />
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {client.crm_link && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(client.crm_link, '_blank')}
                            className="text-blue-600 hover:text-blue-800"
                            data-testid={`crm-link-${client.id}`}
                            title="Відкрити CRM посилання"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingClient(client)}
                          data-testid={`edit-client-${client.id}`}
                          title="Редагувати клієнта"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClient(client.id)}
                          data-testid={`delete-client-${client.id}`}
                          title="Видалити клієнта"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Client Dialog Component
const ClientDialog = ({ client, statusTypes, actionStatusTypes, onSave, onCancel, trigger }) => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    client_status: '',
    crm_link: '',
    expected_order_sets: '',
    expected_order_amount: '',
    sets_ordered_this_month: '',
    amount_this_month: '',
    debt: '',
    last_contact_date: null,
    task_description: '',
    comment: '',
    action_status: {
      made_order: false,
      completed_survey: false,
      notified_about_promotion: false,
      has_additional_questions: false,
      need_callback: false,
      not_answering: false,
      planning_order: false
    }
  });

  useEffect(() => {
    if (client) {
      setFormData({
        ...client,
        last_contact_date: client.last_contact_date ? new Date(client.last_contact_date) : null,
        expected_order_sets: client.expected_order_sets || '',
        expected_order_amount: client.expected_order_amount || '',
        sets_ordered_this_month: client.sets_ordered_this_month || '',
        amount_this_month: client.amount_this_month || '',
        debt: client.debt || ''
      });
      setOpen(true);
    }
  }, [client]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      last_contact_date: formData.last_contact_date ? format(formData.last_contact_date, 'yyyy-MM-dd') : null,
      expected_order_sets: formData.expected_order_sets === '' ? 0 : Number(formData.expected_order_sets),
      expected_order_amount: formData.expected_order_amount === '' ? 0 : Number(formData.expected_order_amount),
      sets_ordered_this_month: formData.sets_ordered_this_month === '' ? 0 : Number(formData.sets_ordered_this_month),
      amount_this_month: formData.amount_this_month === '' ? 0 : Number(formData.amount_this_month),
      debt: formData.debt === '' ? 0 : Number(formData.debt)
    };
    onSave(submitData);
    setOpen(false);
    if (onCancel) onCancel();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto" aria-describedby="client-form-description">
        <DialogHeader>
          <DialogTitle>
            {client ? 'Редагувати клієнта' : 'Додати клієнта'}
          </DialogTitle>
          <div id="client-form-description" className="text-sm text-gray-600">
            {client ? 'Редагуйте інформацію про клієнта' : 'Заповніть форму для додавання нового клієнта'}
          </div>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name">Ім'я</Label>
              <Input
                id="first_name"
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                required
                data-testid="client-first-name"
              />
            </div>
            <div>
              <Label htmlFor="last_name">Прізвище</Label>
              <Input
                id="last_name"
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                required
                data-testid="client-last-name"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="phone">Телефон</Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                data-testid="client-phone"
              />
            </div>
            <div>
              <Label htmlFor="client_status">Статус клієнта</Label>
              <Select
                value={formData.client_status || undefined}
                onValueChange={(value) => setFormData({...formData, client_status: value})}
              >
                <SelectTrigger data-testid="client-status-select">
                  <SelectValue placeholder="Оберіть статус" />
                </SelectTrigger>
                <SelectContent>
                  {statusTypes.map((status) => (
                    <SelectItem key={status.id} value={status.name}>
                      {status.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="crm_link">CRM посилання</Label>
            <Input
              id="crm_link"
              type="url"
              value={formData.crm_link}
              onChange={(e) => setFormData({...formData, crm_link: e.target.value})}
              placeholder="https://..."
              data-testid="client-crm-link"
            />
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div>
              <Label htmlFor="expected_order_sets">Очікувані набори</Label>
              <Input
                id="expected_order_sets"
                type="text"
                value={formData.expected_order_sets || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d+$/.test(value)) {
                    setFormData({...formData, expected_order_sets: value === '' ? 0 : parseInt(value)});
                  }
                }}
                placeholder="0"
                data-testid="client-expected-sets"
              />
            </div>
            <div>
              <Label htmlFor="expected_order_amount">Очікувана сума (₴)</Label>
              <Input
                id="expected_order_amount"
                type="text"
                value={formData.expected_order_amount || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d*\.?\d*$/.test(value)) {
                    setFormData({...formData, expected_order_amount: value === '' ? 0 : parseFloat(value) || 0});
                  }
                }}
                placeholder="0.00"
                data-testid="client-expected-amount"
              />
            </div>
            <div>
              <Label htmlFor="sets_ordered_this_month">Наборів в цьому місяці</Label>
              <Input
                id="sets_ordered_this_month"
                type="text"
                value={formData.sets_ordered_this_month || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d+$/.test(value)) {
                    setFormData({...formData, sets_ordered_this_month: value === '' ? 0 : parseInt(value)});
                  }
                }}
                placeholder="0"
                data-testid="client-sets-this-month"
              />
            </div>
            <div>
              <Label htmlFor="amount_this_month">Сума в цьому місяці (₴)</Label>
              <Input
                id="amount_this_month"
                type="text"
                value={formData.amount_this_month || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d*\.?\d*$/.test(value)) {
                    setFormData({...formData, amount_this_month: value === '' ? 0 : parseFloat(value) || 0});
                  }
                }}
                placeholder="0.00"
                data-testid="client-amount-this-month"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="debt">Борг (₴)</Label>
              <Input
                id="debt"
                type="text"
                value={formData.debt || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d*\.?\d*$/.test(value)) {
                    setFormData({...formData, debt: value === '' ? 0 : parseFloat(value) || 0});
                  }
                }}
                placeholder="0.00"
                data-testid="client-debt"
              />
            </div>
            <div>
              <Label>Дата останього контакту</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                    data-testid="client-contact-date"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.last_contact_date ? format(formData.last_contact_date, 'PPP') : 'Оберіть дату'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={formData.last_contact_date}
                    onSelect={(date) => setFormData({...formData, last_contact_date: date})}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div>
            <Label htmlFor="task_description">Суть задачі</Label>
            <Textarea
              id="task_description"
              value={formData.task_description}
              onChange={(e) => setFormData({...formData, task_description: e.target.value})}
              data-testid="client-task-description"
            />
          </div>

          <div>
            <Label htmlFor="comment">Коментар</Label>
            <Textarea
              id="comment"
              value={formData.comment}
              onChange={(e) => setFormData({...formData, comment: e.target.value})}
              data-testid="client-comment"
            />
          </div>

          <div>
            <Label>Статуси дій</Label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              {Object.entries(formData.action_status).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <Checkbox
                    id={`action_${key}`}
                    checked={value}
                    onCheckedChange={(checked) => 
                      setFormData({
                        ...formData, 
                        action_status: {...formData.action_status, [key]: checked}
                      })
                    }
                    data-testid={`action-status-${key}`}
                  />
                  <Label 
                    htmlFor={`action_${key}`} 
                    className="text-sm"
                    style={{ color: value ? getStatusColor(key, actionStatusTypes) : 'inherit' }}
                  >
                    {getStatusName(key)}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Скасувати
            </Button>
            <Button type="submit" data-testid="save-client-button">
              Зберегти
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Action Status Management Component
const ActionStatusManagement = ({ actionStatusTypes, onSave }) => {
  const [open, setOpen] = useState(false);
  const [newActionStatus, setNewActionStatus] = useState({ name: '', key: '', color: '#3B82F6' });
  const [editingActionStatus, setEditingActionStatus] = useState(null);

  const handleSave = async () => {
    try {
      if (editingActionStatus) {
        await axios.put(`${API}/action-status-types/${editingActionStatus.id}`, newActionStatus);
        toast.success('Статус дії оновлено');
      } else {
        await axios.post(`${API}/action-status-types`, newActionStatus);
        toast.success('Статус дії додано');
      }
      setNewActionStatus({ name: '', key: '', color: '#3B82F6' });
      setEditingActionStatus(null);
      setOpen(false);
      onSave();
    } catch (error) {
      console.error('Error saving action status:', error);
      toast.error('Помилка збереження статусу дії');
    }
  };

  const handleDelete = async (statusId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цей статус дії?')) {
      try {
        await axios.delete(`${API}/action-status-types/${statusId}`);
        toast.success('Статус дії видалено');
        onSave();
      } catch (error) {
        console.error('Error deleting action status:', error);
        toast.error('Помилка видалення статусу дії');
      }
    }
  };

  const startEdit = (actionStatus) => {
    setNewActionStatus({ name: actionStatus.name, key: actionStatus.key, color: actionStatus.color });
    setEditingActionStatus(actionStatus);
    setOpen(true);
  };

  const cancelEdit = () => {
    setNewActionStatus({ name: '', key: '', color: '#3B82F6' });
    setEditingActionStatus(null);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" data-testid="manage-action-status-types-button">
          Кольори статусів дій
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Управління кольорами статусів дій</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Add/Edit form */}
          <div className="border rounded-lg p-4 space-y-4">
            <h3 className="font-medium">
              {editingActionStatus ? 'Редагувати статус дії' : 'Додати новий статус дії'}
            </h3>
            <div className="grid grid-cols-3 gap-2">
              <Input
                placeholder="Назва статусу"
                value={newActionStatus.name}
                onChange={(e) => setNewActionStatus({...newActionStatus, name: e.target.value})}
                data-testid="action-status-name"
              />
              <Input
                placeholder="Ключ (made_order)"
                value={newActionStatus.key}
                onChange={(e) => setNewActionStatus({...newActionStatus, key: e.target.value})}
                data-testid="action-status-key"
              />
              <input
                type="color"
                value={newActionStatus.color}
                onChange={(e) => setNewActionStatus({...newActionStatus, color: e.target.value})}
                className="w-full h-10 border border-gray-300 rounded-md cursor-pointer"
                data-testid="action-status-color"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSave} disabled={!newActionStatus.name.trim() || !newActionStatus.key.trim()}>
                {editingActionStatus ? 'Оновити' : 'Додати'}
              </Button>
              {editingActionStatus && (
                <Button variant="outline" onClick={cancelEdit}>
                  Скасувати
                </Button>
              )}
            </div>
          </div>

          {/* Action status types list */}
          <div className="space-y-2">
            <h3 className="font-medium">Існуючі статуси дій</h3>
            {actionStatusTypes.map((actionStatus) => (
              <div key={actionStatus.id} className="flex items-center justify-between p-2 border rounded">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded" 
                    style={{ backgroundColor: actionStatus.color }}
                  />
                  <span>{actionStatus.name}</span>
                  <span className="text-xs text-gray-500">({actionStatus.key})</span>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => startEdit(actionStatus)}
                    data-testid={`edit-action-status-${actionStatus.id}`}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(actionStatus.id)}
                    data-testid={`delete-action-status-${actionStatus.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Action Status Popover Component
const ActionStatusPopover = ({ client, actionStatusTypes, onUpdate }) => {
  const [open, setOpen] = useState(false);
  const [statusState, setStatusState] = useState(client.action_status);
  const [saving, setSaving] = useState(false);

  // Update local state when client changes
  useEffect(() => {
    setStatusState(client.action_status);
  }, [client.action_status]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/clients/${client.id}`, {
        action_status: statusState
      });
      toast.success('Статуси дій оновлено');
      setOpen(false);
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating action status:', error);
      toast.error('Помилка оновлення статусів');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = (statusKey, checked) => {
    setStatusState(prev => ({
      ...prev,
      [statusKey]: checked
    }));
  };

  const activeStatuses = Object.entries(statusState).filter(([key, value]) => value);
  const hasStatuses = activeStatuses.length > 0;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-auto min-h-8 py-1 px-2 flex flex-wrap gap-1 justify-start"
          data-testid={`action-status-trigger-${client.id}`}
        >
          {hasStatuses ? (
            <div className="flex flex-wrap gap-1">
              {activeStatuses.map(([key, value]) => (
                <Badge 
                  key={key}
                  style={{ backgroundColor: getStatusColor(key, actionStatusTypes), color: 'white' }}
                  className="text-xs py-0 px-1 h-5"
                >
                  {getStatusName(key)}
                </Badge>
              ))}
            </div>
          ) : (
            <span className="text-gray-400 text-xs">Натисніть для вибору</span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" data-testid={`action-status-popover-${client.id}`}>
        <div className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">
              Статуси дій для {client.first_name} {client.last_name}
            </h4>
            <p className="text-sm text-muted-foreground">
              Оберіть статуси дій для цього клієнта
            </p>
          </div>
          
          <div className="space-y-3">
            {Object.entries(statusState).map(([key, value]) => (
              <div key={key} className="flex items-center space-x-2">
                <Checkbox
                  id={`${client.id}-${key}`}
                  checked={value}
                  onCheckedChange={(checked) => handleStatusChange(key, checked)}
                  data-testid={`status-checkbox-${key}-${client.id}`}
                />
                <Label 
                  htmlFor={`${client.id}-${key}`}
                  className="text-sm cursor-pointer flex items-center gap-2"
                >
                  <div 
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: getStatusColor(key, actionStatusTypes) }}
                  />
                  {getStatusName(key)}
                </Label>
              </div>
            ))}
          </div>
          
          <div className="flex justify-between pt-2 border-t">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                setStatusState(client.action_status);
                setOpen(false);
              }}
              data-testid={`cancel-status-${client.id}`}
            >
              Скасувати
            </Button>
            <Button 
              size="sm" 
              onClick={handleSave}
              disabled={saving}
              data-testid={`save-status-${client.id}`}
            >
              {saving ? 'Збереження...' : 'Зберегти'}
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};

// Comment Cell Component
const CommentCell = ({ client, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [comment, setComment] = useState(client.comment || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (saving) return;
    
    setSaving(true);
    try {
      await axios.patch(`${API}/clients/${client.id}/comment`, { comment });
      toast.success('Коментар оновлено');
      setIsEditing(false);
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating comment:', error);
      toast.error('Помилка оновлення коментаря');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setComment(client.comment || '');
    setIsEditing(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className="min-w-48 max-w-64">
        <Textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Введіть коментар..."
          className="text-xs min-h-16 resize-none"
          data-testid={`comment-input-${client.id}`}
          autoFocus
        />
        <div className="flex gap-1 mt-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleSave}
            disabled={saving}
            className="h-6 px-2 text-xs"
            data-testid={`save-comment-${client.id}`}
          >
            {saving ? '...' : '💾'}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleCancel}
            className="h-6 px-2 text-xs"
            data-testid={`cancel-comment-${client.id}`}
          >
            ✕
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-w-48 max-w-64 cursor-pointer hover:bg-gray-50 p-1 rounded text-xs"
      onClick={() => setIsEditing(true)}
      data-testid={`comment-display-${client.id}`}
    >
      {client.comment ? (
        <div className="text-gray-700 line-clamp-3 whitespace-pre-wrap">
          {client.comment}
        </div>
      ) : (
        <div className="text-gray-400 italic">
          Клікніть для додавання коментаря...
        </div>
      )}
    </div>
  );
};

// Status Type Management Component
const StatusTypeManagement = ({ 
  statusTypes, 
  newStatusType, 
  setNewStatusType, 
  editingStatusType, 
  setEditingStatusType,
  onSave, 
  onDelete 
}) => {
  const [open, setOpen] = useState(false);

  const handleSave = () => {
    onSave();
    setOpen(false);
  };

  const startEdit = (statusType) => {
    setNewStatusType({ name: statusType.name, color: statusType.color });
    setEditingStatusType(statusType);
    setOpen(true);
  };

  const cancelEdit = () => {
    setNewStatusType({ name: '', color: '#3B82F6' });
    setEditingStatusType(null);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" data-testid="manage-status-types-button">
          Управління статусами
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Управління статусами клієнтів</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Add/Edit form */}
          <div className="border rounded-lg p-4 space-y-4">
            <h3 className="font-medium">
              {editingStatusType ? 'Редагувати статус' : 'Додати новий статус'}
            </h3>
            <div className="flex gap-2">
              <Input
                placeholder="Назва статусу"
                value={newStatusType.name}
                onChange={(e) => setNewStatusType({...newStatusType, name: e.target.value})}
                data-testid="status-type-name"
              />
              <input
                type="color"
                value={newStatusType.color}
                onChange={(e) => setNewStatusType({...newStatusType, color: e.target.value})}
                className="w-20 h-10 border border-gray-300 rounded-md cursor-pointer"
                data-testid="status-type-color"
              />
              <Button onClick={handleSave} disabled={!newStatusType.name.trim()}>
                {editingStatusType ? 'Оновити' : 'Додати'}
              </Button>
              {editingStatusType && (
                <Button variant="outline" onClick={cancelEdit}>
                  Скасувати
                </Button>
              )}
            </div>
          </div>

          {/* Status types list */}
          <div className="space-y-2">
            <h3 className="font-medium">Існуючі статуси</h3>
            {statusTypes.map((statusType) => (
              <div key={statusType.id} className="flex items-center justify-between p-2 border rounded">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded" 
                    style={{ backgroundColor: statusType.color }}
                  />
                  <span>{statusType.name}</span>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => startEdit(statusType)}
                    data-testid={`edit-status-type-${statusType.id}`}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(statusType.id)}
                    data-testid={`delete-status-type-${statusType.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Daily Reports Page
const DailyReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingReport, setEditingReport] = useState(null);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/daily-reports`);
      setReports(response.data);
    } catch (error) {
      console.error('Error loading reports:', error);
      toast.error('Помилка завантаження звітів');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReport = async (reportData) => {
    try {
      if (editingReport) {
        await axios.put(`${API}/daily-reports/${editingReport.id}`, reportData);
        toast.success('Звіт оновлено');
      } else {
        await axios.post(`${API}/daily-reports`, reportData);
        toast.success('Звіт додано');
      }
      setEditingReport(null);
      loadReports();
    } catch (error) {
      console.error('Error saving report:', error);
      toast.error('Помилка збереження звіту');
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цей звіт?')) {
      try {
        await axios.delete(`${API}/daily-reports/${reportId}`);
        toast.success('Звіт видалено');
        loadReports();
      } catch (error) {
        console.error('Error deleting report:', error);
        toast.error('Помилка видалення звіту');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Щоденні звіти</h1>
        <ReportDialog 
          report={editingReport}
          onSave={handleSaveReport}
          onCancel={() => setEditingReport(null)}
          trigger={
            <Button data-testid="add-report-button">
              <Plus className="w-4 h-4 mr-2" />
              Додати звіт
            </Button>
          }
        />
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Дата</TableHead>
                  <TableHead>Замовлення на комплектації</TableHead>
                  <TableHead>Наборів, шт</TableHead>
                  <TableHead>Сума замовлень</TableHead>
                  <TableHead>Заведено коштів</TableHead>
                  <TableHead>Спроби дзвінків</TableHead>
                  <TableHead>Дзвінки</TableHead>
                  <TableHead>Дії</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">
                      {format(new Date(report.date), 'dd.MM.yyyy')}
                    </TableCell>
                    <TableCell>{report.orders_in_assembly}</TableCell>
                    <TableCell>{report.sets_count}</TableCell>
                    <TableCell>{report.orders_amount} ₴</TableCell>
                    <TableCell>{report.money_received_today} ₴</TableCell>
                    <TableCell>{report.call_attempts}</TableCell>
                    <TableCell>{report.successful_calls}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingReport(report)}
                          data-testid={`edit-report-${report.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteReport(report.id)}
                          data-testid={`delete-report-${report.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Report Dialog Component
const ReportDialog = ({ report, onSave, onCancel, trigger }) => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date(),
    orders_in_assembly: 0,
    sets_count: 0,
    orders_amount: 0,
    money_received_today: 0,
    call_attempts: 0,
    successful_calls: 0,
    self_messaged_client: 0,
    responses: 0,
    chats_today: 0,
    clients_no_order: 0,
    comment: ''
  });

  useEffect(() => {
    if (report) {
      setFormData({
        ...report,
        date: new Date(report.date)
      });
      setOpen(true);
    }
  }, [report]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      date: format(formData.date, 'yyyy-MM-dd')
    };
    onSave(submitData);
    setOpen(false);
    if (onCancel) onCancel();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {report ? 'Редагувати звіт' : 'Додати звіт'}
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Дата</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                  data-testid="report-date"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {formData.date ? format(formData.date, 'PPP') : 'Оберіть дату'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={formData.date}
                  onSelect={(date) => setFormData({...formData, date})}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="orders_in_assembly">Замовлення на комплектації</Label>
              <Input
                id="orders_in_assembly"
                type="number"
                value={formData.orders_in_assembly}
                onChange={(e) => setFormData({...formData, orders_in_assembly: parseInt(e.target.value) || 0})}
                data-testid="report-orders-assembly"
              />
            </div>
            <div>
              <Label htmlFor="sets_count">Наборів, шт</Label>
              <Input
                id="sets_count"
                type="number"
                value={formData.sets_count}
                onChange={(e) => setFormData({...formData, sets_count: parseInt(e.target.value) || 0})}
                data-testid="report-sets-count"
              />
            </div>
            <div>
              <Label htmlFor="orders_amount">Сума замовлень</Label>
              <Input
                id="orders_amount"
                type="number"
                step="0.01"
                value={formData.orders_amount}
                onChange={(e) => setFormData({...formData, orders_amount: parseFloat(e.target.value) || 0})}
                data-testid="report-orders-amount"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="money_received_today">Заведено коштів за день</Label>
              <Input
                id="money_received_today"
                type="number"
                step="0.01"
                value={formData.money_received_today}
                onChange={(e) => setFormData({...formData, money_received_today: parseFloat(e.target.value) || 0})}
                data-testid="report-money-received"
              />
            </div>
            <div>
              <Label htmlFor="call_attempts">Спроб дзвонити</Label>
              <Input
                id="call_attempts"
                type="number"
                value={formData.call_attempts}
                onChange={(e) => setFormData({...formData, call_attempts: parseInt(e.target.value) || 0})}
                data-testid="report-call-attempts"
              />
            </div>
            <div>
              <Label htmlFor="successful_calls">Дзвінків</Label>
              <Input
                id="successful_calls"
                type="number"
                value={formData.successful_calls}
                onChange={(e) => setFormData({...formData, successful_calls: parseInt(e.target.value) || 0})}
                data-testid="report-successful-calls"
              />
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div>
              <Label htmlFor="self_messaged_client">Сам написав клієнту</Label>
              <Input
                id="self_messaged_client"
                type="number"
                value={formData.self_messaged_client}
                onChange={(e) => setFormData({...formData, self_messaged_client: parseInt(e.target.value) || 0})}
                data-testid="report-self-messaged"
              />
            </div>
            <div>
              <Label htmlFor="responses">Відповідей</Label>
              <Input
                id="responses"
                type="number"
                value={formData.responses}
                onChange={(e) => setFormData({...formData, responses: parseInt(e.target.value) || 0})}
                data-testid="report-responses"
              />
            </div>
            <div>
              <Label htmlFor="chats_today">Чатів за день</Label>
              <Input
                id="chats_today"
                type="number"
                value={formData.chats_today}
                onChange={(e) => setFormData({...formData, chats_today: parseInt(e.target.value) || 0})}
                data-testid="report-chats-today"
              />
            </div>
            <div>
              <Label htmlFor="clients_no_order">Клієнти без замовлення</Label>
              <Input
                id="clients_no_order"
                type="number"
                value={formData.clients_no_order}
                onChange={(e) => setFormData({...formData, clients_no_order: parseInt(e.target.value) || 0})}
                data-testid="report-clients-no-order"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="comment">Коментар</Label>
            <Textarea
              id="comment"
              value={formData.comment}
              onChange={(e) => setFormData({...formData, comment: e.target.value})}
              data-testid="report-comment"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Скасувати
            </Button>
            <Button type="submit" data-testid="save-report-button">
              Зберегти
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// App Content Component (needs to be inside Router)
const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <>
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <Routes>
          <Route path="/" element={<ClientsPage />} />
          <Route path="/daily-reports" element={<DailyReportsPage />} />
          <Route path="/auth" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App min-h-screen bg-gray-50">
        <Router>
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/*" element={<AppContent />} />
          </Routes>
        </Router>
      </div>
    </AuthProvider>
  );
}

export default App;