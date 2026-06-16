//配置
const CONFIG = {
  // 开发阶段设为 true，使用 Mock 数据；联调时改为 false
  USE_MOCK: false,

  // Mock 延迟（模拟网络请求，单位 ms）
  MOCK_DELAY: 300,

  // API 基础路径（与 Nginx 同源，使用相对路径）
  API_BASE: '/api',
};

//当前登录用户（由 /api/me/ 填充）
let currentUser = null;

// 1. Mock 数据（所有接口的假数据）
const MOCK_DATA = {
  //用户
  users: [
    { id: 1, username: 'admin', nickname: '管理员', is_admin: 1 },
    { id: 2, username: 'test', nickname: '测试用户', is_admin: 0 },
  ],

  //餐馆
  restaurants: [
    { id: 1, name: '沙县小吃', category: 'snack', avg_price: 20, weight: 6, is_active: 1, is_deleted: 0, draw_count: 12, created_at: '2026-06-01 10:00:00' },
    { id: 2, name: '海底捞', category: 'hotpot', avg_price: 120, weight: 2, is_active: 1, is_deleted: 0, draw_count: 3, created_at: '2026-06-01 10:00:00' },
    { id: 3, name: '肯德基', category: 'fastfood', avg_price: 35, weight: 4, is_active: 1, is_deleted: 0, draw_count: 8, created_at: '2026-06-01 10:00:00' },
    { id: 4, name: '川菜馆', category: 'chinese', avg_price: 60, weight: 3, is_active: 1, is_deleted: 0, draw_count: 5, created_at: '2026-06-01 10:00:00' },
    { id: 5, name: '烤肉店', category: 'western', avg_price: 88, weight: 2, is_active: 1, is_deleted: 0, draw_count: 4, created_at: '2026-06-01 10:00:00' },
    { id: 6, name: '兰州拉面', category: 'snack', avg_price: 15, weight: 5, is_active: 1, is_deleted: 0, draw_count: 9, created_at: '2026-06-01 10:00:00' },
    { id: 7, name: '黄焖鸡米饭', category: 'fastfood', avg_price: 18, weight: 4, is_active: 1, is_deleted: 0, draw_count: 6, created_at: '2026-06-01 10:00:00' },
  ],

  //历史
  history: [
    { id: 1, restaurant_id: 1, restaurant_name: '沙县小吃', drawn_at: '2026-06-16 19:30:00' },
    { id: 2, restaurant_id: 3, restaurant_name: '肯德基', drawn_at: '2026-06-16 18:20:00' },
    { id: 3, restaurant_id: 6, restaurant_name: '兰州拉面', drawn_at: '2026-06-16 12:10:00' },
    { id: 4, restaurant_id: 2, restaurant_name: '海底捞', drawn_at: '2026-06-15 20:00:00' },
    { id: 5, restaurant_id: 4, restaurant_name: '川菜馆', drawn_at: '2026-06-15 19:00:00' },
    { id: 6, restaurant_id: 1, restaurant_name: '沙县小吃', drawn_at: '2026-06-15 12:30:00' },
    { id: 7, restaurant_id: 5, restaurant_name: '烤肉店', drawn_at: '2026-06-14 20:00:00' },
    { id: 8, restaurant_id: 7, restaurant_name: '黄焖鸡米饭', drawn_at: '2026-06-14 18:45:00' },
    { id: 9, restaurant_id: 3, restaurant_name: '肯德基', drawn_at: '2026-06-14 12:00:00' },
    { id: 10, restaurant_id: 6, restaurant_name: '兰州拉面', drawn_at: '2026-06-13 19:30:00' },
  ],
};

// 自增 ID 计数（用于 Mock 新增）
let _mockRestaurantId = 10;
let _mockHistoryId = 11;

// 2. Mock 响应分发器
function mockResponse(url, options = {}) {
  const method = options.method || 'GET';
  const body = options.body ? JSON.parse(options.body) : {};

  // 解析路径（去除 API_BASE 前缀）
  const path = url.replace(CONFIG.API_BASE, '').split('?')[0];

  return new Promise((resolve) => {
    setTimeout(() => {
      let result = mockDispatch(path, method, body, url);
      resolve(result);
    }, CONFIG.MOCK_DELAY);
  });
}

