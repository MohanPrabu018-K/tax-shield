import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Backend (FastAPI/Pydantic) serializes Mongo ids as `_id`; the frontend
// types use `id`. Normalize once here so every list key and every
// update/delete id-match works instead of silently comparing undefined.
function normalize<T>(value: T): T {
  if (Array.isArray(value)) return value.map(normalize) as unknown as T;
  if (value && typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj)) out[k] = normalize(v);
    if (typeof out._id === 'string' && typeof out.id !== 'string') out.id = out._id;
    return out as T;
  }
  return value;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/login', { email, password });
    return normalize(response.data);
  }

  async register(data: { email: string; password: string; name: string }) {
    const response = await this.client.post('/register', data);
    return normalize(response.data);
  }

  async getCurrentUser() {
    const response = await this.client.get('/me');
    return normalize(response.data);
  }

  async getTransactions() {
    const response = await this.client.get('/transactions');
    return normalize(response.data);
  }

  async getTransactionsPaginated(skip = 0, limit = 20) {
    const response = await this.client.get(`/transactions?skip=${skip}&limit=${limit}`);
    return normalize(response.data);
  }

  async createTransaction(data: any) {
    const response = await this.client.post('/transactions', data);
    return normalize(response.data);
  }

  async uploadTransactionsCsv(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/transactions/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return normalize(response.data);
  }

  async deleteTransaction(id: string) {
    const response = await this.client.delete(`/transactions/${id}`);
    return normalize(response.data);
  }

  async getInvestments() {
    const response = await this.client.get('/investments');
    return normalize(response.data);
  }

  async createInvestment(data: any) {
    const response = await this.client.post('/investments', data);
    return normalize(response.data);
  }

  async getDeductions() {
    const response = await this.client.get('/deductions');
    return normalize(response.data);
  }

  async createDeduction(data: any) {
    const response = await this.client.post('/deductions', data);
    return normalize(response.data);
  }

  async uploadDocument(file: File, data: any) {
    const formData = new FormData();
    formData.append('file', file);
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, String(value));
      }
    });
    const response = await this.client.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return normalize(response.data);
  }

  async getDocuments() {
    const response = await this.client.get('/documents');
    return normalize(response.data);
  }

  downloadDocumentUrl(id: string) {
    return `${API_URL}/documents/${id}/download`;
  }

  async deleteDocument(id: string) {
    const response = await this.client.delete(`/documents/${id}`);
    return response.data;
  }

  async verifyDocument(id: string, to: string, notes = '') {
    const response = await this.client.patch(`/documents/${id}/verify`, { to, notes });
    return normalize(response.data);
  }

  async getObligations() {
    const response = await this.client.get('/obligations');
    return normalize(response.data);
  }

  async updateObligationStatus(id: string, status: string) {
    const response = await this.client.patch(`/obligations/${id}`, { status });
    return normalize(response.data);
  }

  async getDeadlines() {
    const response = await this.client.get('/deadlines');
    return normalize(response.data);
  }

  async updateDeadlineStatus(id: string, is_completed: boolean) {
    const response = await this.client.patch(`/deadlines/${id}`, { is_completed });
    return normalize(response.data);
  }

  async getScenarios() {
    const response = await this.client.get('/scenarios');
    return normalize(response.data);
  }

  async createScenario(data: any) {
    const response = await this.client.post('/scenarios', data);
    return normalize(response.data);
  }

  async compareScenarios(scenarioIds: string[]) {
    const response = await this.client.post('/scenarios/compare', { scenario_ids: scenarioIds });
    return normalize(response.data);
  }

  async getDashboard(regime: string = 'old') {
    const response = await this.client.get(`/dashboard?regime=${regime}`);
    return normalize(response.data);
  }

  async getReadinessScore() {
    const response = await this.client.get('/readiness-score');
    return normalize(response.data);
  }

  async seedDemoData() {
    const response = await this.client.get('/demo/seed');
    return normalize(response.data);
  }

  async getTaxPayments() {
    const response = await this.client.get('/tax-payments');
    return normalize(response.data);
  }

  async createTaxPayment(data: any) {
    const response = await this.client.post('/tax-payments', data);
    return normalize(response.data);
  }

  async getAisRecords() {
    const response = await this.client.get('/ais-records');
    return normalize(response.data);
  }

  async createAisRecord(data: any) {
    const response = await this.client.post('/ais-records', data);
    return normalize(response.data);
  }

  async getForm26ASRecords() {
    const response = await this.client.get('/form26as-records');
    return normalize(response.data);
  }

  async createForm26ASRecord(data: any) {
    const response = await this.client.post('/form26as-records', data);
    return normalize(response.data);
  }

  async getReconciliation() {
    const response = await this.client.get('/reconciliation');
    return normalize(response.data);
  }

  async getRisks() {
    const response = await this.client.get('/risks');
    return normalize(response.data);
  }

  async getActions() {
    const response = await this.client.get('/actions');
    return normalize(response.data);
  }

  async getTaxDetail(regime: string = 'old') {
    const response = await this.client.get(`/tax-detail?regime=${regime}`);
    return normalize(response.data);
  }

  async chatMessage(message: string) {
    const response = await this.client.post('/chat/message', { message });
    return normalize(response.data);
  }

  async chatHistory(limit = 50) {
    const response = await this.client.get(`/chat/history?limit=${limit}`);
    return normalize(response.data);
  }

  async voiceTranscribe(transcript: string, lang?: string) {
    const response = await this.client.post('/chat/voice/transcribe', { transcript, lang });
    return normalize(response.data);
  }

  async voiceSynthesize(text: string) {
    const response = await this.client.post('/chat/voice/synthesize', { text });
    return normalize(response.data);
  }

  async chatScenario(extra_deduction: number = 50000) {
    const response = await this.client.post('/chat/scenario', { extra_deduction });
    return normalize(response.data);
  }

  // ---- Phases 3-13: SaaS modules ----
  async ensureAccounts() {
    const response = await this.client.post('/accounts/ensure-seed', {});
    return normalize(response.data);
  }

  async getAccounts() {
    const response = await this.client.get('/accounts');
    return normalize(response.data);
  }

  async postJournal(data: any, idempotencyKey?: string) {
    const response = await this.client.post('/journals',
      { ...data, idempotency_key: idempotencyKey },
      { headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined });
    return normalize(response.data);
  }

  async getJournals(skip = 0, limit = 100) {
    const response = await this.client.get(`/journals?skip=${skip}&limit=${limit}`);
    return normalize(response.data);
  }

  async reverseJournal(id: string, narration = '') {
    const response = await this.client.post(`/journals/${id}/reverse`, { narration });
    return normalize(response.data);
  }

  async getLedger(code: string) {
    const response = await this.client.get(`/ledger/${code}`);
    return normalize(response.data);
  }

  async getTrialBalance() {
    const response = await this.client.get('/trial-balance');
    return normalize(response.data);
  }

  async getProfitLoss() {
    const response = await this.client.get('/reports/profit-loss');
    return normalize(response.data);
  }

  async getBalanceSheet() {
    const response = await this.client.get('/reports/balance-sheet');
    return normalize(response.data);
  }

  async getCashFlow() {
    const response = await this.client.get('/reports/cash-flow');
    return normalize(response.data);
  }

  async createParty(data: any) {
    const response = await this.client.post('/parties', data);
    return normalize(response.data);
  }

  async getParties(kind?: string) {
    const response = await this.client.get(kind ? `/parties?kind=${kind}` : '/parties');
    return normalize(response.data);
  }

  async deleteParty(id: string) {
    const response = await this.client.delete(`/parties/${id}`);
    return normalize(response.data);
  }

  async analyzeImport(rows: any[]) {
    const response = await this.client.post('/imports/analyze', { rows });
    return normalize(response.data);
  }

  async suggestCategory(description: string, transaction_type = 'expense') {
    const response = await this.client.post('/categorize/suggest', { description, transaction_type });
    return normalize(response.data);
  }

  async getReceivablesPayables() {
    const response = await this.client.get('/finance/receivables-payables');
    return normalize(response.data);
  }

  async createInvoice(data: any) {
    const response = await this.client.post('/invoices', data);
    return normalize(response.data);
  }

  async getInvoices(params = '') {
    const response = await this.client.get(`/invoices${params}`);
    return normalize(response.data);
  }

  async transitionInvoice(id: string, to: string) {
    const response = await this.client.post(`/invoices/${id}/transition`, { to });
    return normalize(response.data);
  }

  async payInvoice(id: string, data: any) {
    const response = await this.client.post(`/invoices/${id}/payments`, data);
    return normalize(response.data);
  }

  async getGstSummary() {
    const response = await this.client.get('/gst/summary');
    return normalize(response.data);
  }

  async validateGstin(gstin: string) {
    const response = await this.client.post('/gst/validate', { gstin });
    return normalize(response.data);
  }

  async gstReconcile(books_tax: number, portal_tax: number) {
    const response = await this.client.post('/gst/reconcile', { books_tax, portal_tax });
    return normalize(response.data);
  }

  async computeTds(section: string, amount: number, pan_available = true) {
    const response = await this.client.post('/tds/compute', { section, amount, pan_available });
    return normalize(response.data);
  }

  async getTdsSections() {
    const response = await this.client.get('/tds/sections');
    return normalize(response.data);
  }

  async getTdsRecords() {
    const response = await this.client.get('/tds-records');
    return normalize(response.data);
  }

  async createTdsRecord(data: any) {
    const response = await this.client.post('/tds-records', data);
    return normalize(response.data);
  }

  async getTdsSummary() {
    const response = await this.client.get('/tds/summary');
    return normalize(response.data);
  }

  async computeGain(data: any) {
    const response = await this.client.post('/gains/compute', data);
    return normalize(response.data);
  }

  async getPlanning(regime = 'old') {
    const response = await this.client.get(`/planning/opportunities?regime=${regime}`);
    return normalize(response.data);
  }

  async getMonthEndClose() {
    const response = await this.client.get('/close/month-end');
    return normalize(response.data);
  }

  async getAnomalies() {
    const response = await this.client.get('/intel/anomalies');
    return normalize(response.data);
  }

  async forecastCash(data: any) {
    const response = await this.client.post('/intel/forecast', data);
    return normalize(response.data);
  }

  async getHealth(tax_period = '2024-25') {
    const response = await this.client.get(`/intel/health?tax_period=${tax_period}`);
    return normalize(response.data);
  }

  async getTaxOwed() {
    const response = await this.client.get('/assistant/tax-owed');
    return normalize(response.data);
  }

  async getAttention() {
    const response = await this.client.get('/assistant/attention');
    return normalize(response.data);
  }

  async getOverdueInvoices() {
    const response = await this.client.get('/assistant/overdue-invoices');
    return normalize(response.data);
  }

  async getClients() {
    const response = await this.client.get('/clients');
    return normalize(response.data);
  }

  async createClient(data: any) {
    const response = await this.client.post('/clients', data);
    return normalize(response.data);
  }

  async getTasks() {
    const response = await this.client.get('/tasks');
    return normalize(response.data);
  }

  async createTask(data: any) {
    const response = await this.client.post('/tasks', data);
    return normalize(response.data);
  }

  async updateTask(id: string, status: string) {
    const response = await this.client.patch(`/tasks/${id}`, { status });
    return normalize(response.data);
  }

  async getDocRequests() {
    const response = await this.client.get('/doc-requests');
    return normalize(response.data);
  }

  async createDocRequest(data: any) {
    const response = await this.client.post('/doc-requests', data);
    return normalize(response.data);
  }

  async getReviews() {
    const response = await this.client.get('/reviews');
    return normalize(response.data);
  }

  async transitionReview(id: string, to: string) {
    const response = await this.client.patch(`/reviews/${id}/transition`, { to });
    return normalize(response.data);
  }

  async getPracticeOverview() {
    const response = await this.client.get('/practice/overview');
    return normalize(response.data);
  }

  async getProducts() {
    const response = await this.client.get('/products');
    return normalize(response.data);
  }

  async createProduct(data: any) {
    const response = await this.client.post('/products', data);
    return normalize(response.data);
  }

  async getLowStock() {
    const response = await this.client.get('/inventory/low-stock');
    return normalize(response.data);
  }

  async createPosBill(cart: any[], extra: any = {}) {
    const response = await this.client.post('/pos/bill', { cart, ...extra });
    return normalize(response.data);
  }

  async getIntegrations() {
    const response = await this.client.get('/integrations/status');
    return normalize(response.data);
  }

  async getPlans() {
    const response = await this.client.get('/billing/plans');
    return normalize(response.data);
  }

  async getSubscription() {
    const response = await this.client.get('/billing/subscription');
    return normalize(response.data);
  }

  async getEntitlement() {
    const response = await this.client.get('/billing/entitlement');
    return normalize(response.data);
  }

  async getBillingHistory() {
    const response = await this.client.get('/billing/history');
    return normalize(response.data);
  }

  async checkout(plan: string, provider = 'manual') {
    const response = await this.client.post('/billing/checkout', { plan, provider });
    return normalize(response.data);
  }

  async cancelSubscription() {
    const response = await this.client.post('/billing/cancel', {});
    return normalize(response.data);
  }

  async startTrial(plan: string) {
    const response = await this.client.post('/billing/trial/start', { plan });
    return normalize(response.data);
  }

  async getSupportTickets() {
    const response = await this.client.get('/support');
    return normalize(response.data);
  }

  async createSupportTicket(data: any) {
    const response = await this.client.post('/support', data);
    return normalize(response.data);
  }

  async getSupportTicket(id: string) {
    const response = await this.client.get(`/support/${id}`);
    return normalize(response.data);
  }

  async replySupportTicket(id: string, body: string) {
    const response = await this.client.post(`/support/${id}/reply`, { body });
    return normalize(response.data);
  }

  async getNotifications(unreadOnly = false) {
    const response = await this.client.get(`/notifications${unreadOnly ? '?unread_only=true' : ''}`);
    return normalize(response.data);
  }

  async markNotification(id: string, read = true) {
    const response = await this.client.patch(`/notifications/${id}`, { read });
    return normalize(response.data);
  }

  async markAllNotificationsRead() {
    const response = await this.client.post('/notifications/read-all', {});
    return normalize(response.data);
  }

  async getAdminOverview() {
    const response = await this.client.get('/admin/overview');
    return normalize(response.data);
  }

  async getAdminUsers() {
    const response = await this.client.get('/admin/users?limit=50');
    return normalize(response.data);
  }

  async patchAdminUser(id: string, patch: any) {
    const response = await this.client.patch(`/admin/users/${id}`, patch);
    return normalize(response.data);
  }

  async getAdminSubscriptions() {
    const response = await this.client.get('/admin/subscriptions?limit=50');
    return normalize(response.data);
  }

  async getAdminSupport() {
    const response = await this.client.get('/admin/support?limit=50');
    return normalize(response.data);
  }

  async getAdminAudit() {
    const response = await this.client.get('/admin/audit?limit=100');
    return normalize(response.data);
  }

  async getAdminHealth() {
    const response = await this.client.get('/admin/health');
    return normalize(response.data);
  }

  async getAdminIncidents() {
    const response = await this.client.get('/admin/incidents');
    return normalize(response.data);
  }

  async createIncident(title: string) {
    const response = await this.client.post('/admin/incidents', { title, severity: 'medium' });
    return normalize(response.data);
  }

  async patchIncident(id: string, patch: any) {
    const response = await this.client.patch(`/admin/incidents/${id}`, patch);
    return normalize(response.data);
  }

  async activateRule(version: number) {
    const response = await this.client.post('/admin/rules/activate', { version });
    return normalize(response.data);
  }

  async changePassword(old_password: string, new_password: string) {
    const response = await this.client.post('/auth/password-change', { old_password, new_password });
    return normalize(response.data);
  }

  async requestPasswordReset(email: string) {
    const response = await this.client.post('/auth/password-reset/request', { email });
    return normalize(response.data);
  }

  async confirmPasswordReset(token: string, new_password: string) {
    const response = await this.client.post('/auth/password-reset/confirm', { token, new_password });
    return normalize(response.data);
  }

  async getSessions() {
    const response = await this.client.get('/auth/sessions');
    return normalize(response.data);
  }

  async logoutAll() {
    const response = await this.client.post('/auth/logout-all', {});
    return normalize(response.data);
  }

  async updateMe(patch: any) {
    const response = await this.client.patch('/me', patch);
    return normalize(response.data);
  }

  async getConsents() {
    const response = await this.client.get('/consents');
    return normalize(response.data);
  }

  async setConsent(purpose: string, granted: boolean) {
    const response = await this.client.post('/consents', { purpose, granted });
    return normalize(response.data);
  }

  async requestDeletion() {
    const response = await this.client.post('/account/deletion/request', {});
    return normalize(response.data);
  }

  async deletionStatus() {
    const response = await this.client.get('/account/deletion/status');
    return normalize(response.data);
  }

  async executeDeletion(confirm: string, skip_grace = false) {
    const response = await this.client.post('/account/deletion/execute', { confirm, skip_grace });
    return normalize(response.data);
  }

  exportUrl(kind: 'transactions' | 'invoices' | 'parties') {
    return `${API_URL}/exports/${kind}.csv`;
  }
}

export const api = new ApiClient();