function mockDispatch(path, method, body, fullUrl) {
  // 用户相关
  if (path === '/me/' && method === 'GET') {
    return mockMe();
  }
  if (path === '/login/' && method === 'POST') {
    return mockLogin(body);
  }
  if (path === '/register/' && method === 'POST') {
    return mockRegister(body);
  }
  if (path === '/logout/' && method === 'POST') {
    return mockLogout();
  }

  //餐馆相关
  if (path === '/restaurants/' && method === 'GET') {
    return mockRestaurants(fullUrl);
  }
  if (path === '/restaurants/' && method === 'POST') {
    return mockRestaurantCreate(body);
  }
  // 路径匹配：/restaurants/{id}/
  const editMatch = path.match(/^\/restaurants\/(\d+)\/$/);
  if (editMatch) {
    const id = parseInt(editMatch[1]);
    if (method === 'PUT') {
      return mockRestaurantUpdate(id, body);
    }
    if (method === 'DELETE') {
      return mockRestaurantDelete(id);
    }
  }
  // Toggle：/restaurants/{id}/toggle/
  const toggleMatch = path.match(/^\/restaurants\/(\d+)\/toggle\/$/);
  if (toggleMatch && method === 'PATCH') {
    return mockRestaurantToggle(parseInt(toggleMatch[1]), body);
  }

  //随机抽取
  if (path === '/random-dinner/' && method === 'POST') {
    return mockRandomDinner(body);
  }

  //历史
  if (path === '/history/' && method === 'GET') {
    return mockHistory(fullUrl);
  }

  // 未匹配的路径，返回 404
  return {
    code: 404,
    msg: 'Mock: 接口未定义',
    data: null
  };
}

// 3. Mock 各接口实现

//当前用户
function mockMe() {
  if (currentUser) {
    return {
      code: 200,
      msg: '操作成功',
      data: currentUser
    };
  }
  return {
    code: 4010,
    msg: '未登录',
    data: null
  };
}

//登录
function mockLogin(body) {
  const user = MOCK_DATA.users.find(u => u.username === body.username);
  if (!user) {
    return { code: 4002, msg: '账号或密码错误', data: null };
  }
  // 简单密码校验（Mock 不加密，明文比对）
  // 实际后端用 make_password 加密，这里简化
  if (body.password !== '123456' && body.password !== 'admin123') {
    return { code: 4002, msg: '账号或密码错误', data: null };
  }
  currentUser = { ...user };
  return {
    code: 200,
    msg: '操作成功',
    data: {
      user_id: user.id,
      nickname: user.nickname,
      is_admin: user.is_admin
    }
  };
}

//注册
function mockRegister(body) {
  if (MOCK_DATA.users.find(u => u.username === body.username)) {
    return { code: 4001, msg: '用户名已存在', data: null };
  }
  if (!body.username || body.username.length < 1) {
    return { code: 4000, msg: '用户名格式非法', data: null };
  }
  if (!body.password || body.password.length < 6) {
    return { code: 4000, msg: '密码长度至少6位', data: null };
  }
  const newUser = {
    id: MOCK_DATA.users.length + 1,
    username: body.username,
    nickname: body.nickname || body.username,
    is_admin: 0
  };
  MOCK_DATA.users.push(newUser);
  return {
    code: 200,
    msg: '操作成功',
    data: { user_id: newUser.id, username: newUser.username }
  };
}

//登出
function mockLogout() {
  currentUser = null;
  return { code: 200, msg: '操作成功', data: null };
}

//餐馆列表
function mockRestaurants(fullUrl) {
  const url = new URL(fullUrl, 'http://mock');
  const category = url.searchParams.get('category') || '';
  const isActive = url.searchParams.get('is_active');
  const page = parseInt(url.searchParams.get('page') || '1');
  const pageSize = parseInt(url.searchParams.get('page_size') || '10');

  let list = MOCK_DATA.restaurants.filter(r => !r.is_deleted);

  if (category) {
    list = list.filter(r => r.category === category);
  }
  if (isActive !== null) {
    list = list.filter(r => r.is_active === parseInt(isActive));
  }

  // 按 weight 降序，id 升序
  list.sort((a, b) => b.weight - a.weight || a.id - b.id);

  const total = list.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paged = list.slice(start, end);

  return {
    code: 200,
    msg: '操作成功',
    data: {
      total: total,
      page: page,
      page_size: pageSize,
      list: paged
    }
  };
}

//新增餐馆
function mockRestaurantCreate(body) {
  // 校验权重
  if (body.weight < 1 || body.weight > 100) {
    return { code: 4005, msg: '权重需为1~100的整数', data: null };
  }
  const newItem = {
    id: ++_mockRestaurantId,
    name: body.name,
    category: body.category || 'other',
    avg_price: body.avg_price || 0,
    weight: body.weight || 1,
    is_active: body.is_active !== undefined ? body.is_active : 1,
    is_deleted: 0,
    draw_count: 0,
    created_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
  };
  MOCK_DATA.restaurants.push(newItem);
  return {
    code: 200,
    msg: '操作成功',
    data: {
      id: newItem.id,
      name: newItem.name,
      weight: newItem.weight,
      is_active: newItem.is_active
    }
  };
}

//编辑餐馆
function mockRestaurantUpdate(id, body) {
  const idx = MOCK_DATA.restaurants.findIndex(r => r.id === id);
  if (idx === -1 || MOCK_DATA.restaurants[idx].is_deleted) {
    return { code: 4006, msg: '资源不存在', data: null };
  }
  if (body.weight < 1 || body.weight > 100) {
    return { code: 4005, msg: '权重需为1~100的整数', data: null };
  }
  const item = MOCK_DATA.restaurants[idx];
  Object.assign(item, {
    name: body.name || item.name,
    category: body.category || item.category,
    avg_price: body.avg_price !== undefined ? body.avg_price : item.avg_price,
    weight: body.weight || item.weight,
    is_active: body.is_active !== undefined ? body.is_active : item.is_active
  });
  return {
    code: 200,
    msg: '操作成功',
    data: {
      id: item.id,
      name: item.name,
      weight: item.weight,
      is_active: item.is_active
    }
  };
}

//删除餐馆（软删除）
function mockRestaurantDelete(id) {
  const idx = MOCK_DATA.restaurants.findIndex(r => r.id === id);
  if (idx === -1 || MOCK_DATA.restaurants[idx].is_deleted) {
    return { code: 4006, msg: '资源不存在', data: null };
  }
  MOCK_DATA.restaurants[idx].is_deleted = 1;
  return {
    code: 200,
    msg: '操作成功',
    data: { id: id, deleted: true }
  };
}

//启用/禁用
function mockRestaurantToggle(id, body) {
  const idx = MOCK_DATA.restaurants.findIndex(r => r.id === id);
  if (idx === -1 || MOCK_DATA.restaurants[idx].is_deleted) {
    return { code: 4006, msg: '资源不存在', data: null };
  }
  MOCK_DATA.restaurants[idx].is_active = body.is_active;
  return {
    code: 200,
    msg: '操作成功',
    data: { id: id, is_active: body.is_active }
  };
}

//随机抽取
function mockRandomDinner(body) {
  const category = body.category || '';
  let pool = MOCK_DATA.restaurants.filter(r => r.is_active && !r.is_deleted);
  if (category) {
    pool = pool.filter(r => r.category === category);
  }
  if (pool.length === 0) {
    return { code: 4004, msg: '无可用候选', data: null };
  }

  // 按权重随机
  const totalWeight = pool.reduce((s, r) => s + r.weight, 0);
  let rand = Math.random() * totalWeight;
  let chosen = pool[0];
  for (const r of pool) {
    rand -= r.weight;
    if (rand <= 0) { chosen = r; break; }
  }

  // 更新 draw_count
  const idx = MOCK_DATA.restaurants.findIndex(r => r.id === chosen.id);
  if (idx !== -1) {
    MOCK_DATA.restaurants[idx].draw_count += 1;
  }

  // 写入历史
  const historyItem = {
    id: ++_mockHistoryId,
    restaurant_id: chosen.id,
    restaurant_name: chosen.name,
    drawn_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
  };
  MOCK_DATA.history.unshift(historyItem);

  return {
    code: 200,
    msg: '今晚就吃它！',
    data: {
      restaurant_id: chosen.id,
      name: chosen.name,
      category: chosen.category,
      avg_price: chosen.avg_price,
      weight: chosen.weight,
      history_id: historyItem.id,
      drawn_at: historyItem.drawn_at
    }
  };
}

//历史列表
function mockHistory(fullUrl) {
  const url = new URL(fullUrl, 'http://mock');
  const page = parseInt(url.searchParams.get('page') || '1');
  const pageSize = parseInt(url.searchParams.get('page_size') || '10');

  const list = MOCK_DATA.history.slice();
  const total = list.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paged = list.slice(start, end);

  return {
    code: 200,
    msg: '操作成功',
    data: {
      total: total,
      page: page,
      page_size: pageSize,
      list: paged
    }
  };
}

// 4. 对外暴露的 API 函数（自动切换 Mock / 真实）

/**
 * 统一 API 请求
 * @param {string} url - 接口路径（如 '/api/login/'）
 * @param {object} options - fetch 选项（method, body, headers 等）
 * @returns {Promise} 解析后的 JSON 数据
 */
export async function apiFetch(url, options = {}) {
  // 确保 url 以 /api/ 开头
  const fullUrl = url.startsWith('/api/') ? url : `/api${url}`;

  const fetchOptions = {
    ...options,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  };

  if (CONFIG.USE_MOCK) {
    return mockResponse(fullUrl, options);
  }

  try {
    const response = await fetch(fullUrl, fetchOptions);
    return await response.json();
  } catch (error) {
    console.error('[API] 网络错误:', error);
    return {
      code: 5000,
      msg: '网络异常，请检查后端服务',
      data: null
    };
  }
}

// 5. Toast 消息系统

let toastTimer = null;

/**
 * 显示全局 Toast 消息
 * @param {string} message - 消息内容
 * @param {string} type - 类型: 'success' | 'error' | 'warning' | 'info'
 * @param {number} duration - 显示时长（ms），默认 3000
 */
export function showToast(message, type = 'info', duration = 3000) {
  const containerId = 'toast-container';
  let container = document.getElementById(containerId);

  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  // 自动移除
  setTimeout(() => {
    toast.classList.add('toast-out');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, duration);
}

// 6. 工具函数

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 格式，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string}
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  const d = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(d.getTime())) return '-';

  const pad = (n) => String(n).padStart(2, '0');
  const map = {
    'YYYY': d.getFullYear(),
    'MM': pad(d.getMonth() + 1),
    'DD': pad(d.getDate()),
    'HH': pad(d.getHours()),
    'mm': pad(d.getMinutes()),
    'ss': pad(d.getSeconds()),
  };
  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (m) => map[m]);
}

/**
 * 获取分类对应的 Emoji
 * @param {string} category - 分类标识
 * @returns {string}
 */
export function getCategoryEmoji(category) {
  const map = {
    fastfood: '🍔',
    hotpot: '🍲',
    snack: '🍜',
    chinese: '🍱',
    western: '🍝',
    other: '🍽️'
  };
  return map[category] || '🍽️';
}

/**
 * 获取分类的中文名称
 * @param {string} category - 分类标识
 * @returns {string}
 */
export function getCategoryLabel(category) {
  const map = {
    fastfood: '快餐',
    hotpot: '火锅',
    snack: '小吃',
    chinese: '中餐',
    western: '西餐',
    other: '其他'
  };
  return map[category] || category;
}

/**
 * 颜色变亮（用于渐变）
 * @param {string} hex - 十六进制颜色
 * @param {number} percent - 变亮百分比
 * @returns {string}
 */
export function lightenColor(hex, percent = 40) {
  let h = hex.replace("#", "");
  if (h.length === 3) {
    h = h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
  }
  const num = parseInt(h, 16);
  const r = Math.min(255, (num >> 16) + percent);
  const g = Math.min(255, ((num >> 8) & 0xFF) + percent);
  const b = Math.min(255, (num & 0xFF) + percent);
  const toHex = (c) => c.toString(16).padStart(2, "0");
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * 获取当前登录用户信息（从缓存或接口）
 * @returns {Promise<object|null>}
 */
export async function getCurrentUser() {
  if (currentUser) return currentUser;
  const data = await apiFetch('/api/me/');
  if (data.code === 200) {
    currentUser = data.data;
    return currentUser;
  }
  return null;
}

/**
 * 检查登录状态，未登录则跳转
 * @param {string} redirectUrl - 跳转目标，默认 '/login.html'
 * @returns {Promise<boolean>}
 */
export async function requireLogin(redirectUrl = '/login.html') {
  const user = await getCurrentUser();
  if (!user) {
    const next = encodeURIComponent(window.location.pathname);
    window.location.href = `${redirectUrl}?next=${next}`;
    return false;
  }
  return true;
}

/**
 * 退出登录
 * @returns {Promise<boolean>}
 */
export async function doLogout() {
  const data = await apiFetch('/api/logout/', { method: 'POST' });
  if (data.code === 200) {
    currentUser = null;
    return true;
  }
  return false;
}

// 7. 导出（兼容 ES Module 和 普通 script）

// 如果是 ES Module 环境
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    apiFetch,
    showToast,
    formatDate,
    getCategoryEmoji,
    getCategoryLabel,
    lightenColor,
    getCurrentUser,
    requireLogin,
    doLogout,
    CONFIG,
  };
}

// 浏览器全局挂载（方便非模块化页面使用）
if (typeof window !== 'undefined') {
  window.__common = {
    apiFetch,
    showToast,
    formatDate,
    getCategoryEmoji,
    getCategoryLabel,
    lightenColor,
    getCurrentUser,
    requireLogin,
    doLogout,
    CONFIG,
  };
}